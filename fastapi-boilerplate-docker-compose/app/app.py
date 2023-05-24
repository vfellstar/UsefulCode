import sys, os
sys.path.append(os.getcwd())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

from modules.documents.upload_handler import save_file
from helper.api_helpers import api_response
from routing.router import router as extra_routes

from modules.redis_connection import RedisConnection
redis_instance = RedisConnection()

from modules.documents.document_factory import DocumentFactory
document_factory = DocumentFactory()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])
app.include_router(extra_routes)

@app.on_event("shutdown")
async def shutdown():
    print("Shutting down...")
    await redis_instance.shutdown()

@app.get("/")
async def root():
    def version_printer():
        import sys
        print(sys.version)
    await redis_instance.acquire_lock_and_run("test", version_printer)
    return api_response({"message": "Hello World"})

@app.post("/upload")
async def upload(request: Request):
    data = await request.form()
    files = []
    # upload files
    for field_name, field_value in data.items():
        file_loc = save_file(field_value)
        files.append({"id": field_name,
                      "location": file_loc})
        
    return api_response({"message": "Upload"})


