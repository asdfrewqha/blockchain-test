from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User
from backend.models.schemas import NewPoll
from backend.routes.polls.tasks import enqueue_notify_author

router = APIRouter()


@router.post("/create-poll")
async def create_poll(user: Annotated[User, Depends(check_user)], poll: NewPoll):
    if not user:
        return badresponse("Unauthorized", 401)
    options = {}
    if len(poll.options) < 2:
        return badresponse("Too few options")
    elif len(poll.options) > 10:
        return badresponse("Too many options")
    elif len(poll.options) != len(set(poll.options)):
        return badresponse("Duplicating options")
    hashtags = [i.replace("#", "") for i in poll.description.split() if i.startswith("#")]
    new_poll_obj = {
        "name": poll.name,
        "description": poll.description,
        "user_id": user.id,
        "user_username": user.username,
        "options": options,
        "start_date": poll.start_date,
        "end_date": poll.end_date,
        "private": poll.private,
        "hashtags": hashtags,
    }
    new_poll_db = await adapter.insert(Poll, new_poll_obj)
    delay = (new_poll_db.end_date - datetime.now(timezone.utc)).total_seconds()
    await enqueue_notify_author(user.telegram_id, new_poll_db.id, delay)
    return okresp(201, str(new_poll_db.id))
