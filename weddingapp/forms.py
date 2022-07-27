from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class ContactForm(FlaskForm):
    fullname= StringField(validators=[DataRequired(), Length(min=5)])
    email= StringField(validators=[Email()])
    message= TextAreaField()
    submit= SubmitField("Submit")


class Signup(FlaskForm):
    fname= StringField(validators=[DataRequired()])
    lname= StringField(validators=[DataRequired()])
    email= StringField(validators=[DataRequired(), Email(message="Email not valid")])
    pswd= PasswordField()
    cpswd= PasswordField(validators=[EqualTo('pswd', message="Password does not match")])
    submit= SubmitField("Signup")