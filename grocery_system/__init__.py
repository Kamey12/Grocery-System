import os
from flask import Flask
from flask_login import LoginManager
from .models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocery.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images', 'products')

    db.init_app(app)
    login_manager.init_app(app)

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.store import store_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(admin_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))