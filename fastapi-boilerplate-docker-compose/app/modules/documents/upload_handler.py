import os, shutil
from etc.env_settings import Setting

from fastapi import UploadFile

def save_file(upload_file:UploadFile):
    upload_dir = Setting.UPLOAD_DIR.value
    filename = upload_file.filename
    destination = os.path.join(upload_dir, filename)
    
    
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    return destination

