from flask import Flask, make_response
from flask_restx import Api
from flask_cors import CORS
import os
from dotenv import load_dotenv
from routes.product_routes import product_ns
from routes.category_routes import category_ns
from routes.product_search import search_ns
from routes.order_routes import order_ns
from utils.mongo_utils import MongoJSONEncoder
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure JSON encoder for MongoDB ObjectId
app.json_encoder = MongoJSONEncoder

# Disable strict trailing slash requirement
app.url_map.strict_slashes = False

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure Swagger documentation
api = Api(
    app,
    version="1.0",
    title="Product Catalog API",
    description="CRUD API for managing products and categories in MongoDB",
    doc="/api/docs"
)

# Define custom output_json function for Flask-RESTx
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, cls=MongoJSONEncoder), code)
    resp.headers.extend(headers or {})
    return resp

# Register namespaces
api.add_namespace(product_ns, path="/api/products")
api.add_namespace(category_ns, path="/api/categories")
api.add_namespace(search_ns, path="/api/product-search")
api.add_namespace(order_ns, path="/api/orders")

if __name__ == "__main__":
    app.run(debug=True) 