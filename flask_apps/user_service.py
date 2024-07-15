from flask import Flask, request, jsonify, Blueprint, make_response
from config import Config
from models.books import  Book, Author, Category
from models.sqlalchemy_setup import db
from models.users import User
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import JWTManager, create_access_token
from .auth_service import auth_required, create_user_object

user_service= Blueprint("users", __name__)

@user_service.route("/users", methods=["GET"])
@auth_required
def get_all_users(current_user):
    users= User.query.all()
    output_users=[]

    for user in users:
        user_data={}
        user_data["id"]= user.id
        user_data["name"]= user.name
        user_data["email"]= user.email
        user_data["password"]= user.password
        output_users.append(user_data)
    
    return jsonify({"users": output_users})

@user_service.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user= User.query.filter_by(id=user_id ).first()
    
    if not user:
        return jsonify({'message': "No user found"})
    
    user_data={}
    user_data["id"]= user.id
    user_data["name"]= user.name
    user_data["email"]= user.email
    user_data["password"]= user.password
    
    return jsonify({'user': user_data})





@user_service.route("/users", methods=["POST"])
def create_user():
    data= request.get_json()
    name=data["name"]
    email= data["email"]
    password= data["password"]
    create_user_object(name, email, password)
    
    

@user_service.route("/users/<int:user_id>/books_started", methods=["POST"])
def add_user_books_started(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message': "No user found"})    
    
    data = request.get_json()
    books_started_ids = data.get("books_started", [])

    try:
        for book_id in books_started_ids:
            book = Book.query.get(book_id)
            if book and book not in user.books_started:
                user.books_started.append(book)
        
        db.session.commit()
        return jsonify({'message': f'User {user.name} books started updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    


@user_service.route("/users/<user_id>", methods=["PUT"])
def update_users():
    pass


