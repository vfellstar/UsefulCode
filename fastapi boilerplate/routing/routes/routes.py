from fastapi import Query, Request, UploadFile, APIRouter, File
from starlette.responses import FileResponse


router = APIRouter(
    prefix="/sample_route",
    tags=["Sample Root"],
    responses={404: {"result": "Not found"}},
)

@router.get("/")
async def get_root():
    return {"reached": True}
