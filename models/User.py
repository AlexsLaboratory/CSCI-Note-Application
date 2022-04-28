import bcrypt
from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, LoginManager
from sqlalchemy import Column, Integer, String, ForeignKey, MetaData, func
from sqlalchemy.orm import declarative_base, relationship

login = LoginManager()
db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = Column(db.Integer, primary_key=True)
    email = Column(db.String, unique=True)
    password = Column(db.String(128))
    first_name = Column(db.String)
    last_name = Column(db.String)
    notes = relationship("Note")

    def __init__(self, email, first_name, last_name, password):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.set_password(password)

    def set_password(self, password):
        salt = bcrypt.gensalt(12)
        self.password = bcrypt.hashpw(password.encode('utf8'), salt).decode()

    def check_password(self, candidate):
        return bcrypt.checkpw(candidate.encode("utf8"), self.password.encode("utf8"))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Note(db.Model):
    __tablename__ = "note"
    id = Column(db.Integer, primary_key=True)
    title = Column(db.String)
    body = Column(db.String)
    user_id = Column(db.Integer, ForeignKey("user.id"))
    time_created = Column(db.DateTime(), server_default=func.now())
    time_updated = Column(db.DateTime(), onupdate=func.now())
    user = relationship("User", back_populates="notes")

    def __init__(self, title, body, user_id):
        self.title = title
        self.body = body
        self.user_id = user_id
