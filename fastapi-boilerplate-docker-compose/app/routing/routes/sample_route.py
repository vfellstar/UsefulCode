from fastapi import Query, Request, UploadFile, APIRouter, File
from starlette.responses import FileResponse
from helper.api_helpers import api_response


router = APIRouter(
    prefix="/sample_route",
    tags=["Sample Root"],
    responses={404: {"result": "Not found"}},
)

@router.get("/")
async def get_root():
    return api_response(payload={"reached": True}, success=True)
