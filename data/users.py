import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(128), unique=True)
    login = sqlalchemy.Column(sqlalchemy.String(128), nullable=False, unique=True)
    password = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)

    admin = orm.relation("Admin", back_populates='user')

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True
