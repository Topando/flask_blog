from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email

class ProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    about = TextAreaField("About", validators=[DataRequired()])
    rewards = TextAreaField("Rewards", validators=[DataRequired()])
    submit = SubmitField("Submit")