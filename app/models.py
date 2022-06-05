from datetime import datetime
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # local_time_zone to be added later
    parent = db.relationship("Parent", backref="user", lazy="dynamic")

    def __repr__(self):
        return "<User {}>".format(self.username)


class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_first_name = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    children = db.relationship("Child", backref="parent", lazy="dynamic")
    # children list?

    def __repr__(self):
        return "<Parent {}>".format(self.parent_first_name)


class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_first_name = db.Column(db.String(120))
    # TODO add in child last name?
    parent_id = db.Column(
        db.Integer, db.ForeignKey("parent.id")
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
