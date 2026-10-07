import traceback
import json
import urllib3
import urllib.parse
from base64 import b64decode
import os
from dotenv import load_dotenv
from app.utils import timer

load_dotenv()
git_token = os.getenv("GIT_TOKEN")
http = urllib3.PoolManager()

supported_files = (
    ".py",
    ".cpp",
    ".h",
    ".hpp",
    ".js",
    ".ts",
    ".java",
    ".cs")

class GitRepo():
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.repo_path = None
        self.repo_data = None
        self.name = None
        self.branch = None
        self.tree_sha = None
        self.tree = None
        self.files = {}

    def request_data(self, url):
        response = http.request(method = 'GET', url = url, headers = {"Authorization" : f"Bearer {git_token}"})
        if response.status == 200:
            data_raw = response.data
            data = json.loads(data_raw)
            return data
        else:
            print(f"GitHub API request for {url} failed. Status: {response.status}")
            return None

    def get_repo_path(self):
        try:
            if "github.com" in self.repo_url:
                parsed = urllib.parse.urlsplit(self.repo_url)
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

    def get_repo_data(self):
        api_url = f"https://api.github.com/repos{self.repo_path}"
        api_data = self.request_data(api_url)
        return api_data

    def get_tree_sha(self):
        branch_url = f"https://api.github.com/repos{self.repo_path}/branches/{self.branch}"
        branch_data = self.request_data(branch_url)
        sha = branch_data["commit"]["commit"]["tree"]["sha"]
        return sha

    def get_repo_tree(self):
        tree_url = f"https://api.github.com/repos{self.repo_path}/git/trees/{self.tree_sha}?recursive=true"
        tree_data = self.request_data(tree_url)
        return tree_data["tree"]

    def get_tree_file_contents(self):
        files = {}
        for item in self.tree:
            path = item["path"]
            item_type = item["type"]
            if item_type == "blob" and path.endswith(supported_files): # Filters out file extensions we never want to review.
                url = item["url"]
                data = self.request_data(url)
                contents = b64decode(data["content"]) # Git API encodes blob contents as base 64.
                files[path] = contents.decode("utf-8") # Convert from bytes type to string type for more readable format.
        return files

    @timer
    def load_repo(self):
        self.repo_path = self.get_repo_path()
        if self.repo_path is None:
            return False
        self.repo_data = self.get_repo_data()
        if self.repo_data is None:
            return False
        self.name = self.repo_data["name"]
        self.branch = self.repo_data["default_branch"]
        self.tree_sha = self.get_tree_sha()
        self.tree = self.get_repo_tree()
        self.files = self.get_tree_file_contents()
        return True