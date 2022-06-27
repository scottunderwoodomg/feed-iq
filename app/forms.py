from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import BooleanField

from wtforms import SubmitField
from wtforms.validators import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from app.models import User
from app.models import Family
from app.models import Child
from flask_login import current_user


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class CreateFamilyForm(FlaskForm):
    family_name = StringField("Add a new family", validators=[DataRequired()])
    submit = SubmitField("Create")


class AddChildForm(FlaskForm):
    child_first_name = StringField(
        "Add a child to your family", validators=[DataRequired()]
    )
    submit = SubmitField("Create")

    # TODO: Need to add protection against adding same child with name case changes
    def validate_child_first_name(self, child_first_name):
        existing_child = Child.query.filter_by(
            child_first_name=child_first_name.data,
            family_id=Family.query.filter_by(user_id=current_user.get_id()).first().id,
        ).first()
        if existing_child is not None:
            raise ValidationError(
                "A child with this name has already been added to your family."
            )
