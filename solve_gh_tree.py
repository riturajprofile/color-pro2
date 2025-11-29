import requests
import os

def solve():
    owner = "sanand0"
    repo = "tools-in-data-science-public"
    sha = "95224924d73f70bf162288742a555fe6d136af2d"
    path_prefix = "project-1/"
    extension = ".md"
    email = "23f2004390@ds.study.iitm.ac.in"

    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{sha}?recursive=1"
    print(f"Fetching: {url}")
    
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    
    count = 0
    for item in data.get("tree", []):
        path = item.get("path", "")
        if path.startswith(path_prefix) and path.endswith(extension):
            count += 1
            # print(f"Found: {path}")
            
    print(f"Count: {count}")
    
    offset = len(email) % 2
    print(f"Email length: {len(email)}")
    print(f"Offset: {offset}")
    
    final_answer = count + offset
    print(f"Final Answer: {final_answer}")

if __name__ == "__main__":
    solve()
