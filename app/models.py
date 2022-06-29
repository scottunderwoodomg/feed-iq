from datetime import datetime
from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    active_child = db.Column(db.Integer, db.ForeignKey("child.id"))
    # local_time_zone to be added later
    family = db.relationship("Family", backref="user", lazy="dynamic")

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family_name = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    children = db.relationship("Child", backref="family", lazy="dynamic")

    def __repr__(self):
        return "<Family {}>".format(self.family_name)


class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_first_name = db.Column(db.String(120))
    # TODO add in child last name?
    family_id = db.Column(
        db.Integer, db.ForeignKey("family.id")
    )  # TODO: need to make this support multiple parents
    feeds = db.relationship("Feed", backref="child", lazy="dynamic")

    def __repr__(self):
        return "<Child {}>".format(self.child_first_name)


# TODO: Potentially rename the feed model to something else?
class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feed_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    feed_type = db.Column(db.String(120))
    child_id = db.Column(db.Integer, db.ForeignKey("child.id"))

    def __repr__(self):
        return "<Feed {}>".format(self.feed_timestamp)
