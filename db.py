from config import db, app
from models import Symptom , Condition, Recommendation

# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if Symptom.query.first():
            print("Database already initialized")
            return
        
        # Add sample symptoms
        symptoms_data = [
            {'name': 'Fever', 'description': 'Elevated body temperature', 'body_system': 'General', 'severity_rating': 'Medium'},
            {'name': 'Cough', 'description': 'Persistent coughing', 'body_system': 'Respiratory', 'severity_rating': 'Low'},
            {'name': 'Headache', 'description': 'Pain in head region', 'body_system': 'Neurological', 'severity_rating': 'Low'},
            {'name': 'Chest Pain', 'description': 'Pain in chest area', 'body_system': 'Cardiovascular', 'severity_rating': 'High'},
            {'name': 'Difficulty Breathing', 'description': 'Shortness of breath', 'body_system': 'Respiratory', 'severity_rating': 'High'},
            {'name': 'Nausea', 'description': 'Feeling of sickness', 'body_system': 'Digestive', 'severity_rating': 'Low'},
            {'name': 'Fatigue', 'description': 'Extreme tiredness', 'body_system': 'General', 'severity_rating': 'Low'},
            {'name': 'Dizziness', 'description': 'Feeling lightheaded', 'body_system': 'Neurological', 'severity_rating': 'Medium'}
        ]
        
        for symptom_data in symptoms_data:
            symptom = Symptom(**symptom_data)
            db.session.add(symptom)
        
        # Add sample conditions
        conditions_data = [
            {
                'name': 'Common Cold',
                'icd10_code': 'J00',
                'overview': 'Viral infection of upper respiratory tract',
                'causes': 'Various viruses, primarily rhinoviruses',
                'treatment': 'Rest, fluids, over-the-counter medications'
            },
            {
                'name': 'Migraine',
                'icd10_code': 'G43',
                'overview': 'Severe recurring headaches',
                'causes': 'Neurological disorder, triggers vary',
                'treatment': 'Pain relievers, rest in dark room'
            },
            {
                'name': 'Heart Attack',
                'icd10_code': 'I21',
                'overview': 'Blockage of blood flow to heart',
                'causes': 'Coronary artery disease',
                'treatment': 'IMMEDIATE EMERGENCY CARE REQUIRED'
            },
            {
                'name': 'Influenza',
                'icd10_code': 'J11',
                'overview': 'Viral respiratory infection',
                'causes': 'Influenza virus',
                'treatment': 'Rest, fluids, antiviral medications'
            }
        ]
        
        for condition_data in conditions_data:
            condition = Condition(**condition_data)
            db.session.add(condition)
        
        # Add recommendations
        recommendations = [
            {'condition_id': 1, 'rec_type': 'Self-Care', 'guidance_text': 'Get plenty of rest and stay hydrated', 'is_emergency_alert': False},
            {'condition_id': 2, 'rec_type': 'Consult', 'guidance_text': 'Consult a neurologist if migraines persist', 'is_emergency_alert': False},
            {'condition_id': 3, 'rec_type': 'Urgent', 'guidance_text': 'CALL EMERGENCY SERVICES IMMEDIATELY', 'is_emergency_alert': True},
            {'condition_id': 4, 'rec_type': 'Consult', 'guidance_text': 'See a doctor for antiviral medication', 'is_emergency_alert': False}
        ]
        
        for rec_data in recommendations:
            rec = Recommendation(**rec_data)
            db.session.add(rec)
        
        db.session.commit()
        print("Database initialized with sample data")
