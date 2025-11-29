import asyncio
import os
from dotenv import load_dotenv
from agent import run_agent

# Load environment variables
load_dotenv()

def main():
    # The starting URL for Project 2
    start_url = "https://tds-llm-analysis.s-anand.net/project2"
    
    print(f"Starting Project 2 automation with URL: {start_url}")
    
    # Run the agent
    try:
        # run_agent is synchronous in the provided agent.py (it uses app.invoke)
        run_agent(start_url)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
