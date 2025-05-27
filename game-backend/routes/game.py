import os
import random
from datetime import datetime

import pymongo
from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify

game_bp = Blueprint('game', __name__)

from services.image_generator import ImageGenerator
from services.object_detector import ObjectDetector

mongo_uri = os.environ.get('MONGO_URI', 'mongodb+srv://dbuser:dbuser123@researchproject.ojxgd.mongodb.net/object_recognition_game?retryWrites=true&w=majority&appName=ResearchProject')
client = pymongo.MongoClient(mongo_uri)
db = client.get_database()


@game_bp.route('/new-round', methods=['GET'])
def new_round():
    """
    Generate a new round
    """
    try:
        # Get difficulty level from request (default to 1)
        difficulty = int(request.args.get('difficulty', 1))
        difficulty = max(1, min(5, difficulty))  # Ensure difficulty is between 1-5

        # Initialize image generator with app config
        image_generator = ImageGenerator()

        # Generate a new image based on difficulty
        result = image_generator.generate_image(difficulty, provider="pollination")

        if not result.get('image_path'):
            return jsonify({
                'success': False,
                'message': 'Failed to generate image',
                'error': result.get('error', 'Unknown error')
            }), 500

        game_theme = result['theme']
        image_path = result['image_path']

        """
            Generate a new round 
            """
        detector = ObjectDetector()
        detect_result = detector.verify_generated_image(
            image_path,
            game_theme
        )
        detected_objects = detect_result['found_objects']

        # Get relative path for the frontend
        image_url = result['image_url']

        # Generate distractor objects
        distractors = generate_distractors(detected_objects, difficulty)

        # Mix objects and distractors for answer options
        answer_options = detected_objects + distractors

        random.shuffle(answer_options)

        # Create a game session in the database
        session_id = str(uuid.uuid4())

        db.game_sessions.insert_one({
            'session_id': session_id,
            'image_path': image_path,
            'image_url': image_url,
            'objects_to_find': detected_objects,
            'answer_options': answer_options,
            'difficulty': difficulty,
            'created_at': datetime.now()
        })

        return jsonify({
            'success': True,
            'session_id': session_id,
            'imageUrl': image_url,
            'objectsToFind': detected_objects,
            'answerOptions': answer_options,
            'difficulty': difficulty
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred',
            'error': str(e)
        }), 500


@game_bp.route('/save-score', methods=['POST'])
def save_score():
    """
    Save the user's score and progress
    """
    try:
        data = request.json
        user_id = data.get('userId')
        score = data.get('score', 0)
        level = data.get('level', 1)
        difficulty = data.get('difficulty', 1)

        if not user_id:
            # Get user ID from session if available
            user_id = request.cookies.get('user_id')

        if user_id:
            # Update the user's score in the database
            db.users.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'currentLevel': level,
                        'difficulty': difficulty,
                        'lastPlayed': datetime.now()
                    },
                    '$max': {'highScore': score}
                }
            )

            # Add to score history
            db.scores.insert_one({
                'userId': ObjectId(user_id),
                'score': score,
                'level': level,
                'difficulty': difficulty,
                'timestamp': datetime.now()
            })

            return jsonify({
                'success': True,
                'message': 'Score saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to save score',
            'error': str(e)
        }), 500


@game_bp.route('/update-progress', methods=['POST'])
def update_progress():
    """
    Update the user's game progress
    """
    try:
        data = request.json
        user_id = data.get('userId')
        level = data.get('level', 1)
        difficulty = data.get('difficulty', 1)

        if not user_id:
            # Get user ID from session if available
            user_id = request.cookies.get('user_id')

        if user_id:
            # Update the user's progress in the database
            db.users.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'currentLevel': level,
                        'difficulty': difficulty,
                        'lastPlayed': datetime.now()
                    }
                }
            )

            return jsonify({
                'success': True,
                'message': 'Progress updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to update progress',
            'error': str(e)
        }), 500


@game_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    Get the global leaderboard
    """
    try:
        # Get parameters
        limit = int(request.args.get('limit', 10))

        # Get top scores from database
        top_scores = list(db.users.find(
            {'highScore': {'$exists': True}},
            {'username': 1, 'highScore': 1, 'currentLevel': 1}
        ).sort('highScore', -1).limit(limit))

        # Format results
        leaderboard = []
        for idx, user in enumerate(top_scores):
            leaderboard.append({
                'rank': idx + 1,
                'username': user.get('username', 'Anonymous'),
                'highScore': user.get('highScore', 0),
                'level': user.get('currentLevel', 1)
            })

        return jsonify({
            'success': True,
            'leaderboard': leaderboard
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch leaderboard',
            'error': str(e)
        }), 500


def generate_distractors(objects_to_find, difficulty):
    """
    Generate distractor objects that are not in the image
    """
    # List of common objects for distractors
    common_objects = [
        "toy", "teddy bear", "doll", "blocks", "book", "pencil", "ball", "backpack",
        "car", "truck", "dog", "cat", "bird", "fish", "apple", "banana", "cookie",
        "hat", "shoe", "sock", "cup", "plate", "spoon", "chair", "table", "lamp",
        "clock", "phone", "computer", "flower", "tree", "boat", "plane", "train",
        "bike", "balloon", "kite", "brush", "crayon", "robot", "dinosaur", "frog"
    ]

    # Filter out objects that are in the image
    available_distractors = [obj for obj in common_objects if not any(
        obj.lower() in target.lower() or target.lower() in obj.lower()
        for target in objects_to_find
    )]

    # Determine number of distractors based on difficulty
    num_distractors = min(difficulty + 2, len(available_distractors))
    num_distractors = min(num_distractors, 3)

    # Select random distractors
    if len(available_distractors) >= num_distractors:
        return random.sample(available_distractors, num_distractors)
    else:
        return available_distractors


import uuid
