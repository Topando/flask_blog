from flask_wtf import FlaskForm
from wtforms import SubmitField,  PasswordField
from wtforms.validators import DataRequired


class GetAdminForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
