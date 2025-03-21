# API Documentation: Category Management

## Overview
This document provides comprehensive information about the Category Management API endpoints in the system. The API allows for creating, retrieving, updating, and deleting product categories.

## Base URL
All API endpoints are accessible under: `/api/categories`

## Authentication
*Currently no authentication is implemented.*

## Data Model

### Category Schema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | String | Auto-generated | Unique identifier for the category |
| name | String | Yes | Category name (e.g., "Laptops") |
| description | String | No | Category description (e.g., "All laptop products") |
| created_at | DateTime | Auto-generated | Timestamp when the category was created |
| updated_at | DateTime | Auto-generated | Timestamp when the category was last updated |

## API Endpoints

### 1. List All Categories
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
    "description": "",
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

### 2. Create a New Category
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

### 3. Get a Category by ID
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

### 4. Update a Category
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

### 5. Delete a Category
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

## Error Handling

The API returns appropriate HTTP status codes and error messages for different scenarios:

### Common Error Codes

| Status Code | Description | Possible Causes |
|-------------|-------------|----------------|
| 400 | Bad Request | Invalid request format, missing required fields |
| 404 | Not Found | Category not found |
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
   - Message: "Invalid category ID format: {id}"

2. **Category Not Found**:
   - Status Code: 404
   - Message: "Category with ID {id} not found"

3. **Validation Error**:
   - Status Code: 400
   - Message: "Validation error"
   - Errors: Object containing field-specific validation errors

## Special Considerations

1. **Category Description**:
   - The description field is optional
   - You can set it to empty/null by providing an empty string in the update request

2. **Category and Products Relationship**:
   - Products can reference categories using the `category_ids` field
   - Deleting a category does not automatically update or delete associated products
   - It's recommended to check for product associations before deleting categories 