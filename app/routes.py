from flask import request, render_template, redirect, url_for, flash
from app import app, client
from app.review import Review
from app.git_repo import GitRepo
from app.forms import GitRepoForm

@app.route('/', methods = ["GET", "POST"])
def home():
    form = GitRepoForm()

    if form.validate_on_submit():
        repo = GitRepo(form.repo_url.data)
        if repo.load_repo():
            flash("Successfully loaded repo.")
            review = Review(client, repo.files)
            review.start_review()
            issues = review.result.issues
            summary = review.summary()
            if summary is not None:
                return render_template("review_results.html", issues = issues, summary = summary)
        else:
            flash("Failed to load repo.")

    return render_template("home.html", form = form)