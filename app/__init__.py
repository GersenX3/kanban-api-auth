from flask import Flask
from flask_jwt_extended import JWTManager
from .db import db
from .routes import auth_bp

def create_app():
    app = Flask(__name__)

    # Configuración básica
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql+psycopg2://authuser:secret@postgres:5432/authdb"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # 🔑 cámbiala en prod

    # Inicializar extensiones
    db.init_app(app)
    JWTManager(app)

    # Registrar rutas
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app
