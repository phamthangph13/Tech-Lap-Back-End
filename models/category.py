from bson import ObjectId
from datetime import datetime

class Category:
    def __init__(self, name, description=None, _id=None, created_at=None, updated_at=None):
        self._id = _id or ObjectId()
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get('_id'),
            name=data.get('name'),
            description=data.get('description'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 