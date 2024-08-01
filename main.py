from flask import Flask, request, jsonify
import flask
from config import Config
from flask_apps.book_service import books_service
from flask_apps.user_service import user_service
from flask_apps.auth_service import auth_service
from flask_apps.app_service import app_service
from models.sqlalchemy_setup import db
from models.users import User
from flask_jwt_extended import JWTManager, decode_token, jwt_required, get_jwt_identity
from functools import wraps
import os

app= Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

jwt = JWTManager(app)
                        
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(books_service)
app.register_blueprint(user_service)
app.register_blueprint(auth_service)
app.register_blueprint(app_service)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token= None
        
        if 'x-access-token' in request.headers:
            token= request.headers["x-access-token"]
            
        if not token:
            return jsonify({"message": "Token is missing"})
        
        try:
            # data= jwt.decode(token,"your_secret_key" )
            data= decode_token(token)
            
            print(data["sub"])
            # use id here as in auth_service.login(), we use id as the identity
            current_user = User.query.filter_by(id=int(data["sub"])).first() #<- INVALID TOKEN CAUSED HERE
        
            print(current_user)
            
        except:
            return jsonify({"message": "Token is invalid"}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated




@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)


import functions_framework

@functions_framework.http
def cors_enabled_function(request):
    # For more information about CORS and CORS preflight requests, see:
    # https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request

    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }

        return ("", 204, headers)

    # Set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}

    return ("Hello World!", 200, headers)
