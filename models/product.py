from bson import ObjectId
from datetime import datetime

class Product:
    def __init__(self, name, brand, model, price, discount_percent, specs, 
                 stock_quantity, category_ids=None, thumbnail=None, images=None, videos=None, 
                 status="available", variant_specs=None, colors=None, product_info=None, 
                 highlights=None, short_description=None, _id=None, created_at=None, updated_at=None):
        self._id = _id or ObjectId()
        self.name = name
        self.brand = brand
        self.model = model
        self.price = price
        self.discount_percent = discount_percent
        self.discount_price = price - (price * discount_percent / 100)
        self.specs = specs
        self.variant_specs = variant_specs or []
        self.colors = colors or []
        self.stock_quantity = stock_quantity
        self.category_ids = category_ids or []
        self.thumbnail = thumbnail
        self.images = images or []
        self.videos = videos or []
        self.product_info = product_info or []
        self.highlights = highlights or []
        self.short_description = short_description
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
            variant_specs=data.get('variant_specs'),
            colors=data.get('colors'),
            stock_quantity=data.get('stock_quantity'),
            category_ids=data.get('category_ids'),
            thumbnail=data.get('thumbnail'),
            images=data.get('images'),
            videos=data.get('videos'),
            product_info=data.get('product_info'),
            highlights=data.get('highlights'),
            short_description=data.get('short_description'),
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
            "variant_specs": self.variant_specs,
            "colors": self.colors,
            "stock_quantity": self.stock_quantity,
            "category_ids": self.category_ids,
            "thumbnail": self.thumbnail,
            "images": self.images,
            "videos": self.videos,
            "product_info": self.product_info,
            "highlights": self.highlights,
            "short_description": self.short_description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status
        } 