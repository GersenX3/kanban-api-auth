from flask import Flask
from flask_jwt_extended import JWTManager
from .db import db
from .routes import auth_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://authuser:secret@postgres:5432/authdb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"

db.init_app(app)
JWTManager(app)
app.register_blueprint(auth_bp, url_prefix="/auth")
