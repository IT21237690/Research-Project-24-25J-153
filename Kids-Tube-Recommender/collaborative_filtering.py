import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
from datetime import datetime

class CollaborativeFilteringRecommender:
    def __init__(self):
        self.user_item_matrix = None
        self.similarity_matrix = None
        self.video_indices = None
        self.last_trained = None
    
    def get_recommendations(self, username, n=16, exclude_videos=None):
        """
        Get video recommendations for a user with added randomness
        
        Parameters:
        username: Username to get recommendations for
        n: Number of recommendations to return
        exclude_videos: List of video IDs to exclude from recommendations
        
        Returns:
        List of recommended video IDs
        """
        import numpy as np
        import random
        
        print(f"Getting recommendations for user: {username}, count: {n}")
        
        if self.user_item_matrix is None or self.similarity_matrix is None:
            print("Model not trained yet")
            return []
        
        if username not in self.user_item_matrix.index:
            print(f"User {username} not found in trained model")
            print(f"Available users: {self.user_item_matrix.index.tolist()}")
            return []  # User not found
        
        # Get similar users
        similar_users = self.similarity_matrix[username].sort_values(ascending=False)
        similar_users = similar_users.drop(username)  # Remove the user itself
        
        print(f"Found {len(similar_users)} similar users")
        
        if similar_users.empty:
            print("No similar users found")
            return []  # No similar users found
        
        # Get videos watched by similar users but not by the target user
        user_videos = self.user_item_matrix.loc[username]
        unwatched_videos = user_videos[user_videos == 0].index
        
        # If exclude_videos is provided, remove those videos from recommendations
        if exclude_videos and len(exclude_videos) > 0:
            unwatched_videos = [v for v in unwatched_videos if v not in exclude_videos]
        
        print(f"User has {len(unwatched_videos)} unwatched videos")
        
        if len(unwatched_videos) == 0:
            print("No unwatched videos")
            return []  # No unwatched videos
        
        # Calculate weighted scores for unwatched videos
        recommendations = {}
        
        for other_user, similarity in similar_users.items():
            if similarity <= 0:
                continue  # Skip users with non-positive similarity
            
            other_user_ratings = self.user_item_matrix.loc[other_user]
            
            # Only consider videos the other user has interacted with
            watched_by_other = other_user_ratings[other_user_ratings > 0].index
            common_videos = set(unwatched_videos) & set(watched_by_other)
            
            for video in common_videos:
                # Add extreme randomness to the score (±50%)
                random_factor = 0.5 + (np.random.random())  # Between 0.5 and 1.5
                
                # If video not in recommendations, initialize it
                if video not in recommendations:
                    recommendations[video] = 0
                    
                recommendations[video] += similarity * other_user_ratings[video] * random_factor
        
        # Always add random videos to ensure variety
        # Get all available videos from the model
        all_videos = set(self.video_indices)
        
        # Remove watched videos and already recommended videos
        available_videos = list(all_videos - set(user_videos[user_videos > 0].index) - set(recommendations.keys()))
        
        # Add random videos with small scores
        if available_videos:
            # Add at least n*2 random videos to ensure variety
            random_count = min(n * 4, len(available_videos))
            random_videos = random.sample(available_videos, random_count)
            
            for video in random_videos:
                # Small random score to prioritize collaborative filtering recommendations
                recommendations[video] = np.random.random() * 0.3
        
        # Convert to list of tuples and sort by score
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        # Get more recommendations than needed
        top_recommendations = sorted_recommendations[:n * 4]
        
        # Shuffle the top recommendations to add variety
        random.shuffle(top_recommendations)
        
        # Take the first n recommendations
        final_recommendations = [video_id for video_id, _ in top_recommendations[:n]]
        
        # Shuffle one more time for good measure
        random.shuffle(final_recommendations)
        
        print(f"Generated {len(final_recommendations)} recommendations")
        if final_recommendations:
            print(f"Sample recommendations: {final_recommendations[:3]}")
        
        return final_recommendations
    
    def prepare_data(self, user_data, video_data):
        """
        Prepare user-item interaction matrix from raw data
        
        Parameters:
        user_data: List of user watch history records
        video_data: List of video metadata
        
        Returns:
        user_item_matrix: DataFrame with users as rows, videos as columns
        """
        import pandas as pd
        
        # Create a list of interactions
        interactions = []
        
        for user in user_data:
            username = user.get('username')
            if not username:
                continue
            
            # Process watch history
            for video in user.get('watchHistory', []):
                if not video.get('videoId'):
                    continue
                    
                # Calculate a score based on watch duration and completion
                score = 1.0  # Base score for watching
                
                if video.get('completed', False):
                    score += 1.0  # Bonus for completing
                
                # Normalize watch duration (assuming videos are ~5 min)
                if video.get('watchDuration'):
                    normalized_duration = min(video['watchDuration'] / 300, 1.0)
                    score += normalized_duration
                
                interactions.append({
                    'username': username,
                    'videoId': video['videoId'],
                    'score': score
                })
            
            # Process liked videos
            for videoId in user.get('likedVideos', []):
                if not videoId:
                    continue
                    
                # Check if this video is already in interactions
                existing = next((item for item in interactions 
                                if item['username'] == username and item['videoId'] == videoId), None)
                
                if existing:
                    existing['score'] += 2.0  # Bonus for liking
                else:
                    interactions.append({
                        'username': username,
                        'videoId': videoId,
                        'score': 2.0  # Base score for liking without watching
                    })
        
        # Convert to DataFrame
        interactions_df = pd.DataFrame(interactions)
        
        if interactions_df.empty:
            print("No interactions found in the data")
            return pd.DataFrame()
        
        # Create user-item matrix
        user_item_matrix = interactions_df.pivot_table(
            index='username', 
            columns='videoId', 
            values='score', 
            fill_value=0
        )
        
        print(f"Created user-item matrix with {len(user_item_matrix.index)} users and {len(user_item_matrix.columns)} videos")
        return user_item_matrix

    def train(self, user_data, video_data):
        """
        Train the collaborative filtering model
        
        Parameters:
        user_data: List of user watch history records
        video_data: List of video metadata
        """
        print(f"Training model with {len(user_data)} users and {len(video_data)} videos")
        
        # Prepare data
        self.user_item_matrix = self.prepare_data(user_data, video_data)
        
        if self.user_item_matrix.empty:
            print("Not enough data to train the model")
            return False
        
        # Calculate user similarity matrix
        print("Calculating user similarity matrix")
        self.similarity_matrix = cosine_similarity(self.user_item_matrix)
        self.similarity_matrix = pd.DataFrame(
            self.similarity_matrix,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )
        
        print(f"Created similarity matrix with shape {self.similarity_matrix.shape}")
        
        # Store video indices for later use
        self.video_indices = self.user_item_matrix.columns
        print(f"Stored {len(self.video_indices)} video indices")
        
        # Record training time
        self.last_trained = datetime.now()
        print(f"Model trained at {self.last_trained}")
        
        return True
    
    def get_recommendations(self, username, n=5, exclude_videos=None):
        """
        Get video recommendations for a user with added randomness
        
        Parameters:
        username: Username to get recommendations for
        n: Number of recommendations to return
        exclude_videos: List of video IDs to exclude from recommendations
        
        Returns:
        List of recommended video IDs
        """
        import numpy as np
        import random
        
        print(f"Getting recommendations for user: {username}, count: {n}")
        
        if self.user_item_matrix is None or self.similarity_matrix is None:
            print("Model not trained yet")
            return []
        
        if username not in self.user_item_matrix.index:
            print(f"User {username} not found in trained model")
            print(f"Available users: {self.user_item_matrix.index.tolist()}")
            return []  # User not found
        
        # Get similar users
        similar_users = self.similarity_matrix[username].sort_values(ascending=False)
        similar_users = similar_users.drop(username)  # Remove the user itself
        
        print(f"Found {len(similar_users)} similar users")
        
        if similar_users.empty:
            print("No similar users found")
            return []  # No similar users found
        
        # Get videos watched by similar users but not by the target user
        user_videos = self.user_item_matrix.loc[username]
        unwatched_videos = user_videos[user_videos == 0].index
        
        # If exclude_videos is provided, remove those videos from recommendations
        if exclude_videos and len(exclude_videos) > 0:
            unwatched_videos = [v for v in unwatched_videos if v not in exclude_videos]
        
        print(f"User has {len(unwatched_videos)} unwatched videos")
        
        if len(unwatched_videos) == 0:
            print("No unwatched videos")
            return []  # No unwatched videos
        
        # Calculate weighted scores for unwatched videos
        recommendations = {}
        
        for other_user, similarity in similar_users.items():
            if similarity <= 0:
                continue  # Skip users with non-positive similarity
            
            other_user_ratings = self.user_item_matrix.loc[other_user]
            
            # Only consider videos the other user has interacted with
            watched_by_other = other_user_ratings[other_user_ratings > 0].index
            common_videos = set(unwatched_videos) & set(watched_by_other)
            
            for video in common_videos:
                # Add significant randomness to the score (±30%)
                random_factor = 0.7 + (np.random.random() * 0.6)  # Between 0.7 and 1.3
                
                # If video not in recommendations, initialize it
                if video not in recommendations:
                    recommendations[video] = 0
                    
                recommendations[video] += similarity * other_user_ratings[video] * random_factor
        
        # If we don't have enough recommendations from collaborative filtering
        if len(recommendations) < n * 2:
            # Add some random videos from the available pool with small scores
            remaining_videos = list(set(unwatched_videos) - set(recommendations.keys()))
            if remaining_videos:
                random_count = min(n * 3, len(remaining_videos))
                random_videos = random.sample(remaining_videos, random_count)
                for video in random_videos:
                    recommendations[video] = np.random.random() * 0.5  # Small random score
        
        # Convert to list of tuples and sort by score
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        # Get more recommendations than needed
        top_recommendations = sorted_recommendations[:n * 3]
        
        # Shuffle the top recommendations to add variety
        random.shuffle(top_recommendations)
        
        # Take the first n recommendations
        final_recommendations = [video_id for video_id, _ in top_recommendations[:n]]
        
        print(f"Generated {len(final_recommendations)} recommendations")
        if final_recommendations:
            print(f"Sample recommendations: {final_recommendations[:3]}")
        
        return final_recommendations
    
    def save_model(self, filepath='model.joblib'):
        """Save the trained model to a file"""
        if self.user_item_matrix is None:
            return False
        
        model_data = {
            'user_item_matrix': self.user_item_matrix,
            'similarity_matrix': self.similarity_matrix,
            'video_indices': self.video_indices,
            'last_trained': self.last_trained
        }
        
        joblib.dump(model_data, filepath)
        return True
    
    def load_model(self, filepath='model.joblib'):
        """Load a trained model from a file"""
        if not os.path.exists(filepath):
            return False
        
        try:
            model_data = joblib.load(filepath)
            self.user_item_matrix = model_data['user_item_matrix']
            self.similarity_matrix = model_data['similarity_matrix']
            self.video_indices = model_data['video_indices']
            self.last_trained = model_data['last_trained']
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

