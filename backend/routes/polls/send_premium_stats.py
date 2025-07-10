import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User
from backend.models.pdf_reports import PremiumPDFReportGenerator
from backend.models.schemas import PollSchema

router = APIRouter()


@router.get("/send-premium-stats/{poll_id}")
async def send_premium_stats(user: Annotated[User, Depends(check_user)], poll_id: uuid.UUID):
    if not user:
        return badresponse("Unauthorized", 401)
    poll = await adapter.get_by_id(Poll, id=poll_id)
    if not poll:
        return badresponse("Poll not found", 404)
    if poll.user_id != user.id:
        return badresponse("You are not the owner of this poll", 403)
    if user.role != "PRO":
        return badresponse("You need to be a PRO user to access this feature", 403)
    poll = PollSchema.model_validate(poll).model_dump()
    pdf_path = PremiumPDFReportGenerator(poll).generate_pdf_report()

    # Добавьте filename для красивого имени файла при скачивании
    return FileResponse(
        pdf_path, media_type="application/pdf", filename=f"poll_report_{poll_id}.pdf"
    )
