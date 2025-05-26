import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-for-development')
    DEBUG = False
    TESTING = False

    # MongoDB settings
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/object_recognition_game')

    # API keys
    STABILITY_API_KEY = os.getenv('STABILITY_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    # File storage
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    GENERATED_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'generated')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    # Game settings
    MAX_DISTRACTORS = 6  # Maximum number of distractor objects to include in options
    MIN_DISTRACTORS = 2  # Minimum number of distractor objects
    TIME_LIMIT_BASE = 30  # Base time limit in seconds

    # Ensure directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(GENERATED_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    MONGO_URI = os.getenv('TEST_MONGO_URI', 'mongodb://localhost:27017/test_object_recognition_game')


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

    # In production, ensure all sensitive keys are set via environment variables

    def __init__(self):
        if not os.getenv('SECRET_KEY'):
            raise ValueError("SECRET_KEY environment variable must be set in production")

        if not os.getenv('MONGO_URI'):
            raise ValueError("MONGO_URI environment variable must be set in production")


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}


# Default to development if not specified
def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)


def get_theme():
    return {
        "easy": ["Apple", "Baby", "Ball", "Balloon", "Banana", "Basket", "Bear", "Bench", "Bicycle", "Bird", "Book",
                 "Bottle", "Bow tie", "Bowl", "Box", "Boy", "Bubble", "Bucket", "Bug", "Butterfly", "Cactus", "Cap",
                 "Carrot", "Cart", "Cat", "Chair", "Chef", "Clouds", "Cupcake", "Dog", "Donut", "Duck", "Elephant",
                 "Fish", "Flamingo", "Flower", "Fox", "Frog", "Giraffe", "Girl", "Guitar", "Hat", "Hut", "Ice cream",
                 "Kids", "Kite", "Ladybird", "Lion cub", "Lizard", "Magic wand", "Man", "Monkey", "Moon", "Motor bike",
                 "Mug", "Mushroom", "Newspaper", "Octopus", "Owl", "Panda", "Parrot", "Penguin", "Pig", "Pigeon",
                 "Pillow", "Pizza", "Pond", "Popsicle", "Porcupine", "Pot", "Rabbit", "Raccoon", "Radio", "Rainbow",
                 "River", "Robot", "Rock", "Scarf", "Sea", "Sea shell", "Skateboard", "Slide", "Sloth", "Snail",
                 "Snowman", "Squirrel", "Star", "Stream", "Sun", "Sunflower", "Sunglasses", "Swing", "Teapot", "Tomato",
                 "Tortoise", "Trampoline", "Tree", "Trunk", "Umbrella", "Unicycle", "Van", "Water", "Watermelon",
                 "Window"],
        "medium": ["Accordion", "Acorn", "Air balloon", "Angel", "Ant", "Astronaut", "Avocado", "Bamboo tree", "Bee",
                   "Binoculars", "Blueberry", "Book shelf", "Bread", "Bridge", "Bun", "Bush", "Cake", "Canvas", "Car",
                   "Ceiling", "Cheese", "Clock", "Clown", "Coin", "Couch", "Cow", "Crab", "Crocodile", "Crown", "Cup",
                   "Diamond", "Disco ball", "Dish", "Dolphin", "Door", "Dragonfly", "Drone", "Drum", "Fish tank",
                   "Flag", "Floor", "Flower bouquet", "Flower vase", "Hammock", "Hands scope", "Headphone", "Heart",
                   "Hippopotamus", "Horse", "Ice", "Jellyfish", "Juice", "Kangaroo", "Koala", "Lemon", "Lily pad",
                   "Lion", "Mailbox", "Map", "Microphone", "Mouse", "Necklace", "Orange", "Oven", "Paint brush",
                   "Pancake", "Paper", "Peacock", "Pedestrian crossing", "Pencil", "Photo frame", "Pineapple", "Planet",
                   "Pool", "Popcorn bucket", "Porsche", "Pumpkin", "Road", "Safe", "Sandwich", "Saxophone", "Scooter",
                   "Seahorse", "Seal", "Shark", "Sheep", "Ship", "Shoe", "Speaker", "Starfish", "Stick", "Stone",
                   "Strawberry", "Street lamp", "Sunflower", "Surfboard", "Swan", "Table", "Television", "Tiger",
                   "Toaster", "Truck", "Turtle", "Unicorn", "Wall", "Water outlet", "Waterfall", "Whale", "Wheel",
                   "Witch", "Women", "Wool ball", "Zebra"],
        "hard": ["Cherry blossoms", "Coconut tree", "Cook", "Corals", "Daisy flowers", "Dinosaur", "Dragon", "Fence",
                 "Floor mat", "Flower pot", "Magnifying glass", "Mat", "Mobile phone", "Road Sign", "Sand castle",
                 "Space ship", "Stone path", "Suitcase", "Trees"]
    }
