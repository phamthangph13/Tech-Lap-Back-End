from flask_restx import fields
from marshmallow import Schema, fields as ma_fields, validate, EXCLUDE
from werkzeug.datastructures import FileStorage

# Swagger model schemas
def get_product_models(api):
    # Define file upload field for Swagger
    upload = api.parser()
    upload.add_argument('file', 
                        location='files',
                        type=FileStorage, 
                        required=True, 
                        help='File to upload')
    
    specs_model = api.model('Specs', {
        'cpu': fields.String(required=True, description='CPU model', example='Intel Core i7-13700H'),
        'ram': fields.String(required=True, description='RAM configuration', example='16GB DDR5'),
        'storage': fields.String(required=True, description='Storage configuration', example='512GB NVMe SSD'),
        'display': fields.String(required=True, description='Display specifications', example='15.6 inch 4K OLED'),
        'gpu': fields.String(required=True, description='GPU model', example='NVIDIA RTX 4060 6GB'),
        'battery': fields.String(required=True, description='Battery capacity', example='86Wh'),
        'os': fields.String(required=True, description='Operating system', example='Windows 11 Pro'),
        'ports': fields.List(fields.String, required=True, description='Available ports', example=['USB-C', 'HDMI', '3.5mm Audio'])
    })
    
    product_model = api.model('Product', {
        '_id': fields.String(description='Product ID'),
        'name': fields.String(required=True, description='Product name', example='Laptop Dell XPS 15'),
        'brand': fields.String(required=True, description='Brand name', example='Dell'),
        'model': fields.String(required=True, description='Model number', example='XPS 15 9530'),
        'price': fields.Integer(required=True, description='Original price', example=35000000),
        'discount_percent': fields.Integer(required=True, description='Discount percentage', example=10),
        'discount_price': fields.Integer(description='Price after discount', example=31500000),
        'specs': fields.Nested(specs_model, required=True, description='Product specifications'),
        'stock_quantity': fields.Integer(required=True, description='Available stock', example=50),
        'category_ids': fields.List(fields.String, description='Category IDs', example=['6600a1c3b6f4a2d4e8f3b130'], required=False),
        'thumbnail': fields.String(description='Thumbnail file ID', required=False),
        'images': fields.List(fields.String, description='Image file IDs', required=False),
        'videos': fields.List(fields.String, description='Video file IDs', required=False),
        'created_at': fields.DateTime(description='Creation timestamp'),
        'updated_at': fields.DateTime(description='Last update timestamp'),
        'status': fields.String(description='Product status', enum=['available', 'sold_out', 'discontinued'], example='available', required=False)
    })
    
    # For product creation, we'll use form data instead of JSON
    product_input_model = api.model('ProductInput', {
        'name': fields.String(required=True, description='Product name', example='Laptop Dell XPS 15'),
        'brand': fields.String(required=True, description='Brand name', example='Dell'),
        'model': fields.String(required=True, description='Model number', example='XPS 15 9530'),
        'price': fields.Integer(required=True, description='Original price', example=35000000),
        'discount_percent': fields.Integer(required=True, description='Discount percentage', example=10),
        'specs.cpu': fields.String(required=True, description='CPU model', example='Intel Core i7-13700H'),
        'specs.ram': fields.String(required=True, description='RAM configuration', example='16GB DDR5'),
        'specs.storage': fields.String(required=True, description='Storage configuration', example='512GB NVMe SSD'),
        'specs.display': fields.String(required=True, description='Display specifications', example='15.6 inch 4K OLED'),
        'specs.gpu': fields.String(required=True, description='GPU model', example='NVIDIA RTX 4060 6GB'),
        'specs.battery': fields.String(required=True, description='Battery capacity', example='86Wh'),
        'specs.os': fields.String(required=True, description='Operating system', example='Windows 11 Pro'),
        'specs.ports': fields.List(fields.String, required=True, description='Available ports', example=['USB-C', 'HDMI', '3.5mm Audio']),
        'stock_quantity': fields.Integer(required=True, description='Available stock', example=50),
        'category_ids': fields.List(fields.String, description='Category IDs', example=['6600a1c3b6f4a2d4e8f3b130'], required=False),
        'status': fields.String(description='Product status', enum=['available', 'sold_out', 'discontinued'], example='available', required=False)
    })
    
    # Create file upload parsers
    thumbnail_upload = api.parser()
    thumbnail_upload.add_argument('thumbnail', 
                                location='files',
                                type=FileStorage, 
                                required=False, 
                                help='Thumbnail image file')
    
    images_upload = api.parser()
    images_upload.add_argument('images', 
                              location='files',
                              type=FileStorage, 
                              required=False, 
                              action='append',
                              help='Product image files (multiple allowed)')
    
    videos_upload = api.parser()
    videos_upload.add_argument('videos', 
                              location='files',
                              type=FileStorage, 
                              required=False, 
                              action='append',
                              help='Product video files (multiple allowed)')
    
    # Combine all parsers
    product_form_parser = api.parser()
    product_form_parser.add_argument('name', location='form', required=True, help='Product name')
    product_form_parser.add_argument('brand', location='form', required=True, help='Brand name')
    product_form_parser.add_argument('model', location='form', required=True, help='Model number')
    product_form_parser.add_argument('price', location='form', type=int, required=True, help='Original price')
    product_form_parser.add_argument('discount_percent', location='form', type=int, required=True, help='Discount percentage (0-100)')
    product_form_parser.add_argument('specs.cpu', location='form', required=True, help='CPU model')
    product_form_parser.add_argument('specs.ram', location='form', required=True, help='RAM configuration')
    product_form_parser.add_argument('specs.storage', location='form', required=True, help='Storage configuration')
    product_form_parser.add_argument('specs.display', location='form', required=True, help='Display specifications')
    product_form_parser.add_argument('specs.gpu', location='form', required=True, help='GPU model')
    product_form_parser.add_argument('specs.battery', location='form', required=True, help='Battery capacity')
    product_form_parser.add_argument('specs.os', location='form', required=True, help='Operating system')
    product_form_parser.add_argument('specs.ports', location='form', required=True, action='append', help='Available ports (can specify multiple times)')
    product_form_parser.add_argument('stock_quantity', location='form', type=int, required=True, help='Available stock')
    product_form_parser.add_argument('category_ids', location='form', required=False, action='append', help='Category IDs (can specify multiple times)')
    product_form_parser.add_argument('status', location='form', required=False, help='Product status (available, sold_out, discontinued)')
    product_form_parser.add_argument('thumbnail', location='files', type=FileStorage, required=False, help='Thumbnail image file')
    product_form_parser.add_argument('images', location='files', type=FileStorage, required=False, action='append', help='Product image files')
    product_form_parser.add_argument('videos', location='files', type=FileStorage, required=False, action='append', help='Product video files')
    
    # For product updates
    product_update_model = api.model('ProductUpdate', {
        'name': fields.String(description='Product name'),
        'brand': fields.String(description='Brand name'),
        'model': fields.String(description='Model number'),
        'price': fields.Integer(description='Original price'),
        'discount_percent': fields.Integer(description='Discount percentage'),
        'specs': fields.Nested(specs_model, description='Product specifications'),
        'stock_quantity': fields.Integer(description='Available stock'),
        'category_ids': fields.List(fields.String, description='Category IDs'),
        'status': fields.String(description='Product status', enum=['available', 'sold_out', 'discontinued'])
    })
    
    # Update parser is similar to form parser but all fields are optional
    product_update_parser = api.parser()
    product_update_parser.add_argument('name', location='form', required=False, help='Product name')
    product_update_parser.add_argument('brand', location='form', required=False, help='Brand name')
    product_update_parser.add_argument('model', location='form', required=False, help='Model number')
    product_update_parser.add_argument('price', location='form', type=int, required=False, help='Original price')
    product_update_parser.add_argument('discount_percent', location='form', type=int, required=False, help='Discount percentage (0-100)')
    product_update_parser.add_argument('specs.cpu', location='form', required=False, help='CPU model')
    product_update_parser.add_argument('specs.ram', location='form', required=False, help='RAM configuration')
    product_update_parser.add_argument('specs.storage', location='form', required=False, help='Storage configuration')
    product_update_parser.add_argument('specs.display', location='form', required=False, help='Display specifications')
    product_update_parser.add_argument('specs.gpu', location='form', required=False, help='GPU model')
    product_update_parser.add_argument('specs.battery', location='form', required=False, help='Battery capacity')
    product_update_parser.add_argument('specs.os', location='form', required=False, help='Operating system')
    product_update_parser.add_argument('specs.ports', location='form', required=False, action='append', help='Available ports (can specify multiple times)')
    product_update_parser.add_argument('stock_quantity', location='form', type=int, required=False, help='Available stock')
    product_update_parser.add_argument('category_ids', location='form', required=False, action='append', help='Category IDs (can specify multiple times)')
    product_update_parser.add_argument('status', location='form', required=False, help='Product status (available, sold_out, discontinued)')
    product_update_parser.add_argument('thumbnail', location='files', type=FileStorage, required=False, help='Thumbnail image file')
    product_update_parser.add_argument('images', location='files', type=FileStorage, required=False, action='append', help='Product image files')
    product_update_parser.add_argument('videos', location='files', type=FileStorage, required=False, action='append', help='Product video files')
    
    return product_model, product_input_model, product_form_parser, product_update_model, product_update_parser

# Marshmallow schemas for validation
class SpecsSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields
    
    cpu = ma_fields.String(required=True)
    ram = ma_fields.String(required=True)
    storage = ma_fields.String(required=True)
    display = ma_fields.String(required=True)
    gpu = ma_fields.String(required=True)
    battery = ma_fields.String(required=True)
    os = ma_fields.String(required=True)
    ports = ma_fields.List(ma_fields.String(), required=True)

class ProductSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields
    
    name = ma_fields.String(required=True)
    brand = ma_fields.String(required=True)
    model = ma_fields.String(required=True)
    price = ma_fields.Integer(required=True, validate=validate.Range(min=0))
    discount_percent = ma_fields.Integer(required=True, validate=validate.Range(min=0, max=100))
    specs = ma_fields.Nested(SpecsSchema, required=True)
    stock_quantity = ma_fields.Integer(required=True, validate=validate.Range(min=0))
    category_ids = ma_fields.List(ma_fields.String(), required=False, default=[])
    status = ma_fields.String(validate=validate.OneOf(['available', 'sold_out', 'discontinued']), required=False, default='available') 