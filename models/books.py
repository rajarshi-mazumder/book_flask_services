from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import JSON
from .sqlalchemy_setup import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Category {self.name}>'

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Author {self.name}>'

class BookCategory(db.Model):
    __tablename__ = 'book_category'
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cover_img_path = db.Column(db.String(250), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=True)
    author = db.relationship('Author', backref=db.backref('books', lazy=True))
    categories = db.relationship('Category', secondary='book_category', backref=db.backref('books', lazy=True))
    book_details = db.relationship('BookDetails', backref='book', uselist=False)
    details_hash = db.Column(db.String(64), nullable=True)
    
    def __repr__(self):
        return f'<Book {self.title}>'

class BookDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False, unique=True)
    book_chapters = db.Column(MutableList.as_mutable(JSON), nullable=False)

    def __repr__(self):
        return f'<BookDetails {self.book_id}>'
    
