from typing import List
from fastapi import Body, FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
import shutil, os

def api_response( payload:dict, success=True):
    return JSONResponse(status_code=200 if success else 400, 
                        content={"status": "success" if success else "failed",
                                 "response": payload})
    
    