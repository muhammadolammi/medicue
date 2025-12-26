from flask import Flask, request, jsonify
from flask_jwt_extended import  create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

from sqlalchemy import func, or_
# from models import User, Symptom, Condition, HistoryRecord, Notification,  SymptomCheck, DiagnosisSuggestion
from models import TokenBlocklist, User

from config import app, bcrypt,db 

from ai import get_medical_analysis



# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User Registration - REQ-6, REQ-7"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('email') or not data.get('password') or not data.get('first_name') or not data.get('last_name') or not data.get('gender') or not data.get('birth_date'):
            return jsonify({'error': 'Email, password,  first name, last name, gender and birth date are required'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password - REQ-8
        password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        # Create user
        new_user = User(
            email=data['email'],
            password_hash=password_hash,
            first_name=data['first_name'],
            last_name=data['last_name'],
            gender=data['gender'],
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() 
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        
        
        return jsonify({
            'message': 'Registration successful',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User Login - REQ-9"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        access_token = create_access_token(identity=user.user_id)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get User Profile - REQ-11"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


from flask_jwt_extended import get_jwt

@app.route('/api/auth/logout', methods=['DELETE'])
@jwt_required()
def logout():
    """User Logout - REQ-10"""
    try:
        # Get the unique identifier (JTI) for the current JWT
        jti = get_jwt()["jti"]
        
        # Add the JTI to our blocklist in the database
        db.session.add(TokenBlocklist(jti=jti))
        db.session.commit()
        
        return jsonify({'message': 'Access token revoked successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# # ==========================================
# # SYMPTOM ENDPOINTS
# # ==========================================

# @app.route('/api/symptoms', methods=['GET'])
# def get_symptoms():
#     """Get all symptoms with optional filtering - REQ-25, REQ-27"""
#     try:
#         query = Symptom.query
        
#         # Search filter
#         search = request.args.get('search', '')
#         if search:
#             query = query.filter(
#                 or_(
#                     Symptom.name.ilike(f'%{search}%'),
#                     Symptom.description.ilike(f'%{search}%')
#                 )
#             )
        
#         # Body system filter
#         body_system = request.args.get('body_system')
#         if body_system:
#             query = query.filter_by(body_system=body_system)
        
#         # Severity filter
#         severity = request.args.get('severity')
#         if severity:
#             query = query.filter_by(severity_rating=severity)
        
#         symptoms = query.all()
#         return jsonify([s.to_dict() for s in symptoms]), 200
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @app.route('/api/symptoms/<int:symptom_id>', methods=['GET'])
# def get_symptom(symptom_id):
#     """Get specific symptom details"""
#     try:
#         symptom = Symptom.query.get(symptom_id)
#         if not symptom:
#             return jsonify({'error': 'Symptom not found'}), 404
        
#         return jsonify(symptom.to_dict()), 200
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# ==========================================
# CONDITION ENDPOINTS
# ==========================================

# @app.route('/api/conditions', methods=['GET'])
# def get_conditions():
#     """Get all conditions with optional filtering"""
#     try:
#         query = Condition.query
        
#         # Search filter
#         search = request.args.get('search', '')
#         if search:
#             query = query.filter(
#                 or_(
#                     Condition.name.ilike(f'%{search}%'),
#                     Condition.overview.ilike(f'%{search}%')
#                 )
#             )
        
#         conditions = query.all()
#         return jsonify([c.to_dict() for c in conditions]), 200
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @app.route('/api/conditions/<int:condition_id>', methods=['GET'])
# def get_condition(condition_id):
#     """Get specific condition details with recommendations"""
#     try:
#         condition = Condition.query.get(condition_id)
#         if not condition:
#             return jsonify({'error': 'Condition not found'}), 404
        
#         result = condition.to_dict()
#         result['recommendations'] = [r.to_dict() for r in condition.recommendations]
        
#         return jsonify(result), 200
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# ==========================================
# SYMPTOM CHECK & DIAGNOSIS
# ==========================================
@app.route('/api/analyze', methods=['POST'])
@jwt_required()
def symptom_check():
    current_user_id = get_jwt_identity()
    data = request.json
    symptoms_text = data.get('symptoms_text', "")
    
    if not symptoms_text:
        return jsonify({"error": "No symptoms provided"}), 400

    # Call Gemini to get structured analysis
    analysis_result = get_medical_analysis(symptoms_text)
    
    # Return the structured data to the Android App [cite: 502, 506]
    return jsonify(analysis_result)

# @app.route('/api/symptom-check', methods=['POST'])
# @jwt_required()
# def symptom_check():
    """Analyze symptoms and provide diagnosis - REQ-1 to REQ-5, REQ-18 to REQ-24"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        symptom_ids = data.get('symptom_ids', [])
        if not symptom_ids:
            return jsonify({'error': 'Please provide at least one symptom'}), 400
        
        # Create history record
        history_record = HistoryRecord(
            user_id=user_id,
            check_timestamp=datetime.utcnow()
        )
        db.session.add(history_record)
        db.session.flush()  # Get history_id
        
        # Check for critical symptoms - REQ-18
        has_emergency = False
        for symptom_id in symptom_ids:
            symptom = Symptom.query.get(symptom_id)
            if symptom:
                is_critical = symptom.severity_rating == 'High'
                if is_critical:
                    has_emergency = True
                
                symptom_check = SymptomCheck(
                    history_id=history_record.history_id,
                    symptom_id=symptom_id,
                    is_critical=is_critical
                )
                db.session.add(symptom_check)
        
        # Find matching conditions using simple algorithm
        # In production, this would be more sophisticated
        all_conditions = Condition.query.all()
        matches = []
        
        for condition in all_conditions:
            # Get symptoms associated with this condition
            # This is simplified - in production, use proper symptom_condition_map
            match_score = 0
            total_symptoms = len(symptom_ids)
            
            # Simple matching logic (you'd enhance this with actual mappings)
            # For now, using condition name keywords matching symptom names
            for symptom_id in symptom_ids:
                symptom = Symptom.query.get(symptom_id)
                if symptom and (symptom.name.lower() in condition.name.lower() or 
                               symptom.name.lower() in condition.overview.lower()):
                    match_score += 1
            
            if match_score > 0:
                confidence = (match_score / total_symptoms) * 100
                matches.append({
                    'condition': condition,
                    'confidence': confidence
                })
        
        # Sort by confidence
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Save top diagnosis suggestions
        top_confidence = 0
        for match in matches[:5]:  # Top 5 matches
            suggestion = DiagnosisSuggestion(
                history_id=history_record.history_id,
                condition_id=match['condition'].condition_id,
                confidence_level=match['confidence']
            )
            db.session.add(suggestion)
            if match['confidence'] > top_confidence:
                top_confidence = match['confidence']
        
        history_record.final_confidence_score = top_confidence
        
        # Create emergency alert notification if needed - REQ-19
        if has_emergency:
            notification = Notification(
                user_id=user_id,
                notif_type='Alert',
                message_body='EMERGENCY: Your symptoms may require immediate medical attention. Please consult a healthcare professional or visit the emergency room.',
                scheduled_time=datetime.utcnow()
            )
            db.session.add(notification)
        
        db.session.commit()
        
        # Prepare response
        result = {
            'history_id': history_record.history_id,
            'timestamp': history_record.check_timestamp.isoformat(),
            'has_emergency': has_emergency,
            'final_confidence_score': float(top_confidence),
            'diagnoses': [
                {
                    'condition': m['condition'].to_dict(),
                    'confidence': m['confidence']
                } for m in matches[:5]
            ]
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# # ==========================================
# # HISTORY ENDPOINTS
# # ==========================================

# @app.route('/api/history', methods=['GET'])
# @jwt_required()
# def get_history():
#     """Get user's symptom check history - REQ-12, REQ-13"""
#     try:
#         user_id = get_jwt_identity()
        
#         # Get history in reverse chronological order - REQ-13
#         history = HistoryRecord.query.filter_by(user_id=user_id)\
#             .order_by(HistoryRecord.check_timestamp.desc())\
#             .all()
        
#         return jsonify([h.to_dict() for h in history]), 200
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @app.route('/api/history/<int:history_id>', methods=['GET'])
# @jwt_required()
# def get_history_detail(history_id):
#     """Get detailed history record - REQ-14"""
#     try:
#         user_id = get_jwt_identity()
        
#         history = HistoryRecord.query.filter_by(
#             history_id=history_id,
#             user_id=user_id
#         ).first()
        
#         if not history:
#             return jsonify({'error': 'History record not found'}), 404
        
#         return jsonify(history.to_dict()), 200
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @app.route('/api/history/<int:history_id>', methods=['DELETE'])
# @jwt_required()
# def delete_history(history_id):
#     """Delete history record - REQ-16"""
#     try:
#         user_id = get_jwt_identity()
        
#         history = HistoryRecord.query.filter_by(
#             history_id=history_id,
#             user_id=user_id
#         ).first()
        
#         if not history:
#             return jsonify({'error': 'History record not found'}), 404
        
#         db.session.delete(history)
#         db.session.commit()
        
#         return jsonify({'message': 'History record deleted successfully'}), 200
        
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500


# # ==========================================
# # NOTIFICATION ENDPOINTS
# # ==========================================

# @app.route('/api/notifications', methods=['GET'])
# @jwt_required()
# def get_notifications():
#     """Get user notifications"""
#     try:
#         user_id = get_jwt_identity()
        
#         notifications = Notification.query.filter_by(user_id=user_id)\
#             .order_by(Notification.scheduled_time.desc())\
#             .all()
        
#         return jsonify([n.to_dict() for n in notifications]), 200
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @app.route('/api/notifications/<int:notif_id>/read', methods=['PATCH'])
# @jwt_required()
# def mark_notification_read(notif_id):
#     """Mark notification as read"""
#     try:
#         user_id = get_jwt_identity()
        
#         notification = Notification.query.filter_by(
#             notif_id=notif_id,
#             user_id=user_id
#         ).first()
        
#         if not notification:
#             return jsonify({'error': 'Notification not found'}), 404
        
#         notification.is_read = True
#         db.session.commit()
        
#         return jsonify({'message': 'Notification marked as read'}), 200
        
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500


# # ==========================================
# # ADMIN ENDPOINTS
# # ==========================================

# @app.route('/api/admin/symptoms', methods=['POST'])
# @jwt_required()
# def add_symptom():
#     """Add new symptom (Admin only)"""
#     try:
#         user_id = get_jwt_identity()
#         user = User.query.get(user_id)
        
#         if not user.is_admin:
#             return jsonify({'error': 'Admin access required'}), 403
        
#         data = request.get_json()
        
#         new_symptom = Symptom(
#             name=data['name'],
#             description=data.get('description'),
#             body_system=data.get('body_system'),
#             severity_rating=data.get('severity_rating')
#         )
        
#         db.session.add(new_symptom)
#         db.session.commit()
        
#         return jsonify({
#             'message': 'Symptom added successfully',
#             'symptom': new_symptom.to_dict()
#         }), 201
        
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500


# @app.route('/api/admin/conditions', methods=['POST'])
# @jwt_required()
# def add_condition():
#     """Add new condition (Admin only)"""
#     try:
#         user_id = get_jwt_identity()
#         user = User.query.get(user_id)
        
#         if not user.is_admin:
#             return jsonify({'error': 'Admin access required'}), 403
        
#         data = request.get_json()
        
#         new_condition = Condition(
#             name=data['name'],
#             icd10_code=data.get('icd10_code'),
#             overview=data.get('overview'),
#             causes=data.get('causes'),
#             treatment=data.get('treatment')
#         )
        
#         db.session.add(new_condition)
#         db.session.commit()
        
#         return jsonify({
#             'message': 'Condition added successfully',
#             'condition': new_condition.to_dict()
#         }), 201
        
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500


# # ==========================================
# # HEALTH CHECK
# # ==========================================

# @app.route('/api/health', methods=['GET'])
# def health_check():
#     """API Health Check"""
#     return jsonify({
#         'status': 'healthy',
#         'timestamp': datetime.utcnow().isoformat(),
#         'version': '1.0.0'
#     }), 200

