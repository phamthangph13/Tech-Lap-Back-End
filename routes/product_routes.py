from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from bson import ObjectId
from datetime import datetime
from marshmallow import ValidationError
from database import products_collection, categories_collection
from utils.mongo_utils import format_product, save_file_to_gridfs, delete_file_from_gridfs
from schemas.product_schema import get_product_models, ProductSchema
import re
import json

# Create namespace
product_ns = Namespace('products', description='Product operations')

# Get models from schema
product_model, product_input_model, product_form_parser, product_update_model, product_update_parser = get_product_models(product_ns)

# Initialize validation schema
product_schema = ProductSchema()

# ObjectId validation regex pattern
OBJECT_ID_PATTERN = re.compile(r'^[0-9a-fA-F]{24}$')

def is_valid_object_id(id_str):
    """Check if a string is a valid ObjectId format"""
    return bool(id_str and OBJECT_ID_PATTERN.match(id_str))

@product_ns.route('/')
class ProductList(Resource):
    @product_ns.doc('list_products')
    @product_ns.response(200, 'Success', [product_model])
    def get(self):
        """List all products"""
        products = list(products_collection.find())
        return [format_product(product) for product in products]
    
    @product_ns.doc('create_product')
    @product_ns.expect(product_form_parser)
    @product_ns.response(201, 'Product created', product_model)
    @product_ns.response(400, 'Validation Error')
    def post(self):
        """Create a new product with file uploads"""
        try:
            # Get form data
            data = {}
            for key in request.form:
                if key.startswith('specs.'):
                    # Handle nested specs fields
                    if 'specs' not in data:
                        data['specs'] = {}
                    field_name = key.split('.')[1]
                    if field_name == 'ports':
                        # Handle ports as a list
                        ports_value = request.form.getlist(key)
                        data['specs']['ports'] = ports_value
                    else:
                        data['specs'][field_name] = request.form[key]
                else:
                    # Handle regular fields, converting to appropriate types
                    if key in ['price', 'discount_percent', 'stock_quantity']:
                        data[key] = int(request.form[key])
                    else:
                        data[key] = request.form[key]
            
            # Handle category_ids - convert to ObjectId if valid or empty list if none
            if 'category_ids' in request.form:
                category_ids_raw = request.form.getlist('category_ids')
                if category_ids_raw:
                    category_ids = []
                    for category_id in category_ids_raw:
                        if not category_id or not is_valid_object_id(category_id):
                            return {"message": f"Invalid category ID format: {category_id}"}, 400
                        
                        # Check if category exists
                        category = categories_collection.find_one({"_id": ObjectId(category_id)})
                        if not category:
                            return {"message": f"Category with ID {category_id} not found"}, 400
                        
                        # Store category_ids as strings to match schema validation
                        category_ids.append(str(ObjectId(category_id)))
                    
                    data['category_ids'] = category_ids
                else:
                    # Allow having no categories
                    data['category_ids'] = []
            
            # Validate input data (excluding file fields that will be handled separately)
            try:
                product_schema.load(data)
            except ValidationError as err:
                return {"message": "Validation error", "errors": err.messages}, 400
            
            # After validation, convert category_ids back to ObjectId for MongoDB
            if 'category_ids' in data and data['category_ids']:
                data['category_ids'] = [ObjectId(category_id) for category_id in data['category_ids']]
            
            # Calculate discount price
            discount_price = data['price'] - (data['price'] * data['discount_percent'] / 100)
            
            # Process file uploads
            # 1. Thumbnail (single file)
            thumbnail_file = request.files.get('thumbnail')
            if thumbnail_file:
                thumbnail_id = save_file_to_gridfs(
                    thumbnail_file.read(),
                    filename=thumbnail_file.filename,
                    content_type=thumbnail_file.content_type
                )
                data['thumbnail'] = thumbnail_id
            
            # 2. Images (multiple files)
            image_files = request.files.getlist('images')
            if image_files:
                image_ids = []
                for image_file in image_files:
                    if image_file.filename:  # Only process if a file was actually uploaded
                        image_id = save_file_to_gridfs(
                            image_file.read(),
                            filename=image_file.filename,
                            content_type=image_file.content_type
                        )
                        image_ids.append(image_id)
                if image_ids:
                    data['images'] = image_ids
            
            # 3. Videos (multiple files)
            video_files = request.files.getlist('videos')
            if video_files:
                video_ids = []
                for video_file in video_files:
                    if video_file.filename:  # Only process if a file was actually uploaded
                        video_id = save_file_to_gridfs(
                            video_file.read(),
                            filename=video_file.filename,
                            content_type=video_file.content_type
                        )
                        video_ids.append(video_id)
                if video_ids:
                    data['videos'] = video_ids
            
            # Add timestamps and discount price
            now = datetime.utcnow()
            data['created_at'] = now
            data['updated_at'] = now
            data['discount_price'] = discount_price
            
            # Insert into database
            result = products_collection.insert_one(data)
            
            # Get the created product
            created_product = products_collection.find_one({"_id": result.inserted_id})
            
            return format_product(created_product), 201
        except Exception as e:
            return {"message": f"Error creating product: {str(e)}"}, 500

@product_ns.route('/<id>')
@product_ns.param('id', 'The product identifier')
@product_ns.response(404, 'Product not found')
class Product(Resource):
    @product_ns.doc('get_product')
    @product_ns.response(200, 'Success', product_model)
    def get(self, id):
        """Get a product by ID"""
        try:
            if not is_valid_object_id(id):
                return {"message": f"Invalid product ID format: {id}"}, 400
                
            product = products_collection.find_one({"_id": ObjectId(id)})
            if not product:
                return {"message": f"Product with ID {id} not found"}, 404
            
            return format_product(product)
        except Exception as e:
            return {"message": f"Error retrieving product: {str(e)}"}, 500
    
    @product_ns.doc('update_product')
    @product_ns.expect(product_update_parser)
    @product_ns.response(200, 'Product updated', product_model)
    @product_ns.response(400, 'Validation Error')
    def put(self, id):
        """Update a product including file uploads"""
        try:
            if not is_valid_object_id(id):
                return {"message": f"Invalid product ID format: {id}"}, 400
                
            product = products_collection.find_one({"_id": ObjectId(id)})
            if not product:
                return {"message": f"Product with ID {id} not found"}, 404
            
            # Get form data
            data = {}
            for key in request.form:
                if key.startswith('specs.'):
                    # Handle nested specs fields
                    if 'specs' not in data:
                        data['specs'] = {}
                    field_name = key.split('.')[1]
                    if field_name == 'ports':
                        # Handle ports as a list
                        ports_value = request.form.getlist(key)
                        data['specs']['ports'] = ports_value
                    else:
                        data['specs'][field_name] = request.form[key]
                else:
                    # Handle regular fields, converting to appropriate types
                    if key in ['price', 'discount_percent', 'stock_quantity']:
                        data[key] = int(request.form[key])
                    else:
                        data[key] = request.form[key]
            
            # Handle category_ids - convert to string for validation, then to ObjectId for storage
            if 'category_ids' in request.form:
                category_ids_raw = request.form.getlist('category_ids')
                if category_ids_raw:
                    category_ids = []
                    for category_id in category_ids_raw:
                        if not category_id or not is_valid_object_id(category_id):
                            return {"message": f"Invalid category ID format: {category_id}"}, 400
                        
                        # Check if category exists
                        category = categories_collection.find_one({"_id": ObjectId(category_id)})
                        if not category:
                            return {"message": f"Category with ID {category_id} not found"}, 400
                        
                        # Store as string for validation
                        category_ids.append(str(ObjectId(category_id)))
                    
                    data['category_ids'] = category_ids
                else:
                    # Allow removing all categories by setting to empty array
                    data['category_ids'] = []
                    
            # Validate the update data
            if data:
                try:
                    # Use partial=True to validate only the fields that are being updated
                    product_schema.load(data, partial=True)
                except ValidationError as err:
                    return {"message": "Validation error", "errors": err.messages}, 400
                
                # After validation, convert category_ids back to ObjectId for MongoDB
                if 'category_ids' in data and data['category_ids']:
                    data['category_ids'] = [ObjectId(category_id) for category_id in data['category_ids']]
            
            # Process file uploads
            # 1. Thumbnail (single file)
            thumbnail_file = request.files.get('thumbnail')
            if thumbnail_file and thumbnail_file.filename:
                # Delete the old thumbnail if it exists
                if 'thumbnail' in product and product['thumbnail']:
                    delete_file_from_gridfs(product['thumbnail'])
                
                # Save the new thumbnail
                thumbnail_id = save_file_to_gridfs(
                    thumbnail_file.read(),
                    filename=thumbnail_file.filename,
                    content_type=thumbnail_file.content_type
                )
                data['thumbnail'] = thumbnail_id
            
            # 2. Images (multiple files)
            image_files = request.files.getlist('images')
            if image_files and any(f.filename for f in image_files):
                # Delete old images if they exist
                if 'images' in product and product['images']:
                    for old_image_id in product['images']:
                        delete_file_from_gridfs(old_image_id)
                
                # Save new images
                image_ids = []
                for image_file in image_files:
                    if image_file.filename:  # Only process if a file was actually uploaded
                        image_id = save_file_to_gridfs(
                            image_file.read(),
                            filename=image_file.filename,
                            content_type=image_file.content_type
                        )
                        image_ids.append(image_id)
                if image_ids:
                    data['images'] = image_ids
            
            # 3. Videos (multiple files)
            video_files = request.files.getlist('videos')
            if video_files and any(f.filename for f in video_files):
                # Delete old videos if they exist
                if 'videos' in product and product['videos']:
                    for old_video_id in product['videos']:
                        delete_file_from_gridfs(old_video_id)
                
                # Save new videos
                video_ids = []
                for video_file in video_files:
                    if video_file.filename:  # Only process if a file was actually uploaded
                        video_id = save_file_to_gridfs(
                            video_file.read(),
                            filename=video_file.filename,
                            content_type=video_file.content_type
                        )
                        video_ids.append(video_id)
                if video_ids:
                    data['videos'] = video_ids
            
            # Update discount price if price or discount percent changed
            if ('price' in data or 'discount_percent' in data):
                price = data.get('price', product['price'])
                discount_percent = data.get('discount_percent', product['discount_percent'])
                data['discount_price'] = price - (price * discount_percent / 100)
            
            # Update timestamp
            data['updated_at'] = datetime.utcnow()
            
            # Update product in database
            products_collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": data}
            )
            
            # Get updated product
            updated_product = products_collection.find_one({"_id": ObjectId(id)})
            
            return format_product(updated_product)
        except Exception as e:
            return {"message": f"Error updating product: {str(e)}"}, 500
    
    @product_ns.doc('delete_product')
    @product_ns.response(204, 'Product deleted')
    def delete(self, id):
        """Delete a product and its files"""
        try:
            if not is_valid_object_id(id):
                return {"message": f"Invalid product ID format: {id}"}, 400
            
            # Get the product first to retrieve file IDs
            product = products_collection.find_one({"_id": ObjectId(id)})
            if not product:
                return {"message": f"Product with ID {id} not found"}, 404
            
            # Delete associated files from GridFS
            
            # 1. Thumbnail
            if 'thumbnail' in product and product['thumbnail']:
                delete_file_from_gridfs(product['thumbnail'])
            
            # 2. Images
            if 'images' in product and product['images']:
                for image_id in product['images']:
                    delete_file_from_gridfs(image_id)
            
            # 3. Videos
            if 'videos' in product and product['videos']:
                for video_id in product['videos']:
                    delete_file_from_gridfs(video_id)
            
            # Delete the product from the collection
            result = products_collection.delete_one({"_id": ObjectId(id)})
            
            return "", 204
        except Exception as e:
            return {"message": f"Error deleting product: {str(e)}"}, 500

# Add routes for serving files
@product_ns.route('/files/<file_id>')
@product_ns.param('file_id', 'The file identifier in GridFS')
class ProductFile(Resource):
    @product_ns.doc('get_file')
    @product_ns.response(200, 'Success')
    @product_ns.response(404, 'File not found')
    def get(self, file_id):
        """Get a file from GridFS by ID"""
        from flask import send_file, abort
        from io import BytesIO
        from utils.mongo_utils import get_file_from_gridfs
        
        if not is_valid_object_id(file_id):
            return {"message": f"Invalid file ID format: {file_id}"}, 400
        
        grid_out = get_file_from_gridfs(file_id)
        if grid_out is None:
            return {"message": f"File with ID {file_id} not found"}, 404
        
        # Create a BytesIO object and send it as a file
        data = grid_out.read()
        mem = BytesIO(data)
        mem.seek(0)
        
        return send_file(
            mem,
            mimetype=grid_out.content_type,
            as_attachment=True,
            download_name=grid_out.filename
        ) 