from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user, get_options_votes
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User, Vote
from backend.models.schemas import PollSchema

router = APIRouter()


@router.get("/get-polls-by-username/{username}")
async def get_poll_by_user_id(username: str, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    if not username.startswith("@"):
        username = "@" + username

    polls = await adapter.get_by_value(Poll, "user_username", username)
    now = datetime.now(timezone.utc)
    result: list[PollSchema] = []

    for poll in polls:
        poll_sch = PollSchema.model_validate(poll)
        poll_sch.is_active = bool(poll.start_date < now and now < poll.end_date)

        if user.username == username:
            poll_sch.options = await get_options_votes(poll_sch.options, poll.id)
            result.append(poll_sch)
            continue

        if now > poll.end_date:
            poll_sch.options = await get_options_votes(poll_sch.options, poll.id)

        if user and not user.id == poll.user_id:
            vote = await adapter.get_by_values(Vote, {"user_id": user.id, "poll_id": poll.id})
            is_private = poll.private
            if vote and not is_private:
                poll_sch.is_voted = True
                result.append(poll_sch)
                continue

        if not poll.private:
            result.append(poll_sch)

    return result
