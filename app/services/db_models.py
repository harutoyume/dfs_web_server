# Impord downloaded modules
from sqlalchemy import ForeignKey, Integer, String
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin

# Import project files 
from .db_service import SqlAlchemyBase

class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)

    files = relationship("File", back_populates='user')

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class File(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'files'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String, nullable=True)
    filesize: Mapped[int] = mapped_column(Integer, nullable=True)
    fileUUID: Mapped[str] = mapped_column(String, nullable=True)
    filehash: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    user = relationship('User')
