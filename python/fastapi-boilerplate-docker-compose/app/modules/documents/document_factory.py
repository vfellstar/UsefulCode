import pickle
from modules.documents.factory_products.document import Document
from modules.redis_connection import RedisConnection
from modules.documents.monitors.id_monitor import DocIDMonitor
from modules.documents.monitors.lifetime_monitor import Lifetime


class DocumentFactory():
    __instance = None
    __redis = None
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__id_monitor = DocIDMonitor()
            cls.__lifetime_monitor = Lifetime()
            
        return cls.__instance
    
    @classmethod
    def create_document(cls, document_id, document_location):
        if cls.__id_monitor.is_id_used(document_id):
            raise IDNotUniqueException("Document ID already used")
        return Document(document_id, document_location)
    
    
class IDNotUniqueException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
        