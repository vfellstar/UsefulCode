import sys, os
sys.path.append(os.getcwd())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

from helpers.helpers import save_file, api_response
from routing.router import router as extra_routes

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

@app.get("/")
async def root():
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


