from db import db
from datetime import date


class PostModel(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    is_visible = db.Column(db.Boolean, default=True)
    content = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(20), nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False, unique=False)
    author = db.relationship("AuthorModel", back_populates="posts")
