import sqlalchemy

from .db_session import SqlAlchemyBase


class Profile(SqlAlchemyBase):
    __tablename__ = 'profile'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String(200), nullable=True)
    rewards = sqlalchemy.Column(sqlalchemy.String(200), nullable=True)
