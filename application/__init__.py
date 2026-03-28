import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b6c96e36780b134bbf3cf00b' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'

UPLOAD_FOLDER = 'static/uploads/resumes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)# Creates the directory if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # Max size - 5MB
print("Upload folder set to:", UPLOAD_FOLDER)

db = SQLAlchemy(app)


