from flask import Blueprint, request, jsonify, make_response
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models import db
from models.user import Users
from validation.authentication import (
    validate_email, 
    validate_password, 
    validate_username
)

authentication = Blueprint('authentication', __name__)


def perform_login(user, response_message):
    login_user(user)

    response = make_response(
        jsonify({
            'message': response_message,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }))

    expires = datetime.now() + timedelta(days=7)
    response.set_cookie('user_id', str(user.id), httponly=True, secure=True, samesite='Strict', expires=expires)

    return response, 200


@authentication.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}

        if not data:
            return jsonify({'message': 'Request body must be valid JSON.'}), 400

        # Define validation methods
        VALIDATION_METHODS = {
            'email': validate_email,
            'password': validate_password,
            'username': validate_username
        }

        # Validate request data
        for key, method in VALIDATION_METHODS.items():
            value = data.get(key)
            is_valid, message = method(value)
            if not is_valid:
                return jsonify({ 'message': message }), 400

        new_user = Users(
            password=generate_password_hash(data.get('password')),
            email=data.get('email'),
            username=data.get('username'),
            phone_number=data.get('phone_number'),
            bio=data.get('bio'),
            location=data.get('location'),
            created_at=datetime.now()
        )

        db.session.add(new_user)
        db.session.commit()

        user_to_login = Users.query.filter_by(email=new_user.email).first()

        # Successful registration
        return perform_login(user_to_login, 'Welcome to TableTop!')
    
    except Exception as e:
        print(f'An exception occured: {e}')
        return jsonify({ 'message': 'Failed to register.' }), 500
    

@authentication.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        user = Users.query.filter_by(email=data.get('email')).first()

        if not user or not check_password_hash(user.password, data.get('password')):
            return jsonify({'message': 'Invalid credentials.'}), 401

        # Successful login
        return perform_login(user, f'Welcome back {user.username}!')

    except Exception as e:
        print(f'An exception occured: {e}')
        return jsonify({ 'message': 'Failed to log in.' }), 500


@authentication.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()

        response = make_response(jsonify({'message': 'Logged out successfully.'}))
        response.delete_cookie('user_id')

        return response, 200

    except Exception as e:
        print(f'An exception occurred: {e}')
        return jsonify({'message': 'Failed to log out.'}), 500


def serialize_user(user):
    return {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'phoneNumber': getattr(user, 'phone_number', None),
        'bio': getattr(user, 'bio', None),
        'location': user.location,
        'isActive': getattr(user, 'is_active', True)
    }

@authentication.route('/validate-user', methods=['GET'])
@login_required
def validate_user():
    try:
        return jsonify({ 
            'message': 'User successfully validated.',
            'user': serialize_user(current_user)
        }), 200
    except Exception as e:
        print(f'An exception occurred during validation: {e}')
        return jsonify({'message': 'Validation failed.'}), 500


@authentication.route('/update-user', methods=['PUT'])
@login_required
def update_user():
    try:
        data = request.get_json() or {}
        user = current_user  # Fetches the logged-in user context securely

        # 1. Define validation methods for incoming data (if provided)
        VALIDATION_METHODS = {
            'email': validate_email,
            'password': validate_password,
            'username': validate_username
        }

        # 2. Dynamic validation for updated fields
        if 'email' in data and data['email'] != user.email:
            is_valid, message = validate_email(data.get('email'))
            if not is_valid:
                return jsonify({ 'message': message }), 400

        if 'username' in data and data['username'] != user.username:
            is_valid, message = validate_username(data.get('username'))
            if not is_valid:
                return jsonify({ 'message': message }), 400

        if 'password' in data:
            is_valid, message = validate_password(data.get('password'))
            if not is_valid:
                return jsonify({ 'message': message }), 400

        # 3. Handle Email Uniqueness checking if it's changing
        if 'email' in data and data['email'] != user.email:
            existing_email = Users.query.filter_by(email=data['email']).first()
            if existing_email:
                return jsonify({ 'message': 'Email is already taken.' }), 400
            user.email = data['email']

        # 4. Handle Username Uniqueness checking if it's changing
        if 'username' in data and data['username'] != user.username:
            existing_username = Users.query.filter_by(username=data['username']).first()
            if existing_username:
                return jsonify({ 'message': 'Username is already taken.' }), 400
            user.username = data['username']

        # 5. Handle Password Hashing if it's changing
        if 'password' in data:
            user.password = generate_password_hash(data['password'])

        # 6. Map and update other optional profile fields safely
        profile_fields = ['phone_number', 'bio', 'location']
        for field in profile_fields:
            if field in data:
                setattr(user, field, data[field])

        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully.',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }), 200

    except Exception as e:
        print(f'An exception occurred during profile update: {e}')
        db.session.rollback()
        return jsonify({ 'message': 'Failed to update user profile.' }), 500