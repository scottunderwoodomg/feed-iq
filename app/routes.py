from flask import abort
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

    if user_active_child is not None:
        user_active_child_name = (
            Child.query.filter_by(id=user_active_child).first().child_first_name
        )
    else:
        user_active_child_name = None

    if user_children is not None:
        log_feed_form = LogFeedForm()
        # TODO: Turn the list reorder into a general lib function
        user_children_list = [(c.id, c.child_first_name) for c in user_children]
        for c in user_children_list:
            if c[0] == user_active_child:
                user_children_list.insert(0, user_children_list.pop())

        log_feed_form.selected_child.choices = user_children_list
        if log_feed_form.validate_on_submit():
            feed = Feed(
                feed_type=log_feed_form.feed_type.data,
                child_id=log_feed_form.selected_child.data,
            )
            db.session.add(feed)
            db.session.query(User).filter(User.id == current_user.get_id()).update(
                {"active_child": log_feed_form.selected_child.data}
            )
            db.session.commit()
            flash("Feed submitted!")
            return redirect(url_for("index"))
    else:
        log_feed_form = None

    feeds = Feed.query.filter_by(child_id=user_active_child).all()

    return render_template(
        "index.html",
        title="Home",
        feeds=feeds,
        user_children=user_children,
        user_active_child_name=user_active_child_name,
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


# @app.route("/feed_history", methods=["GET", "POST"])
# TODO: Update this route so that the relevent child_id is fed in by dynamically
#   populated hyperlinks next to each child in a family on the user profile page
@app.route("/feed_history")
@login_required
def feed_history():
    return render_template(
        "feed_history.html",
        user_active_child_name=Child.query.filter_by(
            id=User.query.filter_by(id=current_user.get_id()).first().active_child
        )
        .first()
        .child_first_name,
    )


@app.route("/api/feed_history_data")
def feed_history_data():
    def feed_data_to_dict(feed):
        return {
            "id": feed.id,
            "child_first_name": feed.child.child_first_name,
            "feed_type": feed.feed_type,
            "feed_timestamp": feed.feed_timestamp,
        }

    user_active_child = (
        User.query.filter_by(id=current_user.get_id()).first().active_child
    )

    if user_active_child is not None:
        active_child_feeds = (
            db.session.query(Feed)
            .join(Child, Child.id == Feed.child_id)
            .filter(Feed.child_id == user_active_child)
        )
    else:
        active_child_feeds = None

    # search filter
    search = request.args.get("search")
    if search:
        active_child_feeds = active_child_feeds.filter(
            db.or_(
                Feed.feed_type.like(f"%{search}%"),
                Feed.feed_timestamp.like(f"%{search}%"),
            )
        )
    total = active_child_feeds.count()

    # sorting
    sort = request.args.get("sort")
    if sort:
        order = []
        for s in sort.split(","):
            direction = s[0]
            ts = s[1:]
            if ts not in ["feed_timestamp"]:
                ts = "feed_timestamp"
            col = getattr(Feed, ts)
            if direction == "-":
                col = col.desc()
            order.append(col)
        if order:
            active_child_feeds = active_child_feeds.order_by(*order)

    # pagination
    start = request.args.get("start", type=int, default=-1)
    length = request.args.get("length", type=int, default=-1)
    if start != -1 and length != -1:
        active_child_feeds = active_child_feeds.offset(start).limit(length)

    # response
    return {
        "data": [feed_data_to_dict(feed) for feed in active_child_feeds],
        "total": total,
    }


@app.route("/api/feed_history_data", methods=["POST"])
def update():
    data = request.get_json()
    if "id" not in data:
        abort(400)
    feed = Feed.query.get(data["id"])
    for field in ["feed_type", "feed_timestamp"]:
        if field in data:
            setattr(
                feed, field, datetime.strptime(data[field], "%a, %d %b %Y %H:%M:%S GMT")
            )
    db.session.commit()
    return "", 204
