import logging
from app.models import ReviewResult
from app.utils import timer
from google.genai import types

logger = logging.getLogger(__name__)

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

    @timer
    def review_chunk(self, chunk):
        prompt = f"""The following text contains code from one or more files in a Github repository. Review the files. For each issue, return its:
- Path
- Start line number
- End line number
- Category
- Severity
- Description
- Suggested improvement

{chunk}"""
        try:
            response = self.client.models.generate_content(
                model = "gemini-3.1-flash-lite",
                contents = prompt,
                config = types.GenerateContentConfig(
                    response_mime_type = "application/json",
                    response_schema = ReviewResult
                    )
                )
            return response
        except Exception as e:
            logger.exception(f"Gemini API request failed: {e}")
            print(f"Unable to review chunk - Gemini service experiencing unavailability: {e}")
            return None

    @timer
    def start_review(self):
        self.file_chunks = self.create_file_chunks()
        self.result = ReviewResult(issues = [])
        for chunk in self.file_chunks:
            response = self.review_chunk(chunk)
            if response is not None:
                self.result.issues.extend(response.parsed.issues)

    def get_issues(self): # For debugging
        all_issues = []
        for issue in self.result.issues:
            if issue.line_start == issue.line_end:
                lines_text = f"Line: {issue.line_start}"
            else:
                lines_text = f"Lines: {issue.line_start}-{issue.line_end}"
            all_issues.append(f"""Path: {issue.file_path}
{lines_text}

Category: {issue.category.value}
Severity: {issue.severity.value}

Description:
{issue.description}

Suggested Changes:
{issue.suggestion}

""")
        return all_issues

    @timer
    def summary(self): # Summary review of whole repo, using collection of issues.
        issues_text = """"""
        for issue in self.get_issues():
            issues_text += issue
        prompt = f"""Using the issues gathered for this GitHub repository, create a summary evaluation of the whole repository.

{issues_text}"""
        try:
            response = self.client.models.generate_content(
                model = "gemini-3.1-flash-lite",
                contents = prompt,
                )
            return response.text
        except Exception as e:
            logger.exception(f"Gemini API request failed: {e}")
            print(f"Unable to produce summary of repository - Gemini service experiencing unavailability: {e}")
            return None