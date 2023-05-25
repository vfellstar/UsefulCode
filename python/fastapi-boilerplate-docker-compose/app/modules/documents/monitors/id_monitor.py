import pickle
import pandas as pd
from modules.redis_connection import RedisConnection
from etc.env_settings import Setting

class DocIDMonitor():
    __instance = None
    __redis = None
    __redis_key = Setting.REDIS_KEYS.value
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__redis = RedisConnection().redis
            cls.__redis_key = cls.__redis_key["doc_id_monitor"]
            cls.__initialise()
            
        return cls.__instance
    
    @classmethod
    def __initialise(cls):
        if cls.__redis.exists(cls.__redis_key) == 0:
            ids = []
            cls.__redis.set(cls.__redis_key, pickle.dumps(ids))
        pickle.loads(cls.__redis.get(cls.__redis_key))
    
    @classmethod
    def __get_id(cls):
        return pickle.loads(cls.__redis.get(cls.__redis_key))
    
    @classmethod
    def is_id_used(cls, obj_id:str):
        return  obj_id in cls.__get_id()
    