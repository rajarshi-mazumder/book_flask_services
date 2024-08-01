from flask import Flask, request, jsonify, Blueprint, make_response
from config import Config
from models.additional_user_data import  AdditionalAppData
from models.sqlalchemy_setup import db
from models.users import User, UserBooksStarted, UserBooksRead, UserInterestedCategories
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import JWTManager, create_access_token
from .auth_service import auth_required, create_user_object, user_data_map

app_service= Blueprint("app_service", __name__)

@app_service.route("/update_app_data", methods=["POST"])
def update_app_data():
    data = request.get_json()
    last_books_list_version = data.get("last_books_list_version")

    if not last_books_list_version:
        return jsonify({"error": "booksListVersion is required"}), 400

    try:
        # Fetch the singleton instance of AdditionalAppData
        app_data = AdditionalAppData.query.first()
        
        # If no record exists, create one
        if app_data is None:
            app_data = AdditionalAppData(last_books_list_version=last_books_list_version)
            db.session.add(app_data)
        else:
            # Update the existing record
            app_data.last_books_list_version = last_books_list_version
        
        # Commit the changes to the database
        db.session.commit()
        return jsonify({"message": "Books list version updated successfully"}), 200
    
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify({"error": str(e)}), 500