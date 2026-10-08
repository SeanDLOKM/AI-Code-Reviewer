from flask import Flask
from config import Config
from google import genai
from google.genai import types
import os

app = Flask(__name__)
app.config.from_object(Config)

client = genai.Client(
    api_key = app.config["GEMINI_API_KEY"],
    http_options = types.HttpOptions(
        retry_options = types.HttpRetryOptions(
            initial_delay = 4.0,
            attempts = 5,
            max_delay = 60,
            http_status_codes = [408, 429, 500, 502, 503, 504]
            )
        )
    )

from app import routes