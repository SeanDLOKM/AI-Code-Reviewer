import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.git_repo import GitRepo
from app.review import Review

logger = logging.getLogger(__name__)
# Load .env into environment
load_dotenv()
gemini_token = os.getenv("GEMINI_API_KEY")
       
def main():
    logging.basicConfig(filename = 'reviewer.log', filemode = "w", level = logging.INFO)
    logger.info('Started')
    
    url = input("Enter a GitHub repo link: ")

    repo = GitRepo(url)

    client = genai.Client(
        api_key = gemini_token,
        http_options = types.HttpOptions(
            retry_options = types.HttpRetryOptions(
                initial_delay = 4.0,
                attempts = 5,
                max_delay = 60,
                http_status_codes = [408, 429, 500, 502, 503, 504]
                )
            )
        )

    if repo.load_repo(): # Loads git repo, before starting a review of it.
        review = Review(client, repo.files)
        review.start_review()
        for issue in review.get_issues():
            print(issue)
        summary = review.summary()
        if summary is not None:
            print(summary)

    logger.info('Finished')

if __name__ == '__main__':
    main()