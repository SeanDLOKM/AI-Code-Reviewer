import traceback
import json
import urllib3
import urllib.parse
import os
from dotenv import load_dotenv

# Load .env into environment
load_dotenv()
git_token = os.getenv("GIT_TOKEN")

supported_files = (
    ".py",
    ".cpp",
    ".h",
    ".hpp",
    ".js",
    ".ts",
    ".java",
    ".cs")

def request_from_git_api(url):
    response = http.request(method = 'GET', url = url, headers = {"Authorization" : f"Bearer {git_token}"})
    if response.status == 200:
        return response
    else:
        print(f"GitHub API request for {url} failed. Status: {response.status}")
        return None

def get_repo_path(repo_url):
    try:
        if "github.com" in repo_url:
            parsed = urllib.parse.urlsplit(repo_url)
            path = parsed.path
            path = path.removesuffix("/")
            path = path.removesuffix(".git")
            return path
        else:
            print("Invalid URL - please enter a GitHub repository URL.")
            return None
    except Exception:
        traceback.print_exc()
        return None

def get_default_branch(repo_path):
    api_url = f"https://api.github.com/repos{repo_path}"
    api_response = request_from_git_api(api_url)
    if api_response is not None:
        data_raw = api_response.data
        data = json.loads(data_raw)
        branch = data["default_branch"]
        return branch

def get_tree_sha(repo_path, branch):
    branch_url = f"https://api.github.com/repos{repo_path}/branches/{branch}"
    branch_response = request_from_git_api(branch_url)
    if branch_response is not None:
        data_raw = branch_response.data
        data = json.loads(data_raw)
        sha = data["commit"]["commit"]["tree"]["sha"]
        return sha

def get_repo_tree(repo_path, branch, sha):
    tree_url = f"https://api.github.com/repos{repo_path}/git/trees/{sha}?recursive=true"
    tree_response = request_from_git_api(tree_url)
    if tree_response is not None:
        data_raw = tree_response.data
        data = json.loads(data_raw)
        return data

http = urllib3.PoolManager()

url = input("Enter a GitHub repo link: ")

path = get_repo_path(url)
branch = get_default_branch(path)
sha = get_tree_sha(path, branch)

tree = get_repo_tree(path, branch, sha)

for item in tree["tree"]:
    print(item["path"], item["type"], "\n")