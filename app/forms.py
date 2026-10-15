from flask_wtf import FlaskForm
from wtforms import URLField, SubmitField

class GitRepoForm(FlaskForm):
    repo_url = URLField(render_kw = {"placeholder": "https://github.com/username/repository", "class": "url-field"})
    submit = SubmitField(render_kw = {"class": "submit-button"})