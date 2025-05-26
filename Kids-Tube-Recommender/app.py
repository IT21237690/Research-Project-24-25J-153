from flask import Flask, request, jsonify
import json
import os
from collaborative_filtering import CollaborativeFilteringRecommender

app = Flask(__name__)
recommender = CollaborativeFilteringRecommender()

# Try to load existing model
model_path = 'model.joblib'
if os.path.exists(model_path):
    print(f"Loading existing model from {model_path}")
    recommender.load_model(model_path)
    print(f"Model loaded: {recommender.last_trained}")
else:
    print(f"No existing model found at {model_path}")

@app.route('/train', methods=['POST'])
def train_model():
    data = request.json
    user_data = data.get('users', [])
    video_data = data.get('videos', [])
    
    print(f"Received training request with {len(user_data)} users and {len(video_data)} videos")
    
    # Print some sample data for debugging
    if user_data:
        print(f"Sample user: {user_data[0]['username']}")
        watch_history = user_data[0].get('watchHistory', [])
        print(f"Sample user has {len(watch_history)} watch history items")
        if watch_history:
            print(f"Sample watch history item: {watch_history[0]}")
    
    success = recommender.train(user_data, video_data)
    
    if success:
        recommender.save_model()
        print("Model trained and saved successfully")
        return jsonify({'status': 'success', 'message': 'Model trained successfully'})
    else:
        print("Not enough data to train model")
        return jsonify({'status': 'error', 'message': 'Not enough data to train model'})

@app.route('/recommend', methods=['GET'])
def get_recommendations():
    username = request.args.get('username')
    count = int(request.args.get('count', 5))
    exclude_videos = request.args.get('exclude', '')
    
    if not username:
        return jsonify({'status': 'error', 'message': 'Username is required'})
    
    # Parse excluded videos
    exclude_list = exclude_videos.split(',') if exclude_videos else []
    
    # Add test video IDs to always exclude
    test_videos = ['AGKPeStDipE']  # Add any test video IDs here
    exclude_list.extend(test_videos)
    
    # Get recommendations
    recommendations = recommender.get_recommendations(username, count, exclude_list)
    
    return jsonify({
        'status': 'success',
        'username': username,
        'recommendations': recommendations
    })

@app.route('/status', methods=['GET'])
def get_status():
    status = {
        'trained': recommender.user_item_matrix is not None,
        'last_trained': str(recommender.last_trained) if recommender.last_trained else None,
        'users_count': len(recommender.user_item_matrix.index) if recommender.user_item_matrix is not None else 0,
        'videos_count': len(recommender.video_indices) if recommender.video_indices is not None else 0
    }
    
    if recommender.user_item_matrix is not None:
        status['users'] = recommender.user_item_matrix.index.tolist()
    
    print(f"Status: {status}")
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)