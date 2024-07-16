from flask_sqlalchemy import SQLAlchemy

from .sqlalchemy_setup import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    books_read = db.relationship('Book', secondary='user_books_read', backref='users_read')
    books_started = db.relationship('Book', secondary='user_books_started', backref='users_started')
    interested_categories = db.relationship('Category', secondary='user_interested_categories', backref='interested_users')

    def __repr__(self):
        return f'<User {self.name}>'

    
class UserBooksRead(db.Model):
    __tablename__ = 'user_books_read'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow) 

class UserBooksStarted(db.Model):
    __tablename__ = 'user_books_started'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow) 

class UserInterestedCategories(db.Model):
    __tablename__ = 'user_interested_categories'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow) 
