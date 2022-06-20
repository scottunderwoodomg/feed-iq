from flask import render_template
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user

from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm
from app.models import User

from datetime import datetime

from werkzeug.urls import url_parse


@app.route("/")
@app.route("/index")
@login_required
def index():
    # user = {"username": "Scott"} <- Can remove this stand in
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
    return render_template("index.html", title="Home", feeds=feeds)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Thanks for registering!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
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
    return render_template("user.html", user=user, feeds=feeds)
