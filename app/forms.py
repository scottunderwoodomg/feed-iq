from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import BooleanField

from wtforms import SelectField
from wtforms import SubmitField
from wtforms.validators import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from app.models import User
from app.models import Family
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
    # TODO: Form should only show up if a user does not already have a family
    family_name = StringField("Add a new family", validators=[DataRequired()])
    submit = SubmitField("Create")

    # TODO: Can probably remove this, may also enforce one family per user at a db level?
    def validate_family_name(self, family_name):
        existing_family = Family.query.filter_by(
            family_name=family_name.data, user_id=current_user.get_id()
        ).first()
        if existing_family is not None:
            raise ValidationError(
                "A family with this name already exists on your account."
            )


class SelectFamilyForm(FlaskForm):
    selected_family = SelectField("Select active family", coerce=int)
    submit = SubmitField("Select")
