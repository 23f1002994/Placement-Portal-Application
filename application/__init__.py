import os
from flask import Flask , redirect , url_for , flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager , current_user
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b6c96e36780b134bbf3cf00b' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'

UPLOAD_FOLDER = 'static/uploads/resumes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)# Creates the directory if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # Max size - 5MB
print("Upload folder set to:", UPLOAD_FOLDER)

db = SQLAlchemy(app)

from application.database import models

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

# Rendering the routes after running the init
from application import routes
