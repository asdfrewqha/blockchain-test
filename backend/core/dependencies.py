import logging
from uuid import UUID

from fastapi import Security
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer
from httpx import AsyncClient

from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.token_manager import TokenManager

Bear = HTTPBearer(auto_error=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_options_votes(options: list, poll_id: UUID) -> dict:
    async with AsyncClient() as client:
        params = {"options": options, "topic_id": poll_id}
        response = await client.get("http://blockchain:2000/votes", params=params)
        data = response.json()
    return dict(data)


async def check_user(access_token: str = Security(Bear)):
    if not access_token or not access_token.credentials:
        logger.error("No token")
        return False

    data = TokenManager.decode_token(access_token.credentials)
    if not data:
        logger.error("No token data")
        return False

    if not data.get("sub") or not data.get("type"):
        logger.error("Invalid token data")
        return False

    if data["type"] != "access":
        logger.error("Invalid token type")
        return False

    user = await adapter.get_by_id(User, data["sub"])
    if user:
        return user

    logger.error("No user for this token")
    return False


def badresponse(msg, code: int = 400, status: str = "error"):
    return JSONResponse(content={"msg": msg, "status": status}, status_code=code)


def okresp(code: int = 200, message: str = None):
    if not message:
        return Response(status_code=code)
    else:
        return JSONResponse(content={"message": message, "status": "success"}, status_code=code)
