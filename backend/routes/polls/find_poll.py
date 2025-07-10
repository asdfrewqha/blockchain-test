from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User, Vote
from backend.models.schemas import PollSchema, SearchPollSchema

router = APIRouter()


async def check_poll_status(poll: Poll, poll_status: Optional[str]) -> bool:
    """Проверяет статус опроса (open/closed)"""
    now = datetime.now(timezone.utc)
    if poll_status in ["all", None]:
        return True
    if poll_status == "open" and poll.start_date <= now <= poll.end_date:
        return True
    if poll_status == "closed" and now > poll.end_date:
        return True
    return False


async def check_vote_status(poll: Poll, vote_status: Optional[str], user_id: UUID) -> bool:
    """Проверяет статус голосования пользователя"""
    if vote_status in ["all", None]:
        return True
    
    votes = await adapter.get_by_values(Vote, {"user_id": user_id, "poll_id": poll.id})
    has_voted = len(votes) > 0 

    if vote_status == "voted" and has_voted:
        return True
    if vote_status == "not_voted" and not has_voted:
        return True
    return False


async def prepare_poll_response(poll: Poll, user: User) -> PollSchema:
    """Подготавливает опрос для ответа, учитывая права доступа"""
    now = datetime.now(timezone.utc)
    poll_sch = PollSchema.model_validate(poll)

    if isinstance(poll, dict):
        poll_id = poll["id"]
        start_date = poll["start_date"]
        end_date = poll["end_date"]
        user_id_val = poll["user_id"]
        options = poll["options"]
    else:
        poll_id = poll.id
        start_date = poll.start_date
        end_date = poll.end_date
        user_id_val = poll.user_id
        options = poll.options

    poll_sch.is_active = start_date <= now <= end_date

    votes = await adapter.get_by_values(Vote, {"user_id": user.id, "poll_id": poll_id})
    poll_sch.is_voted = len(votes) > 0

    if user.id != user_id_val and now < end_date:
        poll_sch.options = list(options.keys()) if options else []

    return poll_sch


@router.post("/search-polls")
async def search_polls(user: Annotated[User, Depends(check_user)], search_params: SearchPollSchema):
    if not user:
        return badresponse("Unauthorized", 401)

    if search_params.voting_status not in ["all", "voted", "not_voted", None]:
        return badresponse("Invalid voting status", 400)
    if search_params.sort_by not in ["popularity_asc", "popularity_desc", None]:
        return badresponse("Invalid sorting", 400)
    if search_params.poll_status not in ["all", "open", "closed", None]:
        return badresponse("Invalid poll status", 400)

    if search_params.poll_name:
        polls = await adapter.find_similar_value(
            Poll, "name", search_params.poll_name, similarity_threshold=40
        )
    else:
        polls = await adapter.get_all(Poll)

    filtered_polls = []
    for poll in polls:
        if isinstance(poll, dict):
            is_private = poll["private"]
            user_id_val = poll["user_id"]
        else:
            is_private = poll.private
            user_id_val = poll.user_id

        if is_private:
            continue

        # if is_private and user_id_val != user.id:
        #     continue

        if not await check_vote_status(poll, search_params.voting_status, user.id):
            continue

        if not await check_poll_status(poll, search_params.poll_status):
            continue

        if search_params.tags:
            poll_tags = poll["hashtags"] if isinstance(poll, dict) else poll.hashtags
            poll_tags = poll_tags or []
            if not set(search_params.tags).issubset(set(poll_tags)):
                continue

        filtered_polls.append(poll)

    if filtered_polls:
        if search_params.sort_by == "popularity_asc":
            if isinstance(filtered_polls[0], dict):
                filtered_polls.sort(key=lambda x: x["votes_count"])
            else:
                filtered_polls.sort(key=lambda x: x.votes_count)
        elif search_params.sort_by == "popularity_desc":
            if isinstance(filtered_polls[0], dict):
                filtered_polls.sort(key=lambda x: x["votes_count"], reverse=True)
            else:
                filtered_polls.sort(key=lambda x: x.votes_count, reverse=True)
    else:
        return badresponse("Polls not found", 404)

    result = [await prepare_poll_response(poll, user) for poll in filtered_polls]
    return result
