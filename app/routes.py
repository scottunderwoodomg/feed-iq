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
from app.forms import CreateFamilyForm
from app.forms import AddChildForm
from app.forms import LogFeedForm
from app.models import Child
from app.models import Family
from app.models import Feed
from app.models import User

from datetime import datetime

from werkzeug.urls import url_parse


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    # user = {"username": "Scott"} <- Can remove this stand in
    user_children = Child.query.filter_by(
        family_id=Family.query.filter_by(user_id=current_user.get_id()).first().id
    ).all()

    if user_children is not None:
        log_feed_form = LogFeedForm()
        log_feed_form.selected_child.choices = [
            (c.id, c.child_first_name) for c in user_children
        ]
        if log_feed_form.validate_on_submit():
            feed = Feed(
                feed_type=log_feed_form.feed_type.data,
                child_id=log_feed_form.selected_child.data,
            )
            db.session.add(feed)
            db.session.commit()
            flash("Feed submitted!")
            return redirect(url_for("index"))

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
    return render_template(
        "index.html",
        title="Home",
        feeds=feeds,
        user_children=user_children,
        log_feed_form=log_feed_form,
    )


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


@app.route("/user/<username>", methods=["GET", "POST"])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_family = Family.query.filter_by(user_id=current_user.get_id()).first()

    if user_family is not None:
        create_family_form = None
        user_children = [
            {"child_id": c.id, "child_name": c.child_first_name}
            for c in Child.query.filter_by(family_id=user_family.id)
        ]
        add_child_form = AddChildForm()
        if add_child_form.validate_on_submit():
            user_family_id = user_family.id
            child = Child(
                child_first_name=add_child_form.child_first_name.data,
                family_id=user_family_id,
            )
            db.session.add(child)
            db.session.commit()
            flash("Child added!")
            return redirect(url_for("user", username=current_user.username))
    else:
        add_child_form = None
        user_children = None
        create_family_form = CreateFamilyForm()
        if create_family_form.validate_on_submit():
            current_user_id = current_user.get_id()
            family = Family(
                family_name=create_family_form.family_name.data, user_id=current_user_id
            )
            db.session.add(family)
            db.session.commit()
            flash("Family created!")
            return redirect(url_for("user", username=current_user.username))

    return render_template(
        "user.html",
        user=user,
        user_family=user_family,
        user_children=user_children,
        create_family_form=create_family_form,
        add_child_form=add_child_form,
    )
