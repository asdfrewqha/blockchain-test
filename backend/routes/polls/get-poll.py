import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user, get_options_votes
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User, Vote
from backend.models.schemas import PollSchema

router = APIRouter()


@router.get("/get-poll/{poll_id}", response_model=PollSchema)
async def get_poll_by_id(poll_id: uuid.UUID, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    poll = await adapter.get_by_id(Poll, id=poll_id)
    if not poll:
        return badresponse("Poll not found", 404)
    poll_sch = PollSchema.model_validate(poll)
    now = datetime.now(timezone.utc)
    if poll.user_id == user.id or poll.end_date < now:
        poll_sch.options = await get_options_votes(poll_sch.options, poll.id)
    if poll.start_date < now and poll.end_date > now:
        poll_sch.is_active = True
    if not user.id == poll.user_id:
        vote = await adapter.get_by_values(Vote, {"user_id": user.id, "poll_id": poll_id})
        if vote:
            poll_sch.is_voted = True
    return poll_sch
