import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Type(SqlAlchemyBase):
    __tablename__ = 'types'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(128), nullable=True)
    article = orm.relation("Article", back_populates='type_rel')
