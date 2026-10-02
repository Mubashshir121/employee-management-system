import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)

    else:
        user = quote_plus(os.getenv("DB_USER", "root"))
        password = quote_plus(os.getenv("DB_PASSWORD", ""))
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        name = os.getenv("DB_NAME", "employee_management")
        database_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False