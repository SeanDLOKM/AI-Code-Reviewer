import logging
import traceback
import json
import urllib3
import urllib.parse
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from base64 import b64decode
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

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

excluded_directories = (
    "node_modules",
    "__pycache__",
    ".git",
    "build",
    "dist")

http = urllib3.PoolManager()

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

class Severity(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Category(Enum):
    PERFORMANCE = "Performance"
    SECURITY = "Security"
    BUG = "Bug"
    ERROR_HANDLING = "Error Handling"
    READABILITY = "Readability"
    RELIABILITY = "Reliability"
    MAINTAINABILITY = "Maintainability"
    ARCHITECTURE_DESIGN = "Architecture/Design"
    TESTING = "Testing"
    OTHER = "Other"

class Issue(BaseModel):
    file_path: str = Field(description = "Path of file being reviewed, can be found before the beginning of \"Contents\" section.")
    line_start: int = Field(description = "First line number of code associated with the issue.")
    line_end: int = Field(description = "Final line number of code associated with the issue.")
    category: Category = Field(description = "Category that the issue most closely relates to.")
    severity: Severity = Field(description = "How impactful the issue is on the quality of the overall code. High severity issues have a significant negative impact on the quality/consistency of the code.")
    description: str = Field(description = "Description of the issue, how it negatively impacts the code, and why.")
    suggestion: str = Field(description = "Suggested changes to make to resolve the issue.")

class ReviewResult(BaseModel):
    issues: List[Issue]

class Review():
    def __init__(self, client, files):
        self.files = files
        self.client = client
        self.file_chunks = None
        self.result = None
         
    def create_file_chunks(self, max_chars = 50000):
        current_chunk = ""
        chunks = []
        for filepath, contents in self.files.items():
            if len(contents) == 0:
                continue
            file_text = f"""
File path: {filepath}

Contents:

{contents}
"""
            if current_chunk == "":
                current_chunk = file_text
                continue
            if len(current_chunk) + len(file_text) > max_chars:
                chunks.append(current_chunk)
                current_chunk = ""

            current_chunk += file_text
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    def start_review(self):
        self.file_chunks = self.create_file_chunks()
        self.result = ReviewResult(issues = [])
        for chunk in self.file_chunks:
            prompt = f"""The following text contains code from one or more files in a Github repository. Review the files. For each issue, return its:
- Path
- Start line number
- End line number
- Category
- Severity
- Description
- Suggested improvement

{chunk}"""
            response = self.client.models.generate_content(
                model = "gemini-3.1-flash-lite",
                contents = prompt,
                config = types.GenerateContentConfig(
                    response_mime_type = "application/json",
                    response_schema = ReviewResult
                    )
                )
            self.result.issues.extend(response.parsed.issues)

    def display_results(self):
        for issue in self.result.issues:
            if issue.line_start == issue.line_end:
                lines_text = f"Line: {issue.line_start}"
            else:
                lines_text = f"Lines: {issue.line_start}-{issue.line_end}"

            print(f"""Path: {issue.file_path}
{lines_text}

Category: {issue.category.value}
Severity: {issue.severity.value}

Description:
{issue.description}

Suggested Changes:
{issue.suggestion}

""")
       
def main():
    logging.basicConfig(filename = 'reviewer.log', level = logging.INFO)
    logger.info('Started')
    
    url = input("Enter a GitHub repo link: ")

    repo = GitRepo(url)

    client = genai.Client(
        api_key = gemini_token,
        http_options = types.HttpOptions(
            retry_options = types.HttpRetryOptions(
                initial_delay = 10.0,
                attempts = 5,
                max_delay = 60,
                http_status_codes = [408, 429, 500, 502, 503, 504]
                )
            )
        )

    if repo.load_repo():
        review = Review(client, repo.files)
        review.start_review()
        review.display_results()

    logger.info('Finished')

if __name__ == '__main__':
    main()