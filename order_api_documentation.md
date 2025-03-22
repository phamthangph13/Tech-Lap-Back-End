# Order API Documentation

This document describes the endpoints for managing orders in the system.

## Collection Schema: Orders

```javascript
{
  _id: ObjectId,
  orderNumber: String, // TS-YYYYMMDD-XXX
  customer: {
    fullName: String,
    phone: String,
    email: String
  },
  shippingAddress: {
    province: String,
    district: String,
    ward: String,
    streetAddress: String
  },
  items: [
    {
      productId: ObjectId,
      productName: String,
      basePrice: Number,
      
      // Variant selection (configuration)
      variantName: String,          // e.g., "APPLE M3"
      variantSpecs: {
        cpu: String,
        ram: String,
        storage: String,
        display: String,
        gpu: String,
        battery: String,
        os: String,
        ports: [String]
      },
      variantPrice: Number,         // Price specific to variant
      variantDiscountPercent: Number,
      
      // Color selection
      colorName: String,            // e.g., "Silver", "Black"
      colorCode: String,            // e.g., "#cfc9c9"
      colorPriceAdjustment: Number, // Additional cost for this color
      colorDiscountAdjustment: Number,
      
      quantity: Number,
      
      // Price calculations
      unitPrice: Number,            // Final unit price after variant and color
      discountedPrice: Number,      // Price after discount
      subtotal: Number,             // discountedPrice * quantity
      
      // Product image for order reference
      thumbnailUrl: String
    }
  ],
  payment: {
    method: String,                 // "COD"
    status: String                  // "pending", "paid"
  },
  productInfo: [                    // Copy of product_info for order record
    {
      title: String,
      content: String
    }
  ],
  subtotal: Number,                 // Sum of all item subtotals
  discountTotal: Number,            // Total discount amount
  shippingFee: Number,
  total: Number,                    // subtotal + shippingFee
  status: String,                   // "pending", "processing", "shipped", "delivered", "cancelled"
  orderDate: Date,
  updatedAt: Date
}
```

## Endpoints

### Create Order

Creates a new order in the system.

**URL**: `/api/orders`

**Method**: `POST`

**Auth required**: No

**Request Body**:

```json
{
  "customer": {
    "fullName": "Nguyễn Văn A",
    "phone": "0901234567",
    "email": "nguyenvana@example.com"
  },
  "shippingAddress": {
    "province": "Hồ Chí Minh",
    "district": "Quận 1",
    "ward": "Phường Bến Nghé",
    "streetAddress": "123 Nguyễn Huệ"
  },
  "items": [
    {
      "productId": "67deaf2d7457268626f9e0eb",
      "quantity": 1,
      "variantName": "APPLE M3",
      "colorName": "Silver"
    }
  ],
  "payment": {
    "method": "COD"
  }
}
```

#### Success Response

**Code**: `201 CREATED`

**Content example**:

```json
{
  "success": true,
  "message": "Order created successfully",
  "data": {
    "orderId": "60d21b4667d0d8992e610c85",
    "orderNumber": "TS-20230724-001",
    "items": [
      {
        "productName": "MacBook Pro 16",
        "variantName": "APPLE M3",
        "colorName": "Silver",
        "quantity": 1,
        "unitPrice": 75170000,
        "discountedPrice": 71411500,
        "subtotal": 71411500
      }
    ],
    "subtotal": 71411500,
    "shippingFee": 0,
    "total": 71411500,
    "status": "pending"
  }
}
```

#### Error Response

**Condition**: If the request is invalid or validation fails.

**Code**: `400 BAD REQUEST`

**Content example**:

```json
{
  "success": false,
  "message": "Failed to create order",
  "errors": [
    "Product not found",
    "Requested variant not available for product MacBook Pro 16",
    "Requested color not available for product MacBook Pro 16"
  ]
}
```

### Notes

1. The API automatically sets quantity to 1 if an invalid (zero or negative) quantity is provided.
2. The final price calculation includes:
   - Base product price (from product.price)
   - Variant price (additional cost for the specific variant)
   - Color price adjustment (additional cost for the specific color)
   - Discounts from both variant and color
3. All product information needed for the order is stored with the order at creation time, including:
   - Product details
   - Variant specifications
   - Color information
   - Pricing details
4. Shipping is currently set to free (0 VND) for all orders. 