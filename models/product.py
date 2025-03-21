from bson import ObjectId
from datetime import datetime

class Product:
    def __init__(self, name, brand, model, price, discount_percent, specs, 
                 stock_quantity, category_ids=None, thumbnail=None, images=None, videos=None, 
                 status="available", _id=None, created_at=None, updated_at=None):
        self._id = _id or ObjectId()
        self.name = name
        self.brand = brand
        self.model = model
        self.price = price
        self.discount_percent = discount_percent
        self.discount_price = price - (price * discount_percent / 100)
        self.specs = specs
        self.stock_quantity = stock_quantity
        self.category_ids = category_ids or []
        self.thumbnail = thumbnail
        self.images = images or []
        self.videos = videos or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.status = status
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get('_id'),
            name=data.get('name'),
            brand=data.get('brand'),
            model=data.get('model'),
            price=data.get('price'),
            discount_percent=data.get('discount_percent'),
            specs=data.get('specs'),
            stock_quantity=data.get('stock_quantity'),
            category_ids=data.get('category_ids'),
            thumbnail=data.get('thumbnail'),
            images=data.get('images'),
            videos=data.get('videos'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            status=data.get('status')
        )
    
    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "brand": self.brand,
            "model": self.model,
            "price": self.price,
            "discount_percent": self.discount_percent,
            "discount_price": self.discount_price,
            "specs": self.specs,
            "stock_quantity": self.stock_quantity,
            "category_ids": self.category_ids,
            "thumbnail": self.thumbnail,
            "images": self.images,
            "videos": self.videos,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status
        } 