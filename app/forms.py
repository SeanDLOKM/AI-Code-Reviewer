from flask_wtf import FlaskForm
from wtforms import URLField, SubmitField

class GitRepoForm(FlaskForm):
    repo_url = URLField("GitHub Public Repository URL")
    submit = SubmitField("Generate Review")