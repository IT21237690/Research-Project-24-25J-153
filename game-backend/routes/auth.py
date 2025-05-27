from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, get_jwt_identity,
    jwt_required, set_access_cookies, unset_jwt_cookies
)
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import datetime
import pymongo
import os
auth_bp = Blueprint('auth', __name__)
from flask_cors import cross_origin

# Access MongoDB from main app
mongo_uri = os.environ.get('MONGO_URI', 'mongodb+srv://dbuser:dbuser123@researchproject.ojxgd.mongodb.net/object_recognition_game?retryWrites=true&w=majority&appName=ResearchProject')
client = pymongo.MongoClient(mongo_uri)
db = client.get_database()

@auth_bp.route('/register', methods=['POST'])
@cross_origin(supports_credentials=True)
def register():
    data = request.get_json()

    # Validate input
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({
            'success': False,
            'message': 'Username and password are required'
        }), 400

    # Check if username already exists
    if db.users.find_one({'username': data['username']}):
        return jsonify({
            'success': False,
            'message': 'Username already exists'
        }), 400

    # Create new user
    new_user = {
        'username': data['username'],
        'password': generate_password_hash(data['password']),
        'email': data.get('email', ''),
        'created_at': datetime.datetime.now(),
        'highScore': 0,
        'currentLevel': 1,
        'difficulty': 1,
        'totalGames': 0,
        'completedGames': 0
    }

    user_id = db.users.insert_one(new_user).inserted_id

    # Create access token
    access_token = create_access_token(identity=str(user_id))

    # Return user info (excluding password)
    user_info = dict(new_user)
    user_info.pop('password')
    user_info['_id'] = str(user_info['_id'])

    return jsonify({
        'success': True,
        'token': access_token,
        'user': user_info
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validate input
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({
            'success': False,
            'message': 'Username and password are required'
        }), 400

    # Find user
    user = db.users.find_one({'username': data['username']})

    # Check if user exists and password is correct
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401

    # Create access token
    access_token = create_access_token(identity=str(user['_id']))

    # Return user info (excluding password)
    user_info = dict(user)
    user_info.pop('password')
    user_info['_id'] = str(user_info['_id'])

    return jsonify({
        'success': True,
        'token': access_token,
        'user': user_info
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()

    # Find user
    user = db.users.find_one({'_id': ObjectId(user_id)})

    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404

    # Return user info (excluding password)
    user_info = dict(user)
    user_info.pop('password')
    user_info['_id'] = str(user_info['_id'])

    return jsonify({
        'success': True,
        'user': user_info
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({'success': True, 'message': 'Successfully logged out'})
    unset_jwt_cookies(resp)
    return resp, 200
