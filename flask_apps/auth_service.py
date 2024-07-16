from flask import Flask, request, jsonify, Blueprint, make_response
from config import Config
from models.sqlalchemy_setup import db
from models.books import  Book, Author, Category
from models.users import User, UserBooksStarted, UserInterestedCategories, UserBooksRead
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required,  get_jwt_identity
from functools import wraps
import asyncio
from sqlalchemy import desc

auth_service= Blueprint("auth", __name__)

token_expiration_time=timedelta(minutes=300)

def user_data_map(user):
    # Sort the books_started relationship in memory by the date attribute in UserBooksStarted
    books_started_associations = UserBooksStarted.query.filter_by(user_id=user.id).order_by(desc(UserBooksStarted.date)).all()
    books_started = [assoc.book_id for assoc in books_started_associations]
    
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "password": user.password,
        "books_started": books_started
    }
    return user_data



def auth_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        current_user_identity = get_jwt_identity()
        current_user= User.query.filter_by(id= current_user_identity["id"]).first()
        if not current_user:
            return jsonify({'message':'user not found'})
        
        print(current_user) 
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_service.route("/silent_login", methods=["GET"])
@jwt_required()
def silent_login():
    curernt_user_identity= get_jwt_identity()
    current_user= User.query.filter_by(id= curernt_user_identity["id"]).first()
    if not current_user:
        return make_response(jsonify({'message':'user not found'}), 404)
    
    user_data = user_data_map(current_user)
    return jsonify({"user_data":user_data}), 200

@auth_service.route("/login")
def login():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        print(auth)
        return make_response('Could not verify 1st', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    user = User.query.filter_by(email=auth.username).first()
    if not user:
        return make_response('Could not verify 2nd', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    if check_password_hash(user.password, auth.password):
        token = create_access_token(identity={'id': user.id}, expires_delta= token_expiration_time)

        user_data = user_data_map(user)
        print({"user_data": user_data})
        return jsonify({'token': token, "user_data": user_data})
    
    return make_response('Could not verify 3rd', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@auth_service.route("/register", methods=["POST"])
def register():
    data= request.get_json()
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return make_response(jsonify({'message': 'Name, email, and password are required!'}), 400)

    name = data['name']
    email = data['email']
    password = data['password']
    
    new_user= create_user_object(name, email, password)
    token = create_access_token(identity={'id': new_user.id}, expires_delta= token_expiration_time)
    user_data = user_data_map(new_user)
    return jsonify({'token': token, "user_data":user_data})


def create_user_object(name, email, password):
     # Check if the user already exists
    if User.query.filter_by(email=email).first():
        response = make_response(jsonify({'message': 'User already exists!'}), 409)
        return response
    
    hashed_password= generate_password_hash(password, method= "pbkdf2:sha256")
    admin= False
    new_user= User(name= name, email= email, password= hashed_password, admin= admin)
    db.session.add(new_user)
    db.session.commit()

    return new_user