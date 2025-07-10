from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User, Vote
from backend.routes.polls.tasks import enqueue_notify_author, enqueue_notify_user

router = APIRouter()

@router.post("/end-poll/{poll_id}")
async def end_vote(poll_id: UUID, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    poll = await adapter.get_by_id(Poll, poll_id)
    if not poll:
        return badresponse("Poll not found", 404)
    if poll.user_id != user.id:
        return badresponse("You are not the owner of this poll", 403)
    poll.end_date = datetime.now(timezone.utc)
    await adapter.update_by_id(Poll, poll_id, {"end_date": poll.end_date})
    await enqueue_notify_author(user.telegram_id, poll_id, 0.0)
    votes = await adapter.get_by_value(Vote, "poll_id", poll_id)
    if votes:
        for vote in votes:
            if vote.notification:
                await enqueue_notify_user(user_id=vote.user_id, poll_id=poll_id, delay=0.0)
    return okresp(200, "Poll ended")
