from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
from app import app
from app.forms import LoginForm
from datetime import datetime


@app.route("/")
@app.route("/index")
def index():
    user = {"username": "Scott"}
    feeds = [
        {
            "child": "Charlie",
            "feed_datetime": datetime(2022, 5, 29, 11, 46, 42),
            "feed_type": "Breast",
        },
        {
            "child": "Charlie",
            "feed_datetime": datetime(2022, 5, 29, 8, 35, 41),
            "feed_type": "Breast",
        },
    ]
    return render_template("index.html", title="Home", user=user, feeds=feeds)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            "Login requested for user {}, remember_me={}".format(
                form.username.data, form.remember_me.data
            )
        )
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)
