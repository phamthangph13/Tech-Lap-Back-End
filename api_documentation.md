# API Documentation: Product Catalog Management

## Overview
This document provides comprehensive information about the Product Catalog Management API endpoints in the system. The API allows for creating, retrieving, updating, and deleting both products and categories, including file uploads for product media.

## Base URL
All API endpoints are accessible under: `/api`

## Authentication
*Currently no authentication is implemented.*

## Table of Contents
1. [Product Management](#product-management)
   - [Data Model](#product-data-model)
   - [Endpoints](#product-endpoints)
   - [Error Handling](#product-error-handling)
   - [Special Considerations](#product-special-considerations)
2. [Category Management](#category-management)
   - [Data Model](#category-data-model)
   - [Endpoints](#category-endpoints)
   - [Error Handling](#category-error-handling)
   - [Special Considerations](#category-special-considerations)

---

## Product Management

### Product Data Model

#### Product Schema
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

#### Specs Schema
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

### Product Endpoints

#### 1. List All Products
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

#### 2. Create a New Product
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

#### 3. Get a Product by ID
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

#### 4. Update a Product
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

#### 5. Delete a Product
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

#### 6. Get Product File
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

### Product Error Handling

The API returns appropriate HTTP status codes and error messages for different scenarios:

#### Common Error Codes

| Status Code | Description | Possible Causes |
|-------------|-------------|----------------|
| 400 | Bad Request | Invalid request format, missing required fields, invalid field values |
| 404 | Not Found | Product or file not found |
| 500 | Internal Server Error | Server-side error during processing |

#### Error Response Format

```json
{
  "message": "Error description",
  "errors": {
    "field_name": ["Error details"]
  }
}
```

#### Specific Error Messages

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

### Product Special Considerations

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

---

## Category Management

### Category Data Model

#### Category Schema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | String | Auto-generated | Unique identifier for the category |
| name | String | Yes | Category name (e.g., "Laptops") |
| description | String | No | Category description (e.g., "All laptop products") |
| created_at | DateTime | Auto-generated | Timestamp when the category was created |
| updated_at | DateTime | Auto-generated | Timestamp when the category was last updated |

### Category Endpoints

#### 1. List All Categories
**Endpoint:** `GET /api/categories/`  
**Description:** Retrieves a list of all categories.

**Response:**
- Status Code: 200 OK
- Content Type: application/json
- Body: Array of Category objects

**Example Request:**
```
GET /api/categories/
```

**Example Response:**
```json
[
  {
    "_id": "6600a1c3b6f4a2d4e8f3b130",
    "name": "Laptops",
    "description": "All laptop products",
    "created_at": "2023-03-21T08:00:00.000Z",
    "updated_at": "2023-03-21T08:00:00.000Z"
  },
  {
    "_id": "6600a1c3b6f4a2d4e8f3b136",
    "name": "Smartphones",
    "description": "Mobile phones and accessories",
    "created_at": "2023-03-21T08:05:00.000Z",
    "updated_at": "2023-03-21T08:05:00.000Z"
  }
]
```

#### 2. Create a New Category
**Endpoint:** `POST /api/categories/`  
**Description:** Creates a new category.

**Request Body:**
- Content Type: application/x-www-form-urlencoded

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | String | Yes | Category name |
| description | String | No | Category description |

**Response:**
- Status Code: 201 Created
- Content Type: application/json
- Body: The created Category object

**Example Request:**
```
POST /api/categories/
Content-Type: application/x-www-form-urlencoded

name=Accessories
description=Computer peripherals and accessories
```

**Example Response:**
```json
{
  "_id": "6600a1c3b6f4a2d4e8f3b137",
  "name": "Accessories",
  "description": "Computer peripherals and accessories",
  "created_at": "2023-03-21T09:30:00.000Z",
  "updated_at": "2023-03-21T09:30:00.000Z"
}
```

#### 3. Get a Category by ID
**Endpoint:** `GET /api/categories/{id}`  
**Description:** Retrieves a specific category by its ID.

**Parameters:**
- id (path): The category identifier

**Response:**
- Status Code: 200 OK
- Content Type: application/json
- Body: Category object

**Example Request:**
```
GET /api/categories/6600a1c3b6f4a2d4e8f3b130
```

**Example Response:**
```json
{
  "_id": "6600a1c3b6f4a2d4e8f3b130",
  "name": "Laptops",
  "description": "All laptop products",
  "created_at": "2023-03-21T08:00:00.000Z",
  "updated_at": "2023-03-21T08:00:00.000Z"
}
```

#### 4. Update a Category
**Endpoint:** `PUT /api/categories/{id}`  
**Description:** Updates a specific category by its ID.

**Parameters:**
- id (path): The category identifier

**Request Body:**
- Content Type: application/x-www-form-urlencoded

*All fields are optional. Only specified fields will be updated.*

| Field | Type | Description |
|-------|------|-------------|
| name | String | Category name |
| description | String | Category description (can be empty to remove description) |

**Response:**
- Status Code: 200 OK
- Content Type: application/json
- Body: The updated Category object

**Example Request:**
```
PUT /api/categories/6600a1c3b6f4a2d4e8f3b130
Content-Type: application/x-www-form-urlencoded

name=Gaming Laptops
description=High-performance gaming laptops
```

**Example Response:**
```json
{
  "_id": "6600a1c3b6f4a2d4e8f3b130",
  "name": "Gaming Laptops",
  "description": "High-performance gaming laptops",
  "created_at": "2023-03-21T08:00:00.000Z",
  "updated_at": "2023-03-21T10:15:00.000Z"
}
```

#### 5. Delete a Category
**Endpoint:** `DELETE /api/categories/{id}`  
**Description:** Deletes a specific category by its ID.

**Parameters:**
- id (path): The category identifier

**Response:**
- Status Code: 204 No Content

**Example Request:**
```
DELETE /api/categories/6600a1c3b6f4a2d4e8f3b137
```

### Category Error Handling

The API returns appropriate HTTP status codes and error messages for different scenarios:

#### Common Error Codes

| Status Code | Description | Possible Causes |
|-------------|-------------|----------------|
| 400 | Bad Request | Invalid request format, missing required fields |
| 404 | Not Found | Category not found |
| 500 | Internal Server Error | Server-side error during processing |

#### Error Response Format

```json
{
  "message": "Error description",
  "errors": {
    "field_name": ["Error details"]
  }
}
```

#### Specific Error Messages

1. **Invalid Object ID Format**:
   - Status Code: 400
   - Message: "Invalid category ID format: {id}"

2. **Category Not Found**:
   - Status Code: 404
   - Message: "Category with ID {id} not found"

3. **Validation Error**:
   - Status Code: 400
   - Message: "Validation error"
   - Errors: Object containing field-specific validation errors

### Category Special Considerations

1. **Category Description**:
   - The description field is optional
   - You can set it to empty/null by providing an empty string in the update request

2. **Category and Products Relationship**:
   - Products can reference categories using the `category_ids` field
   - Deleting a category does not automatically update or delete associated products
   - It's recommended to check for product associations before deleting categories 