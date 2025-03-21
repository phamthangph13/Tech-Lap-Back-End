from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB connection details from environment variables
mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
db_name = os.getenv("DB_NAME", "product_catalog")

# Connect to MongoDB
client = MongoClient(mongodb_uri)
db = client[db_name]

# Collections
products_collection = db.products
categories_collection = db.categories 