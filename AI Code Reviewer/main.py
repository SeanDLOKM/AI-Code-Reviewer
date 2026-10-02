import traceback
import json
import urllib3
import urllib.parse
import os
from google import genai
from base64 import b64decode
from dotenv import load_dotenv

# Load .env into environment
load_dotenv()
git_token = os.getenv("GIT_TOKEN")
gemini_token = os.getenv("GEMINI_API_KEY")

supported_files = (
    ".py",
    ".cpp",
    ".h",
    ".hpp",
    ".js",
    ".ts",
    ".java",
    ".cs")

def request_data_from_git_url(url):
    response = http.request(method = 'GET', url = url, headers = {"Authorization" : f"Bearer {git_token}"})
    if response.status == 200:
        data_raw = response.data
        data = json.loads(data_raw)
        return data
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
    api_data = request_data_from_git_url(api_url)
    branch = api_data["default_branch"]
    return branch

def get_tree_sha(repo_path, branch):
    branch_url = f"https://api.github.com/repos{repo_path}/branches/{branch}"
    branch_data = request_data_from_git_url(branch_url)
    sha = branch_data["commit"]["commit"]["tree"]["sha"]
    return sha

def get_repo_tree(repo_path, branch, sha):
    tree_url = f"https://api.github.com/repos{repo_path}/git/trees/{sha}?recursive=true"
    tree_data = request_data_from_git_url(tree_url)
    return tree_data["tree"]

def get_tree_file_contents(tree):
    files = {}
    for item in tree:
        path = item["path"]
        item_type = item["type"]
        if item_type == "blob" and path.endswith(supported_files):
            url = item["url"]
            data = request_data_from_git_url(url)
            contents = b64decode(data["content"]) # Git API encodes blob contents as base 64.
            files[path] = contents.decode("utf-8") # Convert from bytes type to string type for more readable format.
    return files

http = urllib3.PoolManager()
url = input("Enter a GitHub repo link: ")
path = get_repo_path(url)
branch = get_default_branch(path)
sha = get_tree_sha(path, branch)
tree = get_repo_tree(path, branch, sha)
files = get_tree_file_contents(tree)

for filename, contents in files.items():
    print(filename, contents, "\n\n", sep = "\n")

### Testing LLM integration.
testpath = "app/converter.py"
prompt = f"""You are reviewing a Python source file.

File path: {testpath}

File contents:
{files[testpath]}"""

client = genai.Client(api_key = gemini_token)
response = client.models.generate_content(model = "gemini-3.1-flash-lite", contents = prompt)
print(response.text)