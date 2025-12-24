import datetime
from config import db

# ==========================================
# DATABASE MODELS (Based on ERD)
# ==========================================

class User(db.Model):
    __tablename__ = 'user'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    
    # Relationships
    history_records = db.relationship('HistoryRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'first_name': self.first_name,
            'gender': self.gender,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }


class Symptom(db.Model):
    __tablename__ = 'symptom'
    
    symptom_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    body_system = db.Column(db.String(100), nullable=True)
    severity_rating = db.Column(db.Enum('Low', 'Medium', 'High'), nullable=True)
    
    # Relationships
    symptom_checks = db.relationship('SymptomCheck', backref='symptom', lazy=True)
    
    def to_dict(self):
        return {
            'symptom_id': self.symptom_id,
            'name': self.name,
            'description': self.description,
            'body_system': self.body_system,
            'severity_rating': self.severity_rating
        }


class Condition(db.Model):
    __tablename__ = 'condition'
    
    condition_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    icd10_code = db.Column(db.String(20), unique=True, nullable=True)
    overview = db.Column(db.Text, nullable=True)
    causes = db.Column(db.Text, nullable=True)
    treatment = db.Column(db.Text, nullable=True)
    
    # Relationships
    diagnosis_suggestions = db.relationship('DiagnosisSuggestion', backref='condition', lazy=True)
    recommendations = db.relationship('Recommendation', backref='condition', lazy=True)
    
    def to_dict(self):
        return {
            'condition_id': self.condition_id,
            'name': self.name,
            'icd10_code': self.icd10_code,
            'overview': self.overview,
            'causes': self.causes,
            'treatment': self.treatment
        }


class HistoryRecord(db.Model):
    __tablename__ = 'history_record'
    
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    check_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    final_confidence_score = db.Column(db.Numeric(5, 2), nullable=True)
    
    # Relationships
    diagnosis_suggestions = db.relationship('DiagnosisSuggestion', backref='history_record', lazy=True, cascade='all, delete-orphan')
    symptom_checks = db.relationship('SymptomCheck', backref='history_record', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'history_id': self.history_id,
            'user_id': self.user_id,
            'check_timestamp': self.check_timestamp.isoformat(),
            'final_confidence_score': float(self.final_confidence_score) if self.final_confidence_score else None,
            'symptoms': [sc.symptom.name for sc in self.symptom_checks],
            'diagnoses': [ds.to_dict() for ds in self.diagnosis_suggestions]
        }


class DiagnosisSuggestion(db.Model):
    __tablename__ = 'diagnosis_suggestion'
    
    suggestion_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    history_id = db.Column(db.Integer, db.ForeignKey('history_record.history_id'), nullable=False)
    condition_id = db.Column(db.Integer, db.ForeignKey('condition.condition_id'), nullable=False)
    confidence_level = db.Column(db.Numeric(5, 2), nullable=False)
    
    def to_dict(self):
        return {
            'suggestion_id': self.suggestion_id,
            'condition': self.condition.to_dict(),
            'confidence_level': float(self.confidence_level)
        }


class SymptomCheck(db.Model):
    __tablename__ = 'symptom_check'
    
    check_link_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    history_id = db.Column(db.Integer, db.ForeignKey('history_record.history_id'), nullable=False)
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptom.symptom_id'), nullable=False)
    is_critical = db.Column(db.Boolean, default=False)


class Recommendation(db.Model):
    __tablename__ = 'recommendation'
    
    rec_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    condition_id = db.Column(db.Integer, db.ForeignKey('condition.condition_id'), nullable=False)
    rec_type = db.Column(db.Enum('Self-Care', 'Consult', 'Urgent'), nullable=True)
    guidance_text = db.Column(db.Text, nullable=False)
    is_emergency_alert = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'rec_id': self.rec_id,
            'rec_type': self.rec_type,
            'guidance_text': self.guidance_text,
            'is_emergency_alert': self.is_emergency_alert
        }


class Notification(db.Model):
    __tablename__ = 'notification'
    
    notif_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    notif_type = db.Column(db.Enum('Reminder', 'Health Tip', 'Alert'), nullable=True)
    message_body = db.Column(db.String(500), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'notif_id': self.notif_id,
            'notif_type': self.notif_type,
            'message_body': self.message_body,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'is_read': self.is_read
        }


# ==========================================
# SYMPTOM-CONDITION MAPPING TABLE
# ==========================================
# Many-to-many relationship between symptoms and conditions
symptom_condition_map = db.Table('symptom_condition_map',
    db.Column('symptom_id', db.Integer, db.ForeignKey('symptom.symptom_id'), primary_key=True),
    db.Column('condition_id', db.Integer, db.ForeignKey('condition.condition_id'), primary_key=True)
)