from enum import Enum
import os

class Setting(Enum):
    
    DATETIME_FORMAT_FOR_VECTORDB = "%Y-%m-%dT%H:%M:%S+00:00"
    
    # External Services
    WEAVIATE_HOST = os.getenv("WEAVIATE_HOST")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    REDIS_DB   = os.getenv("REDIS_DB", 0)   
     
    # Internal paths
    UPLOAD_DIR = os.path.join(os.getcwd(), "etc/uploads")
    STORED_DIR = os.path.join(os.getcwd(), "etc/stored")
    APPDATA_DIR = os.path.join(os.getcwd(), "etc/appdata")
    if not os.path.isdir(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)
    if not os.path.isdir(STORED_DIR):
        os.mkdir(STORED_DIR)
    if not os.path.isdir(APPDATA_DIR):
        os.mkdir(APPDATA_DIR)
    
    # Allowed file types
    ALLOWED_FILE_TYPES = [".pdf", ".docx", ".txt", ".html"]
    

    # Default Settings
    DEFAULT_APP_SETTINGS = {
        "split_pdf": "headers",
        "month_retention": 90
    }
    
    DEFAULT_APP_SETTINGS_VALIDATION = {
        "split_pdf": {
            "valid_values": ['headers', 'header', 'h', 'page', 'pages']
        },
        "month_retention": {
            "min": 1,
            "max": 9999999999999999999999999,
        }
    }
    
    REDIS_KEYS = {
        "lifetime_monitor": "document_lifetime_obj74987985723",
        "doc_id_monitor": "doc_id_df974985743",
    }