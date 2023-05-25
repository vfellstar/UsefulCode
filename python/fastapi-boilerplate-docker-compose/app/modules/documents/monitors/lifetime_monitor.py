import pickle
import pandas as pd
from modules.redis_connection import RedisConnection
from modules.documents.factory_products.document import Document
from etc.env_settings import Setting

class Lifetime():
    __instance = None
    __redis = None
    __redis_key = Setting.REDIS_KEYS.value
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__redis = RedisConnection().redis
            cls.__redis_key = cls.__redis_key["lifetime_monitor"]
            cls.__initialise()
        return cls.__instance
    
    @classmethod
    def __initialise(cls):
        if cls.__redis.exists(cls.__redis_key) == 0:
            data = []
            cls.__redis.set(cls.__redis_key, pickle.dumps(data))
        pickle.loads(cls.__redis.get(cls.__redis_key))
    
    @classmethod
    def get_data(cls):
        return pickle.loads(cls.__redis.get(cls.__redis_key))
    
    @classmethod
    async def add_document(cls, document:Document):
        data = {}
        data["id"] = document.id
        data["location"] = document.location
        data["lifetime"] = document.lifetime
    