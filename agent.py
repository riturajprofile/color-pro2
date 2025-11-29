from langgraph.graph import StateGraph, END, START
from langchain_core.rate_limiters import InMemoryRateLimiter
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import get_rendered_html, download_file, post_request, run_code, add_dependencies, transcribe_audio, analyze_image
from typing import TypedDict, Annotated, List, Any
from langchain.chat_models import init_chat_model
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv
from logger_config import get_logger, log_task_start, log_task_end

load_dotenv()

EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")
RECURSION_LIMIT =  5000

logger = get_logger("agent")

# -------------------------------------------------
# STATE
# -------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    task_counter: int  # Track task number


TOOLS = [run_code, get_rendered_html, download_file, post_request, add_dependencies, transcribe_audio, analyze_image]


# -------------------------------------------------
# GEMINI LLM
# -------------------------------------------------
rate_limiter = InMemoryRateLimiter(
    requests_per_second=9/60,  
    check_every_n_seconds=1,  
    max_bucket_size=9  
)
llm = init_chat_model(
   model_provider="google_genai",
   model="gemini-2.5-flash",
   rate_limiter=rate_limiter
).bind_tools(TOOLS)   


# -------------------------------------------------
# SYSTEM PROMPT
# -------------------------------------------------
SYSTEM_PROMPT = f"""
You are an autonomous quiz-solving agent.

Your job is to:
1. Load the quiz page from the given URL.
2. Extract ALL instructions, required parameters, submission rules, and the submit endpoint.
3. Solve the task exactly as required.
4. Submit the answer ONLY to the endpoint specified on the current page (never make up URLs).
5. Read the server response and:
   - If it contains a new quiz URL → fetch it immediately and continue.
   - If no new URL is present → return "END".

STRICT RULES — FOLLOW EXACTLY:

GENERAL RULES:
- NEVER stop early. Continue solving tasks until no new URL is provided.
- NEVER hallucinate URLs, endpoints, fields, values, or JSON structure.
- NEVER shorten or modify URLs. Always submit the full URL.
- NEVER re-submit unless the server explicitly allows or it's within the 3-minute limit.
- ALWAYS inspect the server response before deciding what to do next.
- ALWAYS use the tools provided to fetch, scrape, download, render HTML, or send requests.

FILE MANAGEMENT RULES:
- When you use download_file, files are saved to data/downloads/ directory.
- When you use transcribe_audio on a URL, audio files are saved to data/audio/ directory.
- In your Python code (run_code), ALWAYS use the already-downloaded files from data/downloads/ or data/audio/.
- NEVER re-download files in Python code using requests.get() or similar - use the local files.
- File paths in Python code: "data/downloads/filename.csv" or "data/audio/audio.m4a"
- Example: If you downloaded "demo.csv", use pd.read_csv("data/downloads/demo.csv") NOT requests.get(url)

TIME LIMIT RULES:
- Each task has a hard 3-minute limit.
- The server response includes a "delay" field indicating elapsed time.
- If your answer is wrong retry again.

STOPPING CONDITION:
- Only return "END" when a server response explicitly contains NO new URL.
- DO NOT return END under any other condition.

ADDITIONAL INFORMATION YOU MUST INCLUDE WHEN REQUIRED:
- Email: {EMAIL}
- Secret: {SECRET}

YOUR JOB:
- Follow pages exactly.
- Extract data reliably.
- Never guess.
- Submit correct answers.
- Continue until no new URL.
- Then respond with: END
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages")
])

llm_with_prompt = prompt | llm


# -------------------------------------------------
# AGENT NODE
# -------------------------------------------------
def agent_node(state: AgentState):
    # Check if this is a new URL (user message with URL)
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "type") and last_msg.type == "human":
        # Extract URL from message
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        if content.startswith("http"):
            task_num = state.get("task_counter", 0) + 1
            log_task_start(content, task_num)
            state["task_counter"] = task_num
    
    result = llm_with_prompt.invoke({"messages": state["messages"]})
    return {"messages": state["messages"] + [result]}


# -------------------------------------------------
# GRAPH
# -------------------------------------------------
def route(state):
    last = state["messages"][-1]
    # support both objects (with attributes) and plain dicts
    tool_calls = None
    if hasattr(last, "tool_calls"):
        tool_calls = getattr(last, "tool_calls", None)
    elif isinstance(last, dict):
        tool_calls = last.get("tool_calls")

    if tool_calls:
        return "tools"
    # get content robustly
    content = None
    if hasattr(last, "content"):
        content = getattr(last, "content", None)
    elif isinstance(last, dict):
        content = last.get("content")

    if isinstance(content, str) and content.strip() == "END":
        log_task_end(success=True, message="All tasks completed")
        return END
    if isinstance(content, list) and content[0].get("text").strip() == "END":
        log_task_end(success=True, message="All tasks completed")
        return END
    return "agent"

graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(TOOLS))



graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")
graph.add_conditional_edges(
    "agent",    
    route       
)

app = graph.compile()


# -------------------------------------------------
# TEST
# -------------------------------------------------
def run_agent(url: str) -> str:
    logger.info(f"Starting agent with initial URL: {url}")
    try:
        app.invoke({
            "messages": [{"role": "user", "content": url}],
            "task_counter": 0
        },
            config={"recursion_limit": RECURSION_LIMIT},
        )
        logger.info("Agent completed successfully")
        print("Tasks completed succesfully")
    except Exception as e:
        logger.error(f"Agent failed with error: {str(e)}", exc_info=True)
        log_task_end(success=False, message=f"Error: {str(e)}")
        raise
