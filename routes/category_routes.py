from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from bson import ObjectId
from datetime import datetime
from marshmallow import ValidationError
from database import categories_collection
from schemas.category_schema import get_category_models, CategorySchema
import re

# Create namespace
category_ns = Namespace('categories', description='Category operations')

# Get models from schema
category_model, category_input_model, category_form_parser, category_update_model, category_update_parser = get_category_models(category_ns)

# Initialize validation schema
category_schema = CategorySchema()

# ObjectId validation regex pattern
OBJECT_ID_PATTERN = re.compile(r'^[0-9a-fA-F]{24}$')

def is_valid_object_id(id_str):
    """Check if a string is a valid ObjectId format"""
    return bool(id_str and OBJECT_ID_PATTERN.match(id_str))

# Helper function for category formatting
def format_category(category):
    """Format a category document for API response."""
    if not category:
        return None
    
    if '_id' in category:
        category['_id'] = str(category['_id'])
    
    if 'created_at' in category:
        category['created_at'] = category['created_at'].isoformat() if isinstance(category['created_at'], datetime) else category['created_at']
    
    if 'updated_at' in category:
        category['updated_at'] = category['updated_at'].isoformat() if isinstance(category['updated_at'], datetime) else category['updated_at']
    
    return category

@category_ns.route('/')
class CategoryList(Resource):
    @category_ns.doc('list_categories')
    @category_ns.response(200, 'Success', [category_model])
    def get(self):
        """List all categories"""
        categories = list(categories_collection.find())
        return jsonify([format_category(category) for category in categories])
    
    @category_ns.doc('create_category')
    @category_ns.expect(category_form_parser)
    @category_ns.response(201, 'Category created', category_model)
    @category_ns.response(400, 'Validation Error')
    def post(self):
        """Create a new category"""
        try:
            # Get form data
            data = {
                'name': request.form.get('name')
            }
            
            # Only add description if it's provided and not empty
            description = request.form.get('description')
            if description is not None and description.strip():
                data['description'] = description
            
            # Validate input data
            try:
                category_schema.load(data)
            except ValidationError as err:
                return {"message": "Validation error", "errors": err.messages}, 400
            
            # Add timestamps
            now = datetime.utcnow()
            data['created_at'] = now
            data['updated_at'] = now
            
            # Insert into database
            result = categories_collection.insert_one(data)
            
            # Get the created category
            created_category = categories_collection.find_one({"_id": result.inserted_id})
            
            return format_category(created_category), 201
        except Exception as e:
            return {"message": f"Error creating category: {str(e)}"}, 500

@category_ns.route('/<id>')
@category_ns.param('id', 'The category identifier')
@category_ns.response(404, 'Category not found')
class Category(Resource):
    @category_ns.doc('get_category')
    @category_ns.response(200, 'Success', category_model)
    def get(self, id):
        """Get a category by ID"""
        try:
            if not is_valid_object_id(id):
                return {"message": f"Invalid category ID format: {id}"}, 400
                
            category = categories_collection.find_one({"_id": ObjectId(id)})
            if not category:
                return {"message": f"Category with ID {id} not found"}, 404
            
            return format_category(category)
        except Exception as e:
            return {"message": f"Error retrieving category: {str(e)}"}, 500
    
    @category_ns.doc('update_category')
    @category_ns.expect(category_update_parser)
    @category_ns.response(200, 'Category updated', category_model)
    @category_ns.response(400, 'Validation Error')
    def put(self, id):
        """Update a category"""
        try:
            if not is_valid_object_id(id):
                return {"message": f"Invalid category ID format: {id}"}, 400
                
            category = categories_collection.find_one({"_id": ObjectId(id)})
            if not category:
                return {"message": f"Category with ID {id} not found"}, 404
            
            # Get form data
            data = {}
            if 'name' in request.form and request.form.get('name').strip():
                data['name'] = request.form.get('name')
            
            # Handle description - allow explicitly setting to null/empty
            if 'description' in request.form:
                description = request.form.get('description')
                if description is not None and description.strip():
                    data['description'] = description
                else:
                    data['description'] = None
            
            # Update timestamp
            data['updated_at'] = datetime.utcnow()
            
            # Update category in database
            categories_collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": data}
            )
            
            # Get updated category
            updated_category = categories_collection.find_one({"_id": ObjectId(id)})
            
            return format_category(updated_category)
        except Exception as e:
            return {"message": f"Error updating category: {str(e)}"}, 500
    
    @category_ns.doc('delete_category')
    @category_ns.response(204, 'Category deleted')
    def delete(self, id):
        """Delete a category"""
        try:
            if not is_valid_object_id(id):
                return {"message": f"Invalid category ID format: {id}"}, 400
            
            # Check if category exists
            category = categories_collection.find_one({"_id": ObjectId(id)})
            if not category:
                return {"message": f"Category with ID {id} not found"}, 404
            
            # Delete the category from the collection
            categories_collection.delete_one({"_id": ObjectId(id)})
            
            return "", 204
        except Exception as e:
            return {"message": f"Error deleting category: {str(e)}"}, 500 