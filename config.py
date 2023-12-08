# config.py

import os

class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database.db'
    UPLOAD_FOLDER = 'uploads'
    MAIL_SERVER = 'your_mail_server'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'your_email@example.com'
    MAIL_PASSWORD = 'your_email_password'
