from typing import List
from fastapi import Body, FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
import shutil, os

def api_response( payload:dict, success=True):
    return JSONResponse(status_code=200 if success else 400, 
                        content={"status": "success" if success else "failed",
                                 "response": payload})
    
def save_file(upload_file:UploadFile):
    upload_dir = os.getcwd()
    filename = upload_file.filename
    destination = os.path.join(upload_dir, filename)
    
    
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    return destination