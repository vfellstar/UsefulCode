from fastapi import APIRouter
from routing.routes import sample_route
from routing.routes import settings_route


router = APIRouter()
router.include_router(sample_route.router)
router.include_router(settings_route.router)
