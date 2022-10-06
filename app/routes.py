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
from app.forms import SetActiveChildForm
from app.models import Child
from app.models import Family
from app.models import Feed
from app.models import User

from app.lib.metric_helpers import UserMetrics
from app.lib.route_helpers import RouteUser
from app.lib.route_helpers import return_current_date_string

from datetime import datetime

from werkzeug.urls import url_parse


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    active_user = RouteUser(current_user)
    active_child_metrics = UserMetrics(active_user.user_active_child)

    if active_user.user_children is not None:
        log_feed_form = LogFeedForm()

        # TODO: Replace static feed_type_list once user-level type management has been implemented
        feed_type_list = [
            ("breast", "Breast"),
            ("bottle", "Bottle"),
            ("breast_plus_bottle", "Breast Plus Bottle"),
        ]
        log_feed_form.feed_type.choices = feed_type_list

        if log_feed_form.validate_on_submit():
            feed = Feed(
                feed_type=log_feed_form.feed_type.data,
                child_id=active_user.user_active_child,
            )
            db.session.add(feed)
            db.session.commit()
            flash("Feed submitted!")
            return redirect(url_for("index"))
    else:
        log_feed_form = None

    return render_template(
        "index.html",
        title="Home",
        current_date_string=return_current_date_string(),
        log_feed_form=log_feed_form,
        user_children=active_user.user_children,
        user_active_child_name=active_user.user_active_child_name,
        feeds=active_child_metrics.current_day_feeds,
        most_recent_feed=active_child_metrics.most_recent_feed_display_time,
        time_since_last_feed=active_child_metrics.time_since_last_feed,
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


# TODO: The nested if statements in this route need to be broken up
@app.route("/user/<username>", methods=["GET", "POST"])
@login_required
def user(username):
    active_user = RouteUser(current_user)

    if active_user.user_family is not None:
        create_family_form = None

        add_child_form = AddChildForm()
        if add_child_form.validate_on_submit():
            child = Child(
                child_first_name=add_child_form.child_first_name.data,
                family_id=active_user.user_family.id,
            )
            db.session.add(child)
            db.session.commit()
            flash("Child added!")
            return redirect(url_for("user", username=current_user.username))
    else:
        add_child_form = None
        set_active_child_form = None
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

    if active_user.user_children is not None:
        set_active_child_form = SetActiveChildForm()

        set_active_child_form.selected_child.choices = (
            active_user.user_ordered_child_list
        )
        if set_active_child_form.validate_on_submit():
            db.session.query(User).filter(User.id == current_user.get_id()).update(
                {"active_child": set_active_child_form.selected_child.data}
            )
            db.session.commit()
            flash("Active child updated")
            return redirect(url_for("user", username=current_user.username))
    else:
        set_active_child_form = None

    return render_template(
        "user.html",
        user=current_user,
        user_family=active_user.user_family,
        user_children=active_user.user_ordered_child_list,
        create_family_form=create_family_form,
        add_child_form=add_child_form,
        set_active_child_form=set_active_child_form,
    )


@app.route("/feed_history/<child_id>")
@login_required
def feed_history(child_id):
    return render_template(
        "feed_history.html",
        user_active_child_name=Child.query.filter_by(id=child_id)
        .first()
        .child_first_name,
        selected_child_id=child_id,
    )


# TODO: Move the feed history functions into lib?
@app.route("/api/feed_history_data/<selected_child_id>")
def feed_history_data(selected_child_id):
    def feed_data_to_dict(feed):
        return {
            "id": feed.id,
            "child_first_name": feed.child.child_first_name,
            "feed_type": feed.feed_type,
            "feed_timestamp": feed.feed_timestamp,
        }

    if selected_child_id is not None:
        active_child_feeds = (
            db.session.query(Feed)
            .join(Child, Child.id == Feed.child_id)
            .filter(Feed.child_id == selected_child_id)
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


@app.route("/api/feed_history_data/<selected_child_id>", methods=["POST"])
def feed_history_update(selected_child_id):
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
