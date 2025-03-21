from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from bson import ObjectId
from datetime import datetime
from marshmallow import ValidationError
from database import products_collection, categories_collection, db
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
                    
                    # Handle ports list (or any other array within specs)
                    if field_name == 'ports':
                        data['specs']['ports'] = request.form.getlist(key)
                    else:
                        data['specs'][field_name] = request.form[key]
                elif key == 'category_ids':
                    data['category_ids'] = request.form.getlist(key)
                elif key == 'highlights':
                    data['highlights'] = request.form.getlist(key)
                elif key == 'variant_specs':
                    # Parse JSON data for variant specs
                    try:
                        data['variant_specs'] = json.loads(request.form[key])
                    except json.JSONDecodeError:
                        return {"message": "Invalid JSON format for variant_specs"}, 400
                elif key == 'colors':
                    # Parse JSON data for colors
                    try:
                        data['colors'] = json.loads(request.form[key])
                    except json.JSONDecodeError:
                        return {"message": "Invalid JSON format for colors"}, 400
                elif key == 'product_info':
                    # Parse JSON data for product info
                    try:
                        data['product_info'] = json.loads(request.form[key])
                    except json.JSONDecodeError:
                        return {"message": "Invalid JSON format for product_info"}, 400
                else:
                    data[key] = request.form[key]
            
            # Validate the data
            errors = product_schema.validate(data)
            if errors:
                return {"message": "Validation errors", "errors": errors}, 400
            
            # Store uploaded files
            data['images'] = []
            data['videos'] = []
            
            # Handle thumbnail
            if 'thumbnail' in request.files:
                thumbnail_file = request.files['thumbnail']
                if thumbnail_file.filename:
                    thumbnail_id = save_file_to_gridfs(thumbnail_file, thumbnail_file.filename, thumbnail_file.content_type)
                    data['thumbnail'] = str(thumbnail_id)
            
            # Handle individual image files
            image_count = int(data.get('image_count', 0))
            for i in range(image_count):
                image_key = f'image_{i}'
                if image_key in request.files:
                    image_file = request.files[image_key]
                    if image_file.filename:
                        image_id = save_file_to_gridfs(image_file, image_file.filename, image_file.content_type)
                        data['images'].append(str(image_id))
            
            # Handle individual video files
            video_count = int(data.get('video_count', 0))
            for i in range(video_count):
                video_key = f'video_{i}'
                if video_key in request.files:
                    video_file = request.files[video_key]
                    if video_file.filename:
                        video_id = save_file_to_gridfs(video_file, video_file.filename, video_file.content_type)
                        data['videos'].append(str(video_id))

            # Original method (keeping for backward compatibility)
            if 'images' in request.files:
                image_files = request.files.getlist('images')
                for image_file in image_files:
                    if image_file.filename:
                        image_id = save_file_to_gridfs(image_file, image_file.filename, image_file.content_type)
                        data['images'].append(str(image_id))
            
            if 'videos' in request.files:
                video_files = request.files.getlist('videos')
                for video_file in video_files:
                    if video_file.filename:
                        video_id = save_file_to_gridfs(video_file, video_file.filename, video_file.content_type)
                        data['videos'].append(str(video_id))

            # Create timestamps
            now = datetime.utcnow()
            data['created_at'] = now
            data['updated_at'] = now
            
            # Calculate discount price
            price = float(data['price'])
            discount_percent = float(data['discount_percent'])
            data['discount_price'] = price - (price * discount_percent / 100)
            
            # Insert into database
            result = products_collection.insert_one(data)
            
            # Get the created product
            created_product = products_collection.find_one({"_id": result.inserted_id})
            
            return format_product(created_product), 201
            
        except Exception as e:
            return {"message": f"Error creating product: {str(e)}"}, 400
    
    
@product_ns.route('/<id>')
@product_ns.param('id', 'The product identifier')
@product_ns.response(404, 'Product not found')
class Product(Resource):
    @product_ns.doc('get_product')
    @product_ns.response(200, 'Success', product_model)
    def get(self, id):
        """Get a product by ID"""
        if not is_valid_object_id(id):
            return {"message": "Invalid product ID format"}, 400
            
        product = products_collection.find_one({"_id": ObjectId(id)})
        if not product:
            return {"message": "Product not found"}, 404
            
        return format_product(product)
    
    @product_ns.doc('update_product')
    @product_ns.expect(product_update_parser)
    @product_ns.response(200, 'Product updated', product_model)
    @product_ns.response(400, 'Validation Error')
    def put(self, id):
        """Update a product with file uploads"""
        if not is_valid_object_id(id):
            return {"message": "Invalid product ID format"}, 400
            
        # Check if product exists
        product = products_collection.find_one({"_id": ObjectId(id)})
        if not product:
            return {"message": "Product not found"}, 404
            
        try:
            # Get existing product data
            update_data = {}
            
            # Process form data
            for key in request.form:
                if key.startswith('specs.'):
                    # Handle nested specs fields
                    if 'specs' not in update_data:
                        update_data['specs'] = {}
                    field_name = key.split('.')[1]
                    
                    # Handle ports list (or any other array within specs)
                    if field_name == 'ports':
                        update_data['specs']['ports'] = request.form.getlist(key)
                    else:
                        update_data['specs'][field_name] = request.form[key]
                elif key == 'category_ids':
                    update_data['category_ids'] = request.form.getlist(key)
                elif key == 'highlights':
                    update_data['highlights'] = request.form.getlist(key)
                elif key == 'variant_specs':
                    # Parse JSON data for variant specs
                    try:
                        update_data['variant_specs'] = json.loads(request.form[key])
                    except json.JSONDecodeError:
                        return {"message": "Invalid JSON format for variant_specs"}, 400
                elif key == 'colors':
                    # Parse JSON data for colors
                    try:
                        update_data['colors'] = json.loads(request.form[key])
                    except json.JSONDecodeError:
                        return {"message": "Invalid JSON format for colors"}, 400
                elif key == 'product_info':
                    # Parse JSON data for product info
                    try:
                        update_data['product_info'] = json.loads(request.form[key])
                    except json.JSONDecodeError:
                        return {"message": "Invalid JSON format for product_info"}, 400
                else:
                    update_data[key] = request.form[key]
            
            # If we got price or discount_percent updates, recalculate discount_price
            if 'price' in update_data or 'discount_percent' in update_data:
                price = float(update_data.get('price', product.get('price', 0)))
                discount_percent = float(update_data.get('discount_percent', product.get('discount_percent', 0)))
                update_data['discount_price'] = price - (price * discount_percent / 100)
            
            # Handle file uploads
            # Thumbnail
            if 'thumbnail' in request.files:
                thumbnail_file = request.files['thumbnail']
                if thumbnail_file.filename:
                    # Delete old thumbnail if exists
                    old_thumbnail_id = product.get('thumbnail')
                    if old_thumbnail_id:
                        delete_file_from_gridfs(ObjectId(old_thumbnail_id))
                    
                    # Save new thumbnail
                    thumbnail_id = save_file_to_gridfs(thumbnail_file, thumbnail_file.filename, thumbnail_file.content_type)
                    update_data['thumbnail'] = str(thumbnail_id)
            
            # Images - individual files
            image_count = int(update_data.get('image_count', 0))
            if image_count > 0:
                # Delete old images
                for old_image_id in product.get('images', []):
                    delete_file_from_gridfs(ObjectId(old_image_id))
                
                # Save new images
                new_images = []
                for i in range(image_count):
                    image_key = f'image_{i}'
                    if image_key in request.files:
                        image_file = request.files[image_key]
                        if image_file.filename:
                            image_id = save_file_to_gridfs(image_file, image_file.filename, image_file.content_type)
                            new_images.append(str(image_id))
                
                update_data['images'] = new_images
            
            # Videos - individual files
            video_count = int(update_data.get('video_count', 0))
            if video_count > 0:
                # Delete old videos
                for old_video_id in product.get('videos', []):
                    delete_file_from_gridfs(ObjectId(old_video_id))
                
                # Save new videos
                new_videos = []
                for i in range(video_count):
                    video_key = f'video_{i}'
                    if video_key in request.files:
                        video_file = request.files[video_key]
                        if video_file.filename:
                            video_id = save_file_to_gridfs(video_file, video_file.filename, video_file.content_type)
                            new_videos.append(str(video_id))
                
                update_data['videos'] = new_videos
            
            # Original methods (keeping for backward compatibility)
            # Images
            if 'images' in request.files:
                image_files = request.files.getlist('images')
                if image_files and image_files[0].filename:
                    # If there are valid image files, we'll replace all images
                    # Delete old images
                    for old_image_id in product.get('images', []):
                        delete_file_from_gridfs(ObjectId(old_image_id))
                    
                    # Save new images
                    new_images = []
                    for image_file in image_files:
                        if image_file.filename:
                            image_id = save_file_to_gridfs(image_file, image_file.filename, image_file.content_type)
                            new_images.append(str(image_id))
                    
                    update_data['images'] = new_images
            
            # Videos
            if 'videos' in request.files:
                video_files = request.files.getlist('videos')
                if video_files and video_files[0].filename:
                    # If there are valid video files, we'll replace all videos
                    # Delete old videos
                    for old_video_id in product.get('videos', []):
                        delete_file_from_gridfs(ObjectId(old_video_id))
                    
                    # Save new videos
                    new_videos = []
                    for video_file in video_files:
                        if video_file.filename:
                            video_id = save_file_to_gridfs(video_file, video_file.filename, video_file.content_type)
                            new_videos.append(str(video_id))
                    
                    update_data['videos'] = new_videos
            
            # Set updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            # Update in database
            products_collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": update_data}
            )
            
            # Get the updated product
            updated_product = products_collection.find_one({"_id": ObjectId(id)})
            
            return format_product(updated_product)
            
        except Exception as e:
            return {"message": f"Error updating product: {str(e)}"}, 400
    
    @product_ns.doc('delete_product')
    @product_ns.response(204, 'Product deleted')
    def delete(self, id):
        """Delete a product"""
        if not is_valid_object_id(id):
            return {"message": "Invalid product ID format"}, 400
            
        # Get product to delete its files
        product = products_collection.find_one({"_id": ObjectId(id)})
        if not product:
            return {"message": "Product not found"}, 404
        
        # Delete all associated files (thumbnail, images, videos)
        # Thumbnail
        if 'thumbnail' in product and product['thumbnail']:
            delete_file_from_gridfs(ObjectId(product['thumbnail']))
        
        # Images - individual files
        image_count = int(product.get('image_count', 0))
        for i in range(image_count):
            image_key = f'image_{i}'
            if image_key in product:
                delete_file_from_gridfs(ObjectId(product[image_key]))
        
        # Videos - individual files
        video_count = int(product.get('video_count', 0))
        for i in range(video_count):
            video_key = f'video_{i}'
            if video_key in product:
                delete_file_from_gridfs(ObjectId(product[video_key]))
        
        # Delete product
        products_collection.delete_one({"_id": ObjectId(id)})
        
        return "", 204

@product_ns.route('/files/<file_id>')
@product_ns.param('file_id', 'The file identifier in GridFS')
class ProductFile(Resource):
    @product_ns.doc('get_file')
    @product_ns.response(200, 'Success')
    @product_ns.response(404, 'File not found')
    def get(self, file_id):
        """Get a product file (image/video) by ID"""
        from flask import send_file
        from gridfs import GridFS
        from io import BytesIO
        from database import db
        
        # Use the existing database connection
        fs = GridFS(db)
        
        print(f"GET request for file: {file_id}, DB name: {db.name}")
        
        if not is_valid_object_id(file_id):
            print(f"Invalid file ID format: {file_id}")
            return {"message": "Invalid file ID format"}, 400
        
        try:
            # Check if file exists first
            if not fs.exists(ObjectId(file_id)):
                print(f"File does not exist: {file_id}")
                return {"message": "File not found"}, 404
                
            # Get file by ObjectId
            file_data = fs.get(ObjectId(file_id))
            print(f"File found: {file_id}, name: {file_data.filename}, content-type: {file_data.content_type}")
            
            # Create BytesIO object
            file_obj = BytesIO(file_data.read())
            
            # Get content type
            content_type = file_data.content_type or 'application/octet-stream'
            
            # Send file
            return send_file(
                file_obj,
                mimetype=content_type,
                as_attachment=False,
                download_name=file_data.filename
            )
        except Exception as e:
            print(f"Error fetching file {file_id}: {str(e)}")
            return {"message": f"Error fetching file: {str(e)}"}, 404
            
    @product_ns.doc('head_file')
    @product_ns.response(200, 'File exists')
    @product_ns.response(404, 'File not found')
    def head(self, file_id):
        """Check if a file exists and get its metadata"""
        from flask import Response
        from gridfs import GridFS
        from database import db
        
        # Use the existing database connection
        fs = GridFS(db)
        
        print(f"HEAD request for file: {file_id}, DB name: {db.name}")
        
        if not is_valid_object_id(file_id):
            print(f"Invalid file ID format: {file_id}")
            return Response(status=400)
        
        try:
            # Check if file exists
            if not fs.exists(ObjectId(file_id)):
                print(f"File does not exist: {file_id}")
                return Response(status=404)
                
            # Get file metadata
            file_data = fs.get(ObjectId(file_id))
            print(f"File found: {file_id}, name: {file_data.filename}, content-type: {file_data.content_type}, length: {file_data.length}")
            
            # Create response with appropriate headers
            response = Response(status=200)
            response.headers['Content-Type'] = file_data.content_type or 'application/octet-stream'
            response.headers['Content-Length'] = str(file_data.length)
            if file_data.filename:
                response.headers['Content-Disposition'] = f'inline; filename="{file_data.filename}"'
            
            return response
        except Exception as e:
            print(f"Error checking file {file_id}: {str(e)}")
            return Response(status=404) 