from flask_security.forms import Required
from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NoneOf


class CreateArticleForm(FlaskForm):
    name = StringField("Title", validators=[DataRequired()])
    intro = StringField("Intro", validators=[DataRequired()])
    text = TextAreaField("Text", validators=[DataRequired()])
    types = SelectField("Types", choices=[], validators=[Required()])
    new_type = StringField("New_type")
    submit = SubmitField("Submit")
