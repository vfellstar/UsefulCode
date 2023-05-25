from fastapi import Query, Request, UploadFile, APIRouter, File
from starlette.responses import FileResponse
from helper.api_helpers import api_response


router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
    responses={404: {"result": "Not found"}},
)

@router.get("/")
async def get_root():
    return api_response(payload={"route": "Settings"}, success=True)
