# API Documentation: Product Management

## Overview
This document provides comprehensive information about the Product Management API endpoints in the system. The API allows for creating, retrieving, updating, and deleting product information, including file uploads for product media.

## Technical Implementation Notes
- All API endpoints use JSON for data exchange, except for file upload operations
- File uploads are handled using `multipart/form-data` format
- MongoDB ObjectIds are automatically converted to strings in responses
- Dates are returned in ISO 8601 format (e.g., "2023-03-21T08:30:00.000Z")

## Base URL
All API endpoints are accessible under: `/api/products`

## Authentication
*Currently no authentication is implemented.*

## Data Model

### Product Schema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | String | Auto-generated | Unique identifier for the product |
| name | String | Yes | Product name (e.g., "Laptop Dell XPS 15") |
| brand | String | Yes | Brand name (e.g., "Dell") |
| model | String | Yes | Model number (e.g., "XPS 15 9530") |
| price | Integer | Yes | Original price in Vietnamese Dong (e.g., 35000000) |
| discount_percent | Integer | Yes | Discount percentage (0-100) |
| discount_price | Integer | Auto-calculated | Price after discount (price - (price * discount_percent / 100)) |
| specs | Object | Yes | Product specifications (see Specs Schema) |
| stock_quantity | Integer | Yes | Available stock quantity |
| category_ids | Array of Strings | No | Array of category IDs this product belongs to |
| thumbnail | String | No | GridFS file ID for the product thumbnail |
| images | Array of Strings | No | Array of GridFS file IDs for product images |
| videos | Array of Strings | No | Array of GridFS file IDs for product videos |
| created_at | DateTime | Auto-generated | Timestamp when the product was created |
| updated_at | DateTime | Auto-generated | Timestamp when the product was last updated |
| status | String | No (default: "available") | Product status: "available", "sold_out", or "discontinued" |

### Specs Schema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| cpu | String | Yes | CPU model (e.g., "Intel Core i7-13700H") |
| ram | String | Yes | RAM configuration (e.g., "16GB DDR5") |
| storage | String | Yes | Storage configuration (e.g., "512GB NVMe SSD") |
| display | String | Yes | Display specifications (e.g., "15.6 inch 4K OLED") |
| gpu | String | Yes | GPU model (e.g., "NVIDIA RTX 4060 6GB") |
| battery | String | Yes | Battery capacity (e.g., "86Wh") |
| os | String | Yes | Operating system (e.g., "Windows 11 Pro") |
| ports | Array of Strings | Yes | Available ports (e.g., ["USB-C", "HDMI", "3.5mm Audio"]) |

## API Endpoints

### 1. List All Products
**Endpoint:** `GET /api/products/`  
**Description:** Retrieves a list of all products.

**Response:**
- Status Code: 200 OK
- Content Type: application/json
- Body: Array of Product objects

**Example Request:**
```
GET /api/products/
```

**Example Response:**
```json
[
  {
    "_id": "6600a1c3b6f4a2d4e8f3b131",
    "name": "Laptop Dell XPS 15",
    "brand": "Dell",
    "model": "XPS 15 9530",
    "price": 35000000,
    "discount_percent": 10,
    "discount_price": 31500000,
    "specs": {
      "cpu": "Intel Core i7-13700H",
      "ram": "16GB DDR5",
      "storage": "512GB NVMe SSD",
      "display": "15.6 inch 4K OLED",
      "gpu": "NVIDIA RTX 4060 6GB",
      "battery": "86Wh",
      "os": "Windows 11 Pro",
      "ports": ["USB-C", "HDMI", "3.5mm Audio"]
    },
    "stock_quantity": 50,
    "category_ids": ["6600a1c3b6f4a2d4e8f3b130"],
    "thumbnail": "6600a1c3b6f4a2d4e8f3b132",
    "images": ["6600a1c3b6f4a2d4e8f3b133", "6600a1c3b6f4a2d4e8f3b134"],
    "videos": ["6600a1c3b6f4a2d4e8f3b135"],
    "created_at": "2023-03-21T08:30:00.000Z",
    "updated_at": "2023-03-21T08:30:00.000Z",
    "status": "available"
  }
]
```

### 2. Create a New Product
**Endpoint:** `POST /api/products/`  
**Description:** Creates a new product with optional file uploads.

**Request Body:**
- Content Type: multipart/form-data

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | String | Yes | Product name |
| brand | String | Yes | Brand name |
| model | String | Yes | Model number |
| price | Integer | Yes | Original price |
| discount_percent | Integer | Yes | Discount percentage (0-100) |
| specs.cpu | String | Yes | CPU model |
| specs.ram | String | Yes | RAM configuration |
| specs.storage | String | Yes | Storage configuration |
| specs.display | String | Yes | Display specifications |
| specs.gpu | String | Yes | GPU model |
| specs.battery | String | Yes | Battery capacity |
| specs.os | String | Yes | Operating system |
| specs.ports | Array | Yes | Available ports (can specify multiple times) |
| stock_quantity | Integer | Yes | Available stock |
| category_ids | Array | No | Category IDs (can specify multiple times) |
| status | String | No | Product status |
| thumbnail | File | No | Thumbnail image file |
| images | File(s) | No | Product image files (can upload multiple) |
| videos | File(s) | No | Product video files (can upload multiple) |

**Notes on category_ids:**
- Each category ID must be a valid MongoDB ObjectId (24-character hexadecimal string)
- The API will verify that each category ID exists in the database
- To specify multiple category IDs, use the same field name multiple times in the form data
- Example: `category_ids=6600a1c3b6f4a2d4e8f3b130&category_ids=6600a1c3b6f4a2d4e8f3b136`

**Response:**
- Status Code: 201 Created
- Content Type: application/json
- Body: The created Product object

**Example Request:**
```
POST /api/products/
Content-Type: multipart/form-data

name=Laptop Dell XPS 15
brand=Dell
model=XPS 15 9530
price=35000000
discount_percent=10
specs.cpu=Intel Core i7-13700H
specs.ram=16GB DDR5
specs.storage=512GB NVMe SSD
specs.display=15.6 inch 4K OLED
specs.gpu=NVIDIA RTX 4060 6GB
specs.battery=86Wh
specs.os=Windows 11 Pro
specs.ports=USB-C
specs.ports=HDMI
specs.ports=3.5mm Audio
stock_quantity=50
category_ids=6600a1c3b6f4a2d4e8f3b130
status=available
thumbnail=@thumbnail.jpg
images=@image1.jpg
images=@image2.jpg
videos=@video1.mp4
```

**Example Response:**
```json
{
  "_id": "6600a1c3b6f4a2d4e8f3b131",
  "name": "Laptop Dell XPS 15",
  "brand": "Dell",
  "model": "XPS 15 9530",
  "price": 35000000,
  "discount_percent": 10,
  "discount_price": 31500000,
  "specs": {
    "cpu": "Intel Core i7-13700H",
    "ram": "16GB DDR5",
    "storage": "512GB NVMe SSD",
    "display": "15.6 inch 4K OLED",
    "gpu": "NVIDIA RTX 4060 6GB",
    "battery": "86Wh",
    "os": "Windows 11 Pro",
    "ports": ["USB-C", "HDMI", "3.5mm Audio"]
  },
  "stock_quantity": 50,
  "category_ids": ["6600a1c3b6f4a2d4e8f3b130"],
  "thumbnail": "6600a1c3b6f4a2d4e8f3b132",
  "images": ["6600a1c3b6f4a2d4e8f3b133", "6600a1c3b6f4a2d4e8f3b134"],
  "videos": ["6600a1c3b6f4a2d4e8f3b135"],
  "created_at": "2023-03-21T08:30:00.000Z",
  "updated_at": "2023-03-21T08:30:00.000Z",
  "status": "available"
}
```

**Possible Errors:**
- Status 400: "Invalid category ID format: {category_id}" - When a category ID is not a valid MongoDB ObjectId
- Status 400: "Category with ID {category_id} not found" - When a category ID doesn't exist in the database
- Status 400: "Validation error" - When required fields are missing or invalid

### 3. Get a Product by ID
**Endpoint:** `GET /api/products/{id}`  
**Description:** Retrieves a specific product by its ID.

**Parameters:**
- id (path): The product identifier

**Response:**
- Status Code: 200 OK
- Content Type: application/json
- Body: Product object

**Example Request:**
```
GET /api/products/6600a1c3b6f4a2d4e8f3b131
```

**Example Response:**
```json
{
  "_id": "6600a1c3b6f4a2d4e8f3b131",
  "name": "Laptop Dell XPS 15",
  "brand": "Dell",
  "model": "XPS 15 9530",
  "price": 35000000,
  "discount_percent": 10,
  "discount_price": 31500000,
  "specs": {
    "cpu": "Intel Core i7-13700H",
    "ram": "16GB DDR5",
    "storage": "512GB NVMe SSD",
    "display": "15.6 inch 4K OLED",
    "gpu": "NVIDIA RTX 4060 6GB",
    "battery": "86Wh",
    "os": "Windows 11 Pro",
    "ports": ["USB-C", "HDMI", "3.5mm Audio"]
  },
  "stock_quantity": 50,
  "category_ids": ["6600a1c3b6f4a2d4e8f3b130"],
  "thumbnail": "6600a1c3b6f4a2d4e8f3b132",
  "images": ["6600a1c3b6f4a2d4e8f3b133", "6600a1c3b6f4a2d4e8f3b134"],
  "videos": ["6600a1c3b6f4a2d4e8f3b135"],
  "created_at": "2023-03-21T08:30:00.000Z",
  "updated_at": "2023-03-21T08:30:00.000Z",
  "status": "available"
}
```

### 4. Update a Product
**Endpoint:** `PUT /api/products/{id}`  
**Description:** Updates a specific product by its ID.

**Parameters:**
- id (path): The product identifier

**Request Body:**
- Content Type: multipart/form-data

*All fields are optional. Only specified fields will be updated.*

| Field | Type | Description |
|-------|------|-------------|
| name | String | Product name |
| brand | String | Brand name |
| model | String | Model number |
| price | Integer | Original price |
| discount_percent | Integer | Discount percentage (0-100) |
| specs.cpu | String | CPU model |
| specs.ram | String | RAM configuration |
| specs.storage | String | Storage configuration |
| specs.display | String | Display specifications |
| specs.gpu | String | GPU model |
| specs.battery | String | Battery capacity |
| specs.os | String | Operating system |
| specs.ports | Array | Available ports (can specify multiple times) |
| stock_quantity | Integer | Available stock |
| category_ids | Array | Category IDs (can specify multiple times) |
| status | String | Product status |
| thumbnail | File | Thumbnail image file |
| images | File(s) | Product image files (can upload multiple) |
| videos | File(s) | Product video files (can upload multiple) |

**Notes on category_ids:**
- Each category ID must be a valid MongoDB ObjectId (24-character hexadecimal string)
- The API will verify that each category ID exists in the database
- To specify multiple category IDs, use the same field name multiple times in the form data
- Providing an empty category_ids field will clear all categories associated with the product
- Example: `category_ids=6600a1c3b6f4a2d4e8f3b130&category_ids=6600a1c3b6f4a2d4e8f3b136`

**Response:**
- Status Code: 200 OK
- Content Type: application/json
- Body: The updated Product object

**Example Request:**
```
PUT /api/products/6600a1c3b6f4a2d4e8f3b131
Content-Type: multipart/form-data

price=34000000
discount_percent=15
stock_quantity=45
status=sold_out
```

**Example Response:**
```json
{
  "_id": "6600a1c3b6f4a2d4e8f3b131",
  "name": "Laptop Dell XPS 15",
  "brand": "Dell",
  "model": "XPS 15 9530",
  "price": 34000000,
  "discount_percent": 15,
  "discount_price": 28900000,
  "specs": {
    "cpu": "Intel Core i7-13700H",
    "ram": "16GB DDR5",
    "storage": "512GB NVMe SSD",
    "display": "15.6 inch 4K OLED",
    "gpu": "NVIDIA RTX 4060 6GB",
    "battery": "86Wh",
    "os": "Windows 11 Pro",
    "ports": ["USB-C", "HDMI", "3.5mm Audio"]
  },
  "stock_quantity": 45,
  "category_ids": ["6600a1c3b6f4a2d4e8f3b130"],
  "thumbnail": "6600a1c3b6f4a2d4e8f3b132",
  "images": ["6600a1c3b6f4a2d4e8f3b133", "6600a1c3b6f4a2d4e8f3b134"],
  "videos": ["6600a1c3b6f4a2d4e8f3b135"],
  "created_at": "2023-03-21T08:30:00.000Z",
  "updated_at": "2023-03-21T09:15:00.000Z",
  "status": "sold_out"
}
```

**Possible Errors:**
- Status 400: "Invalid product ID format: {id}" - When the product ID is not a valid MongoDB ObjectId
- Status 404: "Product with ID {id} not found" - When the product doesn't exist in the database
- Status 400: "Invalid category ID format: {category_id}" - When a category ID is not a valid MongoDB ObjectId
- Status 400: "Category with ID {category_id} not found" - When a category ID doesn't exist in the database
- Status 400: "Validation error" - When updated fields have invalid values

### 5. Delete a Product
**Endpoint:** `DELETE /api/products/{id}`  
**Description:** Deletes a specific product by its ID.

**Parameters:**
- id (path): The product identifier

**Response:**
- Status Code: 204 No Content

**Example Request:**
```
DELETE /api/products/6600a1c3b6f4a2d4e8f3b131
```

### 6. Get Product File
**Endpoint:** `GET /api/products/files/{file_id}`  
**Description:** Retrieves a file (image, video, or thumbnail) by its GridFS file ID.

**Parameters:**
- file_id (path): The file identifier in GridFS

**Response:**
- Status Code: 200 OK
- Content Type: [original file content type]
- Body: Binary file data

**Example Request:**
```
GET /api/products/files/6600a1c3b6f4a2d4e8f3b132
```

## Error Handling

The API returns appropriate HTTP status codes and error messages for different scenarios:

### Common Error Codes

| Status Code | Description | Possible Causes |
|-------------|-------------|----------------|
| 400 | Bad Request | Invalid request format, missing required fields, invalid field values |
| 404 | Not Found | Product or file not found |
| 500 | Internal Server Error | Server-side error during processing |

### Error Response Format

```json
{
  "message": "Error description",
  "errors": {
    "field_name": ["Error details"]
  }
}
```

### Specific Error Messages

1. **Invalid Object ID Format**:
   - Status Code: 400
   - Message: "Invalid product ID format: {id}"

2. **Product Not Found**:
   - Status Code: 404
   - Message: "Product with ID {id} not found"

3. **Category Not Found**:
   - Status Code: 400
   - Message: "Category with ID {category_id} not found"

4. **Validation Error**:
   - Status Code: 400
   - Message: "Validation error"
   - Errors: Object containing field-specific validation errors

5. **File Not Found**:
   - Status Code: 404
   - Message: "File not found"

## Special Considerations

1. **File Uploads**:
   - Files are stored in MongoDB GridFS
   - Supported file types: images (JPG, PNG, GIF), videos (MP4, WebM)
   - Maximum file size: Determined by server configuration
   - When updating a product, uploading a new file will replace the old one

2. **Category IDs**:
   - When creating/updating a product, the system validates if the provided category IDs exist
   - You can send an empty array to remove all categories from a product

3. **Product Status**:
   - "available": Product is available for purchase
   - "sold_out": Product is temporarily out of stock
   - "discontinued": Product is no longer being sold

4. **Discount Price Calculation**:
   - The discount_price field is automatically calculated based on price and discount_percent
   - Formula: discount_price = price - (price * discount_percent / 100)

5. **MongoDB ObjectId Handling**:
   - All MongoDB ObjectId values (like _id, category_ids, and file IDs) are automatically serialized to string format in JSON responses
   - When sending ObjectId values in requests (like category_ids), you should provide the 24-character hexadecimal string format
   - Example: "6600a1c3b6f4a2d4e8f3b131" 