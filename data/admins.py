import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Admin(SqlAlchemyBase):
    __tablename__ = 'admins'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    email = sqlalchemy.Column(sqlalchemy.String(50), nullable=False)
    user = orm.relation('User')
    def __repr__(self):
        return "<Admin %r" % self.id
