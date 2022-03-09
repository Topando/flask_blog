import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Article(SqlAlchemyBase):
    __tablename__ = 'articles'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String(50), nullable=True)
    intro = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("types.id"), nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    type_rel = orm.relation('Type')

