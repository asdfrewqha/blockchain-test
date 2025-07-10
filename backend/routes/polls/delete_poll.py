from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User

router = APIRouter()


@router.delete("/delete-poll/{poll_id}")
async def delete_poll(poll_id: UUID, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    poll = await adapter.get_by_id(Poll, poll_id)
    if user.id != poll.user_id:
        return badresponse("You are not the owner of this poll", 403)
    await adapter.delete(Poll, poll_id)
    return okresp(204, "Poll deleted")
