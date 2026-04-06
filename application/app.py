import os
from flask import Flask, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b6c96e36780b134bbf3cf00b' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'

# giving absolute path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'resumes')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
print("Upload folder set to:", UPLOAD_FOLDER)

db = SQLAlchemy(app)

from database import models

login_manager = LoginManager()  
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args,**kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role not in roles:
                flash("You do not have permission to access this page", "danger")
                return redirect(url_for('login'))
            return fn(*args , **kwargs)
        return decorated_view
    return wrapper


import routes 
# print("Hellow")
