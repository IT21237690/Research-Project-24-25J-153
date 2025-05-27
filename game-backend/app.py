from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import pymongo
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Import services
from services.image_generator import ImageGenerator

app = Flask(__name__)
CORS(app)
# Configure app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize JWT
jwt = JWTManager(app)

# Connect to MongoDB
mongo_uri = os.environ.get('MONGO_URI', 'mongodb+srv://dbuser:dbuser123@researchproject.ojxgd.mongodb.net/object_recognition_game?retryWrites=true&w=majority&appName=ResearchProject')
client = pymongo.MongoClient(mongo_uri)
db = client.get_database()

# Initialize image generator
image_generator = ImageGenerator()

# Routes
from routes.auth import auth_bp
from routes.game import game_bp 
from routes.images import images_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(game_bp, url_prefix='/api/game')
app.register_blueprint(images_bp, url_prefix='/api/images')


@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok", "message": "Server is running"})


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
