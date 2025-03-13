from pymongo import MongoClient

# Update the URI and database name as needed
MONGO_URI = "mongodb+srv://dbuser:dbuser123@researchproject.ojxgd.mongodb.net/?retryWrites=true&w=majority&appName=ResearchProject"
DATABASE_NAME = "rp_db"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
results_collection = db["qa_results"]
