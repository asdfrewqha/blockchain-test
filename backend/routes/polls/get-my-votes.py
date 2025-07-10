from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user, get_options_votes
from backend.models.db_adapter import adapter
from backend.models.db_tables import User
from backend.models.schemas import PollSchema

router = APIRouter()


@router.get("/get-my-votes")
async def get_my_votes(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    user_polls = await adapter.get_polls_voted_by_user(user.id)
    print(user_polls)
    polls_sch = []
    for poll in user_polls:
        poll_sch = PollSchema.model_validate(poll)
        poll_sch.is_voted = True
        now = datetime.now(timezone.utc)
        if poll.end_date > now and poll.start_date < now:
            poll_sch.is_active = True
        if poll.end_date < now:
            poll_sch.options = await get_options_votes(poll_sch.options, poll.id)
        polls_sch.append(poll_sch)
    return polls_sch
