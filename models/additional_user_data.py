from flask_sqlalchemy import SQLAlchemy

from .sqlalchemy_setup import db
from datetime import datetime

class AdditionalAppData(db.Model):
    __tablename__ = 'additional_app_data'
    id = db.Column(db.Integer, primary_key=True, default=1)
    last_books_list_version= db.Column(db.String(20))

    def __repr__(self):
        return f'<AdditionalAppData {self.last_books_list_version}>'
