import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Book(SqlAlchemyBase):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    download_link = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    reading_time = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cover_image = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)
