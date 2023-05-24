from fastapi import APIRouter
from routing.routes import sample_route


router = APIRouter()
router.include_router(sample_route.router)
