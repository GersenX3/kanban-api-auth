from flask import Flask
from flask_jwt_extended import JWTManager
from .db import db
from .routes import auth_bp
from flask_migrate import Migrate
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://authuser:supersecretpassword@postgres-auth/authdb"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "super-secret-key"

    db.init_app(app)
    JWTManager(app)
    Migrate(app, db)

    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app
