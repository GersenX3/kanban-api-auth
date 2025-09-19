from .db import db
from datetime import datetime
import json

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con boards
    boards = db.relationship('Board', backref='user', lazy=True, cascade='all, delete-orphan')

class Board(db.Model):
    __tablename__ = "boards"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), default='Mi Tablero Kanban')
    columns_data = db.Column(db.Text, nullable=False)  # JSON string con las columnas y tareas
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_columns(self):
        """Convierte el JSON string a dict de Python"""
        try:
            return json.loads(self.columns_data)
        except:
            return []
    
    def set_columns(self, columns):
        """Convierte el dict de Python a JSON string"""
        self.columns_data = json.dumps(columns)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'columns': self.get_columns(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }