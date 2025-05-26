from pymongo import MongoClient
from datetime import datetime

# Global database connection
mongo_client = None
db = None


def init_db(app):
    """Initialize MongoDB connection"""
    global mongo_client, db

    mongo_client = MongoClient(app.config['MONGO_URI'])
    db = mongo_client.get_database()

    # Create indexes if needed
    db.users.create_index('user_id', unique=True)

    return db


def get_user(user_id):
    """Get user data by user ID"""
    if not db:
        raise Exception("Database not initialized")

    user = db.users.find_one({'user_id': user_id})

    # Convert ObjectId to string for JSON serialization
    if user and '_id' in user:
        user['_id'] = str(user['_id'])

    return user


def create_user(user_data):
    """Create a new user"""
    if not db:
        raise Exception("Database not initialized")

    # Ensure timestamp fields are datetime objects
    if 'created_at' not in user_data:
        user_data['created_at'] = datetime.utcnow()
    if 'last_active' not in user_data:
        user_data['last_active'] = datetime.utcnow()

    result = db.users.insert_one(user_data)
    return str(result.inserted_id)


def update_user(user_id, update_data):
    """Update user data"""
    if not db:
        raise Exception("Database not initialized")

    result = db.users.update_one(
        {'user_id': user_id},
        {'$set': update_data}
    )

    return result.modified_count > 0


def get_leaderboard(limit=10):
    """Get top users by score"""
    if not db:
        raise Exception("Database not initialized")

    leaderboard = list(db.users.find(
        {},
        {'_id': 0, 'user_id': 1, 'score': 1, 'level': 1}
    ).sort('score', -1).limit(limit))

    return leaderboard