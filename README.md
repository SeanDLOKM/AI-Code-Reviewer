# AI Code Reviewer

I wanted to practice implementing APIs and LLMs into my work, while creating a practical application. 
This Python Flask application communicates with the GitHub API to access an input public repository link and retreive relevant files
in an efficient manner. It then uses Google Gemini's free version of an LLM API to provide a summary of potential issues with the project,
referring to the file path as well as the line number(s) where applicable.

The goal of this was primarily to get more comfortable implementing REST APIs into project work, as well as general software development, however
it improved my familiarity with GitHub and the structure of repositories. Additionally, I learned how to implement LLMs into my work, and the
importance of efficiency as the quantity of API requests that can be made over a given time are limited.

### Directions for use

If you are interested in using this application, you'll need to make a virtual environment and generate your own access keys such as for GitHub, and Gemini.
