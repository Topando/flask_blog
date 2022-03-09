from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


class PostsForm(FlaskForm):
    types = SelectField("Types", choices=["Все записи"])
    filters = SelectField("Filter", choices=["По дате (убываение)", "По дате (возврастание)"])
    submit = SubmitField("Поиск")
