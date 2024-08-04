from flask_sqlalchemy import SQLAlchemy

from .sqlalchemy_setup import db
from datetime import datetime

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    collection_img_path = db.Column(db.String(250), nullable=True)
    description= db.Column(db.String(250), nullable= True)
    categories = db.relationship('Category', secondary='collection_categories', backref='collections')

class CollectionCategories(db.Model):
    __tablename__ = 'collection_categories'
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)