from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, email_validator
import sqlite3


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_email(self, email):
        conn = sqlite3.connect('database.db')
        curs = conn.cursor()
        curs.execute("SELECT email FROM users where email = (?)", [email.data])
        valemail = curs.fetchone()
        if valemail is None:
            raise ValidationError('This Email ID is not registered. Please register before login')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'M'), ('Female', 'F')])
    password1 = PasswordField('Password1', validators=[DataRequired()])
    submit = SubmitField('Register')
