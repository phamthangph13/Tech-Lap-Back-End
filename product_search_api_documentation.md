# API Documentation: Product Search and Filtering

## Overview
This document provides information about the Product Search API endpoints. These endpoints allow users to search for products with various filtering options and get metadata for building filtering UI components.

## Base URL
All search API endpoints are accessible under: `/api/product-search`

## Table of Contents
1. [Search Products](#search-products)
2. [Get Brand List](#get-brand-list)
3. [Get Price Range](#get-price-range)
4. [Get Filter Options](#get-filter-options)

---

## Search Products

### Endpoint
**Endpoint:** `GET /api/product-search/`  
**Description:** Search for products with various filtering options.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | String | No | Text search query for product name, brand, or model |
| min_price | Integer | No | Minimum price filter |
| max_price | Integer | No | Maximum price filter |
| min_discount | Integer | No | Minimum discount percentage filter |
| max_discount | Integer | No | Maximum discount percentage filter |
| brands | String | No | Comma-separated list of brands to filter by (e.g., "Dell,Apple,HP") |
| category_ids | String | No | Comma-separated list of category IDs to filter by |
| status | String | No | Filter by product status (available, sold_out, discontinued) |
| cpu | String | No | Filter by CPU (partial match) |
| ram | String | No | Filter by RAM (partial match) |
| storage | String | No | Filter by storage (partial match) |
| gpu | String | No | Filter by GPU (partial match) |
| sort_by | String | No | Field to sort by (price, discount_price, discount_percent, created_at) |
| sort_order | String | No | Sort direction: "asc" or "desc" (default: "asc") |
| page | Integer | No | Page number for pagination (default: 1) |
| limit | Integer | No | Number of items per page (default: 10, max: 100) |

### Response
- Status Code: 200 OK
- Content Type: application/json
- Body: Paginated result object

**Response Body Format:**
```json
{
  "total": 45,             // Total number of matching products
  "page": 1,               // Current page
  "limit": 10,             // Items per page
  "pages": 5,              // Total number of pages
  "products": [            // Array of product objects
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
      "created_at": "2023-03-21T08:30:00.000Z",
      "updated_at": "2023-03-21T08:30:00.000Z",
      "status": "available"
    },
    // Additional products...
  ]
}
```

### Examples

#### Basic Text Search
```
GET /api/product-search/?query=dell laptop
```

#### Price Range and Brand Filter
```
GET /api/product-search/?min_price=20000000&max_price=40000000&brands=Dell,Lenovo
```

#### Category and Specs Filter
```
GET /api/product-search/?category_ids=6600a1c3b6f4a2d4e8f3b130&cpu=Intel&ram=16GB
```

#### Complex Filter with Sorting and Pagination
```
GET /api/product-search/?min_price=25000000&min_discount=10&brands=Dell,HP&status=available&sort_by=price&sort_order=desc&page=2&limit=20
```

## Get Brand List

### Endpoint
**Endpoint:** `GET /api/product-search/brands`  
**Description:** Retrieve a list of all available brands for filter UI options.

### Response
- Status Code: 200 OK
- Content Type: application/json
- Body: Array of brand names

**Response Body Format:**
```json
{
  "brands": [
    "Dell",
    "HP",
    "Apple",
    "Lenovo",
    "Asus",
    "Acer"
  ]
}
```

### Example
```
GET /api/product-search/brands
```

## Get Price Range

### Endpoint
**Endpoint:** `GET /api/product-search/price-range`  
**Description:** Get the minimum and maximum product prices available in the catalog for price filter UI components.

### Response
- Status Code: 200 OK
- Content Type: application/json
- Body: Price range object

**Response Body Format:**
```json
{
  "min_price": 5000000,
  "max_price": 100000000
}
```

### Example
```
GET /api/product-search/price-range
```

## Get Filter Options

### Endpoint
**Endpoint:** `GET /api/product-search/filter-options`  
**Description:** Get all available filter options for specs fields, statuses, and categories to build filter UI components.

### Response
- Status Code: 200 OK
- Content Type: application/json
- Body: Filter options object

**Response Body Format:**
```json
{
  "specs": {
    "cpu": [
      "Intel Core i7-13700H",
      "Intel Core i5-1240P",
      "AMD Ryzen 9 7940HS"
    ],
    "ram": [
      "16GB DDR5",
      "8GB DDR4",
      "32GB DDR5"
    ],
    "storage": [
      "512GB NVMe SSD",
      "1TB NVMe SSD",
      "256GB NVMe SSD"
    ],
    "gpu": [
      "NVIDIA RTX 4060 6GB",
      "Intel Iris Xe Graphics",
      "NVIDIA RTX 4070 8GB"
    ],
    "display": [
      "15.6 inch 4K OLED",
      "14 inch FHD IPS",
      "16 inch QHD+"
    ],
    "os": [
      "Windows 11 Pro",
      "Windows 11 Home",
      "macOS Ventura"
    ]
  },
  "status": [
    "available",
    "sold_out",
    "discontinued"
  ],
  "categories": [
    {
      "id": "6600a1c3b6f4a2d4e8f3b130",
      "name": "Laptops"
    },
    {
      "id": "6600a1c3b6f4a2d4e8f3b136",
      "name": "Smartphones"
    }
  ]
}
```

### Example
```
GET /api/product-search/filter-options
```

## Error Handling

The API returns appropriate HTTP status codes and error messages for different scenarios:

| Status Code | Description | Possible Causes |
|-------------|-------------|----------------|
| 400 | Bad Request | Invalid parameter format or values |
| 500 | Internal Server Error | Server-side error during processing |

**Error Response Format:**
```json
{
  "message": "Error description"
}
``` 