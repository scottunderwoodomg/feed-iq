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

"""
Generalized functions for use across the various routes defined in routes.py 
"""

# TODO: Potentially convert these into a user-related class to simply the importing and use in routes.py?


def return_user_family():
    return Family.query.filter_by(user_id=current_user.get_id()).first()


def return_user_children(user_family):
    return (
        None
        if user_family is None
        else Child.query.filter_by(family_id=user_family.id).all()
    )


def return_user_active_child():
    return User.query.filter_by(id=current_user.get_id()).first().active_child


def return_user_active_child_name(user_active_child):
    return (
        None
        if user_active_child is None
        else Child.query.filter_by(id=user_active_child).first().child_first_name
    )
