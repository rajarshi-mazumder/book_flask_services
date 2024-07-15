import os
class Config:
    username = "postgres"
    password = "Jesus1145"
    hostname = "postgres.cto6w4w2mmw5.us-east-1.rds.amazonaws.com"
    port = "5432"
    database = "postgres"

    SQLALCHEMY_DATABASE_URI  = f"postgresql://{username}:{password}@{hostname}:{port}/{database}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
