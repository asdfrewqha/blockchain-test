import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.config import DEFAULT_AVATAR_URL
from backend.core.dependencies import badresponse, check_user, okresp
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User
from backend.models.s3_adapter import s3
from backend.models.schemas import UpdateProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


def is_valid(username):
    if (
        len(username) < 4
        or len(username) > 20
        or len(
            [i for i in ["#", "!", "&", "?", "/", "|", "\\", "`", "~", ":", ";"] if i in username]
        )
        != 0
        or username.count("@") != 1
    ):
        return False
    return True


@router.put("/update-profile")
async def upd_profile(user: Annotated[User, Depends(check_user)], update: UpdateProfile):
    if not user:
        return badresponse("Unauthorized", 401)

    updated_data = {}
    uid = user.id

    if update.name:
        updated_data["name"] = update.name

    if update.username:
        if not update.username.startswith("@"):
            update.username = f"@{update.username}"
        updated_data["username"] = update.username
        if not is_valid(updated_data["username"]):
            return badresponse("Invalid username", 400)
        if user.username != update.username:
            existing_username = await adapter.get_by_value(User, "username", update.username)
            if not existing_username:
                updated_data["username"] = update.username
                if user.avatar_url != DEFAULT_AVATAR_URL:
                    old_pfp = f"{user.username}/avatar_{uid}.png"
                    new_pfp = f"{update.username}/avatar_{uid}.png"
                    try:
                        await s3.copy_file(old_pfp, new_pfp)
                        await s3.delete_file(old_pfp)
                        public_url = s3.get_url(new_pfp)
                        await adapter.update_by_id(User, uid, {"avatar_url": public_url})
                    except Exception as e:
                        logger.error(f"Ошибка при перемещении аватара: {e}")
                await adapter.update_by_value(
                    Poll,
                    {"user_username": user.username},
                    {"user_username": update.username},
                )
            else:
                return badresponse("This username is already taken", 409)

    if update.description:
        updated_data["description"] = update.description

    if not updated_data:
        return badresponse("No fields provided")

    await adapter.update_by_id(User, uid, updated_data)
    return okresp(message="Profile updated successfully")
