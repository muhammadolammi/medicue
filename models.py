import datetime
from config import db

# # ==========================================
# # SYMPTOM-CONDITION MAPPING TABLE (Many-to-Many)
# # ==========================================
# symptom_condition_map = db.Table('symptom_condition_map',
#     db.Column('symptom_id', db.Integer, db.ForeignKey('symptom.symptom_id'), primary_key=True),
#     db.Column('condition_id', db.Integer, db.ForeignKey('condition.condition_id'), primary_key=True)
# )

# ==========================================
# DATABASE MODELS
# ==========================================

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    # # Relationships
    # # Note: ForeignKey in child tables must point to 'users.user_id'
    # history_records = db.relationship('HistoryRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    # notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'created_at': self.created_at.isoformat()
        }




class TokenBlocklist(db.Model):
    __tablename__ = 'blacklisted_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))