from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends

from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User, Vote
from backend.routes.polls.tasks import enqueue_notify_user

router = APIRouter()


@router.post("/vote/{poll_id}", status_code=201)
async def vote(
    user: Annotated[User, Depends(check_user)],
    poll_id: UUID,
    notification: bool,
    option: str = Body(...),
):
    if not user:
        return badresponse("Unauthorized", 401)
    poll = await adapter.get_by_id(Poll, poll_id)
    if not poll:
        return badresponse("Poll not found", 404)
    if poll.user_id == user.id:
        return badresponse("You can't vote in your polls", 403)
    now = datetime.now(timezone.utc)
    if poll.end_date < now:
        return badresponse("Poll closed")
    if poll.start_date > now:
        return badresponse("Poll is not started")
    existing_vote = await adapter.get_by_values(Vote, {"user_id": user.id, "poll_id": poll_id})
    if existing_vote != []:
        return badresponse("You have already voted", 409)
    if option not in poll.options:
        return badresponse("Invalid option")
    votes = poll.votes_count
    await adapter.update_by_id(Poll, poll_id, {"votes_count": votes + 1})
    if notification:
        delay = (poll.end_date - datetime.now(timezone.utc)).total_seconds()
        await enqueue_notify_user(user.id, poll_id, delay)
        await adapter.insert(Vote, {"user_id": user.id, "poll_id": poll_id, "notification": True})
    else:
        await adapter.insert(Vote, {"user_id": user.id, "poll_id": poll_id})
    return okresp(201)
