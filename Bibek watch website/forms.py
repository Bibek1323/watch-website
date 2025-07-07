from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length,EqualTo
from .extensions import db, login_manager

class SignupForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")

class UpdateAddressForm(FlaskForm):
    address = StringField("Address", validators=[DataRequired()])
    pincode = StringField("Pincode", validators=[DataRequired(), Length(min=4, max=10)])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField("Update Address")

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("Change Password")

class AddressForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    phone = StringField("Phone Number", validators=[DataRequired()])
    address = TextAreaField("Full Address", validators=[DataRequired()])
    pincode = StringField("Pincode", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])
    submit = SubmitField("Save Address")