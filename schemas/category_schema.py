from flask_restx import fields
from marshmallow import Schema, fields as ma_fields, validate, EXCLUDE

# Swagger model schemas
def get_category_models(api):
    # Category model
    category_model = api.model('Category', {
        '_id': fields.String(description='Category ID'),
        'name': fields.String(required=True, description='Category name', example='Laptops'),
        'description': fields.String(description='Category description', example='All laptop products', required=False),
        'created_at': fields.DateTime(description='Creation timestamp'),
        'updated_at': fields.DateTime(description='Last update timestamp')
    })
    
    # For category creation
    category_input_model = api.model('CategoryInput', {
        'name': fields.String(required=True, description='Category name', example='Laptops'),
        'description': fields.String(description='Category description', example='All laptop products', required=False)
    })
    
    # Form parser (no file upload needed anymore)
    category_form_parser = api.parser()
    category_form_parser.add_argument('name', location='form', required=True, help='Category name')
    category_form_parser.add_argument('description', location='form', required=False, help='Category description')
    
    # For category updates
    category_update_model = api.model('CategoryUpdate', {
        'name': fields.String(description='Category name'),
        'description': fields.String(description='Category description', required=False)
    })
    
    # Update parser
    category_update_parser = api.parser()
    category_update_parser.add_argument('name', location='form', required=False, help='Category name')
    category_update_parser.add_argument('description', location='form', required=False, help='Category description')
    
    return category_model, category_input_model, category_form_parser, category_update_model, category_update_parser

# Marshmallow schema for validation
class CategorySchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields
    
    name = ma_fields.String(required=True)
    description = ma_fields.String(required=False, allow_none=True) 