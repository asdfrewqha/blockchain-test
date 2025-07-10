from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.schemas import Role

router = APIRouter()


@router.post("/get-pro-subscribe")
async def get_pro_subcribe(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    if user.role == Role.PRO:
        return {"message": "You are already a PRO user"}
    await adapter.update_by_id(User, user.id, {"role": Role.PRO.value})
    return okresp(200, "You are now a PRO user")
