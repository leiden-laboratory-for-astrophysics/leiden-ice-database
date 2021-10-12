from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, TextAreaField, SubmitField

class ContactForm(FlaskForm):
    name = TextField("Name")
    email = TextField("Email")
    institution = TextField("Institution")
    message = TextAreaField("Message")
    submit = SubmitField("Send")

