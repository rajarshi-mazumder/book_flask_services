from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Blueprint, request, jsonify
from models.sqlalchemy_setup import db
import boto3
from dotenv import load_dotenv
import os
from botocore.exceptions import NoCredentialsError


storage_service= Blueprint("storage_service", __name__)

load_dotenv()

BUCKET_NAME= os.getenv('S3_BUCKET_NAME')
S3_REGION= os.getenv('S3_REGION')

s3= boto3.client(
    's3',
    region_name= S3_REGION,
    aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key= os.getenv("AWS_SECRET_ACCESS_KEY")
)

@storage_service.route("/upload_image", methods=["POST"])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file= request.files["file"]
    
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400
    
    try:
        s3.upload_fileobj(file, BUCKET_NAME, file.filename)

        file_url= f"https://{BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{file.filename}"

        return jsonify({"message": f"File '{file.filename}' uploaded successfully", "file_url": file_url}), 200

    except NoCredentialsError:
        return jsonify({"error": "Credentials not available"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@storage_service.route("/get_pre_signed_url")
def get_pre_signed_url():
    try:    
       object_name= request.args.get('object_name')
        
       response= generate_pre_signed_url(object_name)
    
    except NoCredentialsError:
        return jsonify({"error": "Credentials not available"}), 500
    return jsonify({"signed_url": response})
        

def generate_pre_signed_url(object_name, expiration=3600):
    response= s3.generate_presigned_url('get_object',
                                Params={
                                    'Bucket':BUCKET_NAME,
                                    'Key': object_name
                                },
                                ExpiresIn= expiration)
    return response