from flask import request
from flask_restx import Namespace, Resource, fields
from database import products_collection, orders_collection
from bson import ObjectId
from datetime import datetime
from utils.mongo_utils import object_id_to_str, str_to_object_id
import random
import string

# Create namespace for order operations
order_ns = Namespace('orders', description='Order operations')

# Define models for request and response validation
customer_model = order_ns.model('Customer', {
    'fullName': fields.String(required=True, description='Customer full name'),
    'phone': fields.String(required=True, description='Customer phone number'),
    'email': fields.String(required=True, description='Customer email')
})

shipping_address_model = order_ns.model('ShippingAddress', {
    'province': fields.String(required=True, description='Province/City'),
    'district': fields.String(required=True, description='District'),
    'ward': fields.String(required=True, description='Ward'),
    'streetAddress': fields.String(required=True, description='Street address')
})

order_item_model = order_ns.model('OrderItem', {
    'productId': fields.String(required=True, description='Product ID'),
    'quantity': fields.Integer(required=True, description='Quantity'),
    'variantName': fields.String(required=True, description='Variant name'),
    'colorName': fields.String(required=True, description='Color name')
})

payment_model = order_ns.model('Payment', {
    'method': fields.String(required=True, description='Payment method', enum=['COD'])
})

order_request_model = order_ns.model('OrderRequest', {
    'customer': fields.Nested(customer_model, required=True),
    'shippingAddress': fields.Nested(shipping_address_model, required=True),
    'items': fields.List(fields.Nested(order_item_model), required=True),
    'payment': fields.Nested(payment_model, required=True)
})

order_item_response_model = order_ns.model('OrderItemResponse', {
    'productName': fields.String(description='Product name'),
    'variantName': fields.String(description='Variant name'),
    'colorName': fields.String(description='Color name'),
    'quantity': fields.Integer(description='Quantity'),
    'unitPrice': fields.Integer(description='Unit price'),
    'discountedPrice': fields.Integer(description='Discounted price'),
    'subtotal': fields.Integer(description='Subtotal')
})

order_response_model = order_ns.model('OrderResponse', {
    'success': fields.Boolean(description='Success status'),
    'message': fields.String(description='Response message'),
    'data': fields.Raw(description='Order data')
})

error_response_model = order_ns.model('ErrorResponse', {
    'success': fields.Boolean(description='Success status'),
    'message': fields.String(description='Error message'),
    'errors': fields.List(fields.String, description='List of errors')
})

def generate_order_number():
    """Generate a unique order number in the format TS-YYYYMMDD-XXX"""
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.digits, k=3))
    order_number = f"TS-{date_part}-{random_part}"
    
    # Check if the order number already exists, if so, generate a new one
    existing_order = orders_collection.find_one({"order_number": order_number})
    if existing_order:
        return generate_order_number()
    
    return order_number

@order_ns.route('')
class OrderResource(Resource):
    @order_ns.expect(order_request_model)
    @order_ns.response(201, 'Order created successfully', order_response_model)
    @order_ns.response(400, 'Invalid request', error_response_model)
    def post(self):
        """Create a new order"""
        try:
            # Get request data
            order_data = request.json
            errors = []
            
            # Validate customer information
            if not order_data.get('customer'):
                errors.append("Customer information is required")
            
            # Validate shipping address
            if not order_data.get('shippingAddress'):
                errors.append("Shipping address is required")
            
            # Validate items
            items = order_data.get('items', [])
            if not items:
                errors.append("Order must contain at least one item")
            
            # Validate payment method
            payment = order_data.get('payment', {})
            if not payment or payment.get('method') != 'COD':
                errors.append("Only COD payment method is supported")
            
            if errors:
                return {
                    "success": False,
                    "message": "Failed to create order",
                    "errors": errors
                }, 400
            
            # Process order items
            processed_items = []
            subtotal = 0
            discount_total = 0
            warnings = []  # For non-critical issues
            
            for item in items:
                product_id = item.get('productId')
                
                # Validate product ID
                try:
                    product_obj_id = ObjectId(product_id)
                except:
                    errors.append(f"Invalid product ID: {product_id}")
                    continue
                
                # Fetch product from database
                product = products_collection.find_one({"_id": product_obj_id})
                if not product:
                    errors.append(f"Product not found: {product_id}")
                    continue
                
                # Validate variant
                variant_name = item.get('variantName')
                variant = None
                for v in product.get('variant_specs', []):
                    if v.get('name') == variant_name:
                        variant = v
                        break
                
                if not variant:
                    # If requested variant not found, check if any variants exist
                    variant_specs = product.get('variant_specs', [])
                    if variant_specs:
                        # Use the first variant as default
                        variant = variant_specs[0]
                        variant_name = variant.get('name')
                        warnings.append(f"Requested variant '{item.get('variantName')}' not available. Using '{variant_name}' instead.")
                    else:
                        errors.append(f"Requested variant '{variant_name}' not available for product {product.get('name')}")
                        continue
                
                # Validate color
                color_name = item.get('colorName')
                color = None
                for c in product.get('colors', []):
                    if c.get('name') == color_name:
                        color = c
                        break
                
                if not color:
                    # If requested color not found, check if any colors exist
                    colors = product.get('colors', [])
                    if colors:
                        # Use the first color as default
                        color = colors[0]
                        color_name = color.get('name')
                        warnings.append(f"Requested color '{item.get('colorName')}' not available. Using '{color_name}' instead.")
                    else:
                        errors.append(f"Requested color '{color_name}' not available for product {product.get('name')}")
                        continue
                
                # Get quantity
                quantity = item.get('quantity', 1)
                if quantity <= 0:
                    quantity = 1  # Default to 1 if quantity is invalid
                
                # Calculate prices
                base_price = float(product.get('price', 0))
                variant_price = variant.get('price', 0)
                variant_discount_percent = variant.get('discount_percent', 0)
                
                color_price_adjustment = color.get('price_adjustment', 0)
                color_discount_adjustment = color.get('discount_adjustment', 0)
                
                # Calculate unit price (base + variant + color)
                unit_price = base_price + variant_price + color_price_adjustment
                
                # Calculate discount
                total_discount_percent = variant_discount_percent + color_discount_adjustment
                discount_amount = (unit_price * total_discount_percent) / 100
                discounted_price = unit_price - discount_amount
                
                # Calculate subtotal for this item
                item_subtotal = discounted_price * quantity
                
                # Add to order totals
                subtotal += item_subtotal
                discount_total += discount_amount * quantity
                
                # Create processed item
                processed_item = {
                    "productId": product_obj_id,
                    "productName": product.get('name', ''),
                    "basePrice": base_price,
                    
                    # Variant selection
                    "variantName": variant_name,
                    "variantSpecs": variant.get('specs', {}),
                    "variantPrice": variant_price,
                    "variantDiscountPercent": variant_discount_percent,
                    
                    # Color selection
                    "colorName": color_name,
                    "colorCode": color.get('code', ''),
                    "colorPriceAdjustment": color_price_adjustment,
                    "colorDiscountAdjustment": color_discount_adjustment,
                    
                    "quantity": quantity,
                    
                    # Price calculations
                    "unitPrice": unit_price,
                    "discountedPrice": discounted_price,
                    "subtotal": item_subtotal,
                    
                    # Product image
                    "thumbnailUrl": product.get('thumbnail', '')
                }
                
                processed_items.append(processed_item)
            
            if errors:
                return {
                    "success": False,
                    "message": "Failed to create order",
                    "errors": errors
                }, 400
            
            # Calculate shipping fee (could be based on location or order total)
            shipping_fee = 0  # For simplicity, free shipping
            
            # Calculate total
            total = subtotal + shipping_fee
            
            # Generate order number
            order_number = generate_order_number()
            
            # Copy product info
            product_info = []
            if processed_items and len(processed_items) > 0:
                first_product_id = processed_items[0]["productId"]
                product = products_collection.find_one({"_id": first_product_id})
                if product and 'product_info' in product:
                    product_info = product.get('product_info', [])
            
            # Create order document
            order_document = {
                "orderNumber": order_number,
                "customer": order_data.get('customer', {}),
                "shippingAddress": order_data.get('shippingAddress', {}),
                "items": processed_items,
                "payment": {
                    "method": order_data.get('payment', {}).get('method', 'COD'),
                    "status": "pending"
                },
                "productInfo": product_info,
                "subtotal": subtotal,
                "discountTotal": discount_total,
                "shippingFee": shipping_fee,
                "total": total,
                "status": "pending",
                "orderDate": datetime.now(),
                "updatedAt": datetime.now()
            }
            
            # Insert order into database
            result = orders_collection.insert_one(order_document)
            
            # Format response
            response_items = []
            for item in processed_items:
                response_items.append({
                    "productName": item.get('productName', ''),
                    "variantName": item.get('variantName', ''),
                    "colorName": item.get('colorName', ''),
                    "quantity": item.get('quantity', 0),
                    "unitPrice": item.get('unitPrice', 0),
                    "discountedPrice": item.get('discountedPrice', 0),
                    "subtotal": item.get('subtotal', 0)
                })
            
            # Return success response
            return {
                "success": True,
                "message": "Order created successfully",
                "data": {
                    "orderId": str(result.inserted_id),
                    "orderNumber": order_number,
                    "items": response_items,
                    "subtotal": subtotal,
                    "shippingFee": shipping_fee,
                    "total": total,
                    "status": "pending"
                },
                "warnings": warnings if warnings else None
            }, 201
            
        except Exception as e:
            # Return error response
            return {
                "success": False,
                "message": "Failed to create order",
                "errors": [str(e)]
            }, 400 