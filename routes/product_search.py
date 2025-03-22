from flask import request, jsonify
from flask_restx import Namespace, Resource, fields, reqparse
from bson import ObjectId
from database import products_collection, categories_collection
from utils.mongo_utils import format_product

# Create namespace
search_ns = Namespace('product-search', description='Product search operations')

# Create search parser
search_parser = reqparse.RequestParser()
search_parser.add_argument('query', type=str, required=False, help='Text search query', location='args')
search_parser.add_argument('min_price', type=int, required=False, help='Minimum price', location='args')
search_parser.add_argument('max_price', type=int, required=False, help='Maximum price', location='args')
search_parser.add_argument('min_discount', type=int, required=False, help='Minimum discount percentage', location='args')
search_parser.add_argument('max_discount', type=int, required=False, help='Maximum discount percentage', location='args')
search_parser.add_argument('brands', type=str, required=False, help='Brands (comma-separated)', location='args')
search_parser.add_argument('category_ids', type=str, required=False, help='Category IDs (comma-separated)', location='args')
search_parser.add_argument('status', type=str, required=False, help='Product status (available, sold_out, discontinued)', location='args')
search_parser.add_argument('cpu', type=str, required=False, help='CPU search term', location='args')
search_parser.add_argument('ram', type=str, required=False, help='RAM search term', location='args')
search_parser.add_argument('storage', type=str, required=False, help='Storage search term', location='args')
search_parser.add_argument('gpu', type=str, required=False, help='GPU search term', location='args')
search_parser.add_argument('sort_by', type=str, required=False, 
                          help='Sort field (price, discount_price, discount_percent, created_at)', 
                          location='args', 
                          choices=['price', 'discount_price', 'discount_percent', 'created_at'])
search_parser.add_argument('sort_order', type=str, required=False, 
                          help='Sort order (asc, desc)',
                          location='args',
                          default='asc',
                          choices=['asc', 'desc'])
search_parser.add_argument('page', type=int, required=False, help='Page number', location='args', default=1)
search_parser.add_argument('limit', type=int, required=False, help='Items per page', location='args', default=10)

# Response model for search results
product_model = search_ns.model('Product', {
    '_id': fields.String(description='Product ID'),
    'name': fields.String(description='Product name'),
    'brand': fields.String(description='Brand name'),
    'model': fields.String(description='Model number'),
    'price': fields.Integer(description='Original price'),
    'discount_percent': fields.Integer(description='Discount percentage'),
    'discount_price': fields.Integer(description='Price after discount'),
    'specs': fields.Raw(description='Product specifications'),
    'stock_quantity': fields.Integer(description='Available stock'),
    'category_ids': fields.List(fields.String, description='Category IDs'),
    'thumbnail': fields.String(description='Thumbnail file ID'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp'),
    'status': fields.String(description='Product status')
})

pagination_model = search_ns.model('PaginatedResult', {
    'total': fields.Integer(description='Total number of items'),
    'page': fields.Integer(description='Current page number'),
    'limit': fields.Integer(description='Items per page'),
    'pages': fields.Integer(description='Total number of pages'),
    'products': fields.List(fields.Nested(product_model), description='List of products')
})

# Search API endpoints
@search_ns.route('/')
class ProductSearch(Resource):
    @search_ns.doc('search_products')
    @search_ns.expect(search_parser)
    @search_ns.response(200, 'Success', pagination_model)
    def get(self):
        """Search products with filters"""
        args = search_parser.parse_args()
        
        # Build the query
        query = {}
        
        # Text search (across name, brand, model)
        if args.query:
            query['$or'] = [
                {'name': {'$regex': args.query, '$options': 'i'}},
                {'brand': {'$regex': args.query, '$options': 'i'}},
                {'model': {'$regex': args.query, '$options': 'i'}}
            ]
        
        # Price range filter
        price_filter = {}
        if args.min_price:
            price_filter['$gte'] = args.min_price
        if args.max_price:
            price_filter['$lte'] = args.max_price
        if price_filter:
            query['price'] = price_filter
        
        # Discount range filter
        discount_filter = {}
        if args.min_discount:
            discount_filter['$gte'] = args.min_discount
        if args.max_discount:
            discount_filter['$lte'] = args.max_discount
        if discount_filter:
            query['discount_percent'] = discount_filter
        
        # Brand filter
        if args.brands:
            brands = [brand.strip() for brand in args.brands.split(',')]
            query['brand'] = {'$in': brands}
        
        # Category filter
        if args.category_ids:
            try:
                print(f"Category IDs received: {args.category_ids}")
                # First try to convert to ObjectId, and if that fails, use as string
                category_ids_obj = []
                category_ids_str = []
                
                for cat_id in args.category_ids.split(','):
                    cat_id = cat_id.strip()
                    try:
                        if ObjectId.is_valid(cat_id):
                            # Keep both ObjectId and string version for query
                            category_ids_obj.append(ObjectId(cat_id))
                            category_ids_str.append(cat_id)
                            print(f"Added valid ObjectId: {cat_id}")
                        else:
                            # If not a valid ObjectId, use as string (for test/dev environments)
                            category_ids_str.append(cat_id)
                            print(f"Using category ID as string: {cat_id}")
                    except Exception as e:
                        print(f"Error converting category ID {cat_id}: {str(e)}")
                        # Keep the original ID as a fallback
                        category_ids_str.append(cat_id)
                
                print(f"Looking for ObjectIds: {category_ids_obj}")
                print(f"Looking for string IDs: {category_ids_str}")
                
                if category_ids_obj or category_ids_str:
                    # Check for EITHER string IDs or ObjectIds
                    or_conditions = []
                    
                    # Add ObjectId condition if we have any
                    if category_ids_obj:
                        or_conditions.append({'category_ids': {'$in': category_ids_obj}})
                    
                    # Add string ID condition if we have any
                    if category_ids_str:
                        or_conditions.append({'category_ids': {'$in': category_ids_str}})
                    
                    # Use $or to check both conditions
                    if len(or_conditions) > 1:
                        query['$or'] = or_conditions
                    else:
                        # Just one type of ID to check
                        query['category_ids'] = {'$in': category_ids_obj or category_ids_str}
                    
                    print(f"Final query part for categories: {query.get('$or') or query.get('category_ids')}")
            except Exception as e:
                print(f"Error in category filter: {str(e)}")
                # Don't add category filter if there's an error
        
        # Status filter
        if args.status:
            statuses = [status.strip() for status in args.status.split(',')]
            query['status'] = {'$in': statuses}
        
        # Specs filters
        specs_filter = {}
        if args.cpu:
            specs_filter['cpu'] = {'$regex': args.cpu, '$options': 'i'}
        if args.ram:
            specs_filter['ram'] = {'$regex': args.ram, '$options': 'i'}
        if args.storage:
            specs_filter['storage'] = {'$regex': args.storage, '$options': 'i'}
        if args.gpu:
            specs_filter['gpu'] = {'$regex': args.gpu, '$options': 'i'}
        if specs_filter:
            for key, value in specs_filter.items():
                query[f'specs.{key}'] = value
        
        # Pagination
        page = max(1, args.page)
        limit = max(1, min(100, args.limit))  # Limit between 1 and 100
        skip = (page - 1) * limit
        
        # Sorting
        sort_by = args.sort_by or 'created_at'
        sort_order = 1 if args.sort_order == 'asc' else -1
        sort_criteria = [(sort_by, sort_order)]
        
        # Execute query
        total = products_collection.count_documents(query)
        products_cursor = products_collection.find(query).skip(skip).limit(limit).sort(sort_criteria)
        products = [format_product(product) for product in products_cursor]
        
        # Calculate total pages
        total_pages = (total + limit - 1) // limit
        
        # Return paginated results
        return {
            'total': total,
            'page': page,
            'limit': limit,
            'pages': total_pages,
            'products': products
        }

@search_ns.route('/brands')
class BrandList(Resource):
    @search_ns.doc('list_brands')
    @search_ns.response(200, 'Success')
    def get(self):
        """Get list of available brands for filtering"""
        brands = products_collection.distinct('brand')
        return {'brands': brands}

@search_ns.route('/price-range')
class PriceRange(Resource):
    @search_ns.doc('get_price_range')
    @search_ns.response(200, 'Success')
    def get(self):
        """Get min and max prices available for filtering"""
        min_price = products_collection.find_one({}, sort=[('price', 1)])
        max_price = products_collection.find_one({}, sort=[('price', -1)])
        
        return {
            'min_price': min_price['price'] if min_price else 0,
            'max_price': max_price['price'] if max_price else 0
        }

@search_ns.route('/filter-options')
class FilterOptions(Resource):
    @search_ns.doc('get_filter_options')
    @search_ns.response(200, 'Success')
    def get(self):
        """Get all available filter options for specs fields"""
        # Get all unique values for each specs field
        cpu_options = products_collection.distinct('specs.cpu')
        ram_options = products_collection.distinct('specs.ram')
        storage_options = products_collection.distinct('specs.storage')
        gpu_options = products_collection.distinct('specs.gpu')
        display_options = products_collection.distinct('specs.display')
        os_options = products_collection.distinct('specs.os')
        
        # Get all statuses
        status_options = products_collection.distinct('status')
        
        # Get all categories with names
        categories = list(categories_collection.find({}, {'_id': 1, 'name': 1}))
        category_options = [{'id': str(cat['_id']), 'name': cat['name']} for cat in categories]
        
        return {
            'specs': {
                'cpu': cpu_options,
                'ram': ram_options,
                'storage': storage_options,
                'gpu': gpu_options,
                'display': display_options,
                'os': os_options
            },
            'status': status_options,
            'categories': category_options
        } 