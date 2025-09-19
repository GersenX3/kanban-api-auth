from flask import Blueprint, request, jsonify
from .models import User, Board
from .db import db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import json
from datetime import datetime

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"msg": "No data provided"}), 400
            
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"msg": "Email and password are required"}), 400

        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"msg": "User already exists"}), 409

        # Hash password
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user = User(email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        # Crear tablero por defecto para el nuevo usuario
        default_columns = [
            {
                "id": "col-1",
                "title": "Pendiente",
                "tasks": [{"id": "t-1", "text": "Primera tarea"}]
            },
            {"id": "col-2", "title": "En progreso", "tasks": []},
            {"id": "col-3", "title": "Hecho", "tasks": []}
        ]
        
        default_board = Board(
            user_id=new_user.id,
            name="Mi Tablero Kanban",
            columns_data=json.dumps(default_columns)
        )
        db.session.add(default_board)
        db.session.commit()

        return jsonify({"msg": "User registered successfully"}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Internal server error"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"msg": "No data provided"}), 400
            
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"msg": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=str(user.id))
            return jsonify({"access_token": access_token}), 200

        return jsonify({"msg": "Invalid credentials"}), 401
        
    except Exception as e:
        return jsonify({"msg": "Internal server error"}), 500

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    try:
        user_id = get_jwt_identity()
        
        # Convertir a int si es string
        if isinstance(user_id, str):
            try:
                user_id = int(user_id)
            except ValueError:
                return jsonify({"msg": "Invalid user ID"}), 400
                
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        return jsonify({"id": user.id, "email": user.email}), 200
        
    except Exception as e:
        return jsonify({"msg": "Internal server error"}), 500

# NUEVAS RUTAS PARA MANEJO DE TABLEROS

@auth_bp.route("/boards", methods=["GET"])
@jwt_required()
def get_boards():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        boards = Board.query.filter_by(user_id=user_id).all()
        return jsonify([board.to_dict() for board in boards]), 200
        
    except Exception as e:
        return jsonify({"msg": "Internal server error"}), 500

@auth_bp.route("/boards/<int:board_id>", methods=["GET"])
@jwt_required()
def get_board(board_id):
    try:
        user_id = int(get_jwt_identity())
        board = Board.query.filter_by(id=board_id, user_id=user_id).first()
        
        if not board:
            return jsonify({"msg": "Board not found"}), 404
            
        return jsonify(board.to_dict()), 200
        
    except Exception as e:
        return jsonify({"msg": "Internal server error"}), 500

@auth_bp.route("/boards", methods=["POST"])
@jwt_required()
def create_board():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        name = data.get("name", "Nuevo Tablero")
        columns = data.get("columns", [])
        
        new_board = Board(
            user_id=user_id,
            name=name,
            columns_data=json.dumps(columns)
        )
        
        db.session.add(new_board)
        db.session.commit()
        
        return jsonify(new_board.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Internal server error"}), 500

@auth_bp.route("/boards/<int:board_id>", methods=["PUT"])
@jwt_required()
def update_board(board_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        board = Board.query.filter_by(id=board_id, user_id=user_id).first()
        
        if not board:
            return jsonify({"msg": "Board not found"}), 404
        
        if "name" in data:
            board.name = data["name"]
        
        if "columns" in data:
            board.set_columns(data["columns"])
        
        board.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(board.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Internal server error"}), 500

@auth_bp.route("/boards/<int:board_id>", methods=["DELETE"])
@jwt_required()
def delete_board():
    try:
        user_id = int(get_jwt_identity())
        board = Board.query.filter_by(id=board_id, user_id=user_id).first()
        
        if not board:
            return jsonify({"msg": "Board not found"}), 404
        
        db.session.delete(board)
        db.session.commit()
        
        return jsonify({"msg": "Board deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Internal server error"}), 500

# Ruta especial para actualizar solo las columnas (optimizada para el drag & drop)
@auth_bp.route("/boards/<int:board_id>/columns", methods=["PUT"])
@jwt_required()
def update_board_columns(board_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        board = Board.query.filter_by(id=board_id, user_id=user_id).first()
        
        if not board:
            return jsonify({"msg": "Board not found"}), 404
        
        if "columns" not in data:
            return jsonify({"msg": "Columns data required"}), 400
        
        board.set_columns(data["columns"])
        board.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"msg": "Columns updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Internal server error"}), 500

# Mantener las rutas existentes de autenticación
@auth_bp.route("/debug-token", methods=["GET"])
@jwt_required()
def debug_token():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        return jsonify({
            "user_id": user_id,
            "user_exists": user is not None,
            "user_email": user.email if user else None
        }), 200
    except Exception as e:
        return jsonify({"msg": f"Debug error: {str(e)}"}), 500

@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({"msg": "No data provided"}), 400
            
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if not new_password or not confirm_password:
            return jsonify({"msg": "Both password fields are required"}), 400

        if new_password != confirm_password:
            return jsonify({"msg": "Passwords do not match"}), 400

        # Validación adicional de la contraseña
        if len(new_password) < 6:
            return jsonify({"msg": "Password must be at least 6 characters long"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404

        hashed_pw = bcrypt.generate_password_hash(new_password).decode("utf-8")
        user.password = hashed_pw
        db.session.commit()

        return jsonify({"msg": "Password updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Internal server error"}), 500

@auth_bp.route("/delete-account", methods=["DELETE"])
@jwt_required()
def delete_account():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({"msg": "No data provided"}), 400
            
        confirm_email = data.get("email")

        if not confirm_email:
            return jsonify({"msg": "Email confirmation is required"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404

        if user.email != confirm_email:
            return jsonify({"msg": "Email confirmation does not match"}), 400

        db.session.delete(user)
        db.session.commit()

        return jsonify({"msg": "Account deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Internal server error"}), 500