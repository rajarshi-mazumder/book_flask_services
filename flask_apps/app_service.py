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
    last_categories_list_version = data.get("last_categories_list_version")
    last_collections_list_version = data.get("last_collections_list_version")
    
    # Fetch the singleton instance of AdditionalAppData
    app_data = AdditionalAppData.query.first()

    # Ensure a default value for books list version if not provided
    if not last_books_list_version:
        if app_data and app_data.last_books_list_version is not None:
            last_books_list_version = app_data.last_books_list_version
        else:
            last_books_list_version = "1.0"

    # Ensure a default value for categories list version if not provided
    if not last_categories_list_version:
        if app_data and hasattr(app_data, 'last_categories_list_version') and app_data.last_categories_list_version is not None:
            last_categories_list_version = app_data.last_categories_list_version
        else:
            last_categories_list_version = "1.0"

    # Ensure a default value for categories list version if not provided
    if not last_collections_list_version:
        if app_data and hasattr(app_data, 'last_collections_list_version') and app_data.last_collections_list_version is not None:
            last_collections_list_version = app_data.last_collections_list_version
        else:
            last_collections_list_version = "1.0"


    try:
        # If no record exists, create one
        if app_data is None:
            app_data = AdditionalAppData(
                last_books_list_version=last_books_list_version,
                last_categories_list_version=last_categories_list_version,
                last_collections_list_version=last_collections_list_version
            )
            db.session.add(app_data)
        else:
            # Update the existing record
            app_data.last_books_list_version = last_books_list_version
            app_data.last_categories_list_version = last_categories_list_version
            app_data.last_collections_list_version= last_collections_list_version

        # Commit the changes to the database
        db.session.commit()
        return jsonify({"message": "App data updated successfully"}), 200

    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify({"error": str(e)}), 500

    
@app_service.route("/app_data", methods=["GET"])
def get_app_data():
    app_data= AdditionalAppData.query.first()
    print(app_data)
    return {"app_data": {"last_books_list_version": app_data.last_books_list_version,
                         "last_categories_list_version":app_data.last_categories_list_version,
                         "last_collections_list_version":app_data.last_collections_list_version
                         }}