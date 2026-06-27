from fastapi import APIRouter

from app.core.constants import APP_ROUTER_TAG_ROOT, ROOT_WELCOME_MESSAGE
from app.shared.responses import RootResponse


router = APIRouter(tags=[APP_ROUTER_TAG_ROOT])


@router.get("/", response_model=RootResponse)
async def read_root() -> RootResponse:
    return RootResponse(message=ROOT_WELCOME_MESSAGE)
