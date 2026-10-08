from pydantic import BaseModel, Field
from enum import Enum

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
    severity: Severity = Field(description = "How impactful the issue is on the quality of the overall code. Issues should be labelled high severity only if they should be urgently fixed.")
    description: str = Field(description = "Description of the issue, how it negatively impacts the code, and why.")
    suggestion: str = Field(description = "Suggested changes to make to resolve the issue.")

class ReviewResult(BaseModel):
    issues: list[Issue]