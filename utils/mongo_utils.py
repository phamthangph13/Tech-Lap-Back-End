from bson import ObjectId
from datetime import datetime
from flask import jsonify
from gridfs import GridFS
from database import db
import json

# Initialize GridFS
fs = GridFS(db)

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(MongoJSONEncoder, self).default(obj)

def object_id_to_str(obj_id):
    """Convert ObjectId to string if it's an ObjectId, otherwise return as is."""
    if isinstance(obj_id, ObjectId):
        return str(obj_id)
    return obj_id

def str_to_object_id(id_str):
    """Convert string to ObjectId if it's a valid ObjectId string, otherwise return as is."""
    try:
        if isinstance(id_str, str):
            return ObjectId(id_str)
        return id_str
    except:
        return id_str

def parse_json(data):
    """Convert MongoDB data types to JSON-serializable types."""
    for key, value in data.items():
        if isinstance(value, ObjectId):
            data[key] = str(value)
        elif isinstance(value, datetime):
            data[key] = value.isoformat()
        elif isinstance(value, dict):
            data[key] = parse_json(value)
        elif isinstance(value, list):
            data[key] = [parse_json(item) if isinstance(item, dict) else 
                         str(item) if isinstance(item, ObjectId) else 
                         item.isoformat() if isinstance(item, datetime) else item 
                         for item in value]
    return data

def format_product(product):
    """Format a product document for API response."""
    if not product:
        return None
    
    if '_id' in product:
        product['_id'] = str(product['_id'])
    
    if 'category_id' in product and product['category_id']:
        product['category_id'] = str(product['category_id'])
    
    # Handle category_ids array
    if 'category_ids' in product and product['category_ids']:
        product['category_ids'] = [str(cat_id) if isinstance(cat_id, ObjectId) else cat_id 
                                   for cat_id in product['category_ids']]
    
    if 'thumbnail' in product and product['thumbnail']:
        product['thumbnail'] = str(product['thumbnail'])
    
    if 'images' in product and product['images']:
        product['images'] = [str(img_id) for img_id in product['images']]
    
    if 'videos' in product and product['videos']:
        product['videos'] = [str(vid_id) for vid_id in product['videos']]
    
    if 'created_at' in product:
        product['created_at'] = product['created_at'].isoformat() if isinstance(product['created_at'], datetime) else product['created_at']
    
    if 'updated_at' in product:
        product['updated_at'] = product['updated_at'].isoformat() if isinstance(product['updated_at'], datetime) else product['updated_at']
    
    return product

def save_file_to_gridfs(file_data, filename, content_type):
    """Save a file to GridFS and return the file ID"""
    file_id = fs.put(
        file_data,
        filename=filename,
        content_type=content_type
    )
    return file_id

def get_file_from_gridfs(file_id):
    """Retrieve a file from GridFS by its ID"""
    if not file_id:
        return None
    
    try:
        file_id_obj = ObjectId(file_id) if isinstance(file_id, str) else file_id
        grid_out = fs.get(file_id_obj)
        return grid_out
    except Exception as e:
        print(f"Error retrieving file from GridFS: {str(e)}")
        return None

def delete_file_from_gridfs(file_id):
    """Delete a file from GridFS by its ID"""
    if not file_id:
        return False
    
    try:
        file_id_obj = ObjectId(file_id) if isinstance(file_id, str) else file_id
        fs.delete(file_id_obj)
        return True
    except Exception as e:
        print(f"Error deleting file from GridFS: {str(e)}")
        return False 