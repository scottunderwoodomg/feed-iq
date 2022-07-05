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
from app.forms import SelectActiveChildForm
from app.models import Child
from app.models import Family
from app.models import Feed
from app.models import User

# from datetime import datetime

from werkzeug.urls import url_parse


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    # TODO: Clean up this code, potentially generalize and import since
    #   the checks may be used elsewhere too
    user_family = Family.query.filter_by(user_id=current_user.get_id()).first()

    if user_family is not None:
        user_children = Child.query.filter_by(family_id=user_family.id).all()
    else:
        user_children = None

    # TODO: explore converting this into a global variable
    user_active_child = (
        User.query.filter_by(id=current_user.get_id()).first().active_child
    )
    print(user_active_child)

    if user_children is not None:
        select_active_child_form = SelectActiveChildForm()

        # TODO: Turn the list reorder into a general lib function
        user_children_list = [(c.id, c.child_first_name) for c in user_children]
        for c in user_children_list:
            if c[0] == user_active_child:
                user_children_list.insert(0, user_children_list.pop())

        select_active_child_form.selected_child.choices = user_children_list
        print(select_active_child_form.selected_child.choices)
        if select_active_child_form.validate_on_submit():
            db.session.query(User).filter(User.id == current_user.get_id()).update(
                {"active_child": select_active_child_form.selected_child.data}
            )
            db.session.commit()
            flash("Active child updated")
            return redirect(url_for("index"))

        log_feed_form = LogFeedForm()
        if log_feed_form.validate_on_submit():
            feed = Feed(
                feed_type=log_feed_form.feed_type.data,
                child_id=user_active_child,
            )
            db.session.add(feed)
            db.session.commit()
            flash("Feed submitted!")
            return redirect(url_for("index"))
    else:
        log_feed_form = None
        select_active_child_form = None

    feeds = Feed.query.filter_by(child_id=user_active_child).all()

    return render_template(
        "index.html",
        title="Home",
        feeds=feeds,
        user_children=user_children,
        user_active_child_name=Child.query.filter_by(id=user_active_child)
        .first()
        .child_first_name,
        log_feed_form=log_feed_form,
        select_active_child_form=select_active_child_form,
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
