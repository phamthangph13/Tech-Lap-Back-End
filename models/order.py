from datetime import datetime
from bson import ObjectId

# Order model definition
class Order:
    def __init__(self, 
                 order_number=None,
                 customer=None,
                 shipping_address=None,
                 items=None,
                 payment=None,
                 product_info=None,
                 subtotal=0,
                 discount_total=0,
                 shipping_fee=0,
                 total=0,
                 status="pending",
                 order_date=None,
                 updated_at=None):
        
        self.order_number = order_number
        self.customer = customer or {}
        self.shipping_address = shipping_address or {}
        self.items = items or []
        self.payment = payment or {"method": "COD", "status": "pending"}
        self.product_info = product_info or []
        self.subtotal = subtotal
        self.discount_total = discount_total
        self.shipping_fee = shipping_fee
        self.total = total
        self.status = status
        self.order_date = order_date or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            "order_number": self.order_number,
            "customer": self.customer,
            "shipping_address": self.shipping_address,
            "items": self.items,
            "payment": self.payment,
            "product_info": self.product_info,
            "subtotal": self.subtotal,
            "discount_total": self.discount_total,
            "shipping_fee": self.shipping_fee,
            "total": self.total,
            "status": self.status,
            "order_date": self.order_date,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            order_number=data.get("order_number"),
            customer=data.get("customer"),
            shipping_address=data.get("shipping_address"),
            items=data.get("items"),
            payment=data.get("payment"),
            product_info=data.get("product_info"),
            subtotal=data.get("subtotal", 0),
            discount_total=data.get("discount_total", 0),
            shipping_fee=data.get("shipping_fee", 0),
            total=data.get("total", 0),
            status=data.get("status", "pending"),
            order_date=data.get("order_date"),
            updated_at=data.get("updated_at")
        ) 