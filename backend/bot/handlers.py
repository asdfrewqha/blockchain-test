import os
import secrets
import string

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile

from backend.bot.keyboards import main_keyboard
from backend.core.dependencies import get_options_votes
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User
from backend.models.pdf_reports import PremiumPDFReportGenerator
from backend.models.poll_analyzer import PollVisualizer
from backend.models.redis_adapter import redis_adapter

router = Router()


class PollStates(StatesGroup):
    WAITING_FOR_POLL_NAME = State()


def generate_secure_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


@router.message(Command("start"))
async def handle_start(message: types.Message):
    existing_code = await redis_adapter.get(f"telegram-id:{message.chat.id}")
    if existing_code:
        await message.answer(f"Ваш код: {existing_code}")
    else:
        code = generate_secure_code()
        await redis_adapter.set(f"telegram-id:{message.chat.id}", code, expire=600)
        await redis_adapter.set(f"telegram-code:{code}", message.chat.id, expire=600)
        await message.answer(f"Ваш код: {code}")
    await message.answer(
        "Напишите /menu чтобы получить меню управления статистикой ваших голосований."
    )


@router.message(Command("menu"))
async def menu(message: types.Message):
    await message.answer(
        "Выберите пункт: ",
        reply_markup=main_keyboard,
    )


@router.callback_query(F.data == "subscribe")
async def watch_polls_callback(callback: types.CallbackQuery):
    await callback.answer()
    user = await adapter.get_by_value(User, "telegram_id", callback.message.chat.id)
    if not user:
        await callback.message.answer("Похоже что вы ещё не зарегистрированы в нашем сервисе.")
    elif not user[0].notifications:
        user = user[0]
        await callback.message.answer(
            "Вы только что подписались на уведомления о завершении ваших голосований.\n\n"
            "Теперь, когда любое ваше голосование завершится, "
            "мы сразу пришлём вам его статистику.\n\n"
            "Спасибо, что остаетесь с нами!"
        )

        await adapter.update_by_id(User, user.id, {"notifications": True})
    else:
        user = user[0]
        await callback.message.answer("Вы отписались от уведомлений. Будем скучать!")
        await adapter.update_by_id(User, user.id, {"notifications": False})


@router.callback_query(F.data == "statistics")
async def statistics_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите название голосования, чтобы узнать статистику по нему.")
    await state.set_state(PollStates.WAITING_FOR_POLL_NAME)


@router.message(PollStates.WAITING_FOR_POLL_NAME)
async def handle_poll_name(message: types.Message, state: FSMContext):
    poll_name = message.text.strip()
    polls = await adapter.find_similar_value(Poll, "name", poll_name, similarity_threshold=70)
    user = await adapter.get_by_value(User, "telegram_id", message.chat.id)
    if not user:
        await message.answer("Похоже что вы ещё не зарегистрированы в нашем сервисе.")
        return None
    if polls:
        user = user[0]
        sent = False
        for poll in polls:
            if poll["user_id"] == user.id:
                if poll["votes_count"] == 0:
                    await message.answer(
                        "В вашем голосовании никто не голосовал, вывести статистику невозможно"
                    )
                    return None
                poll["options"] = await get_options_votes(poll["options"], poll["id"])
                poll_dict = {
                    "id": str(poll["id"]),
                    "name": poll["name"],
                    "votes_count": poll["votes_count"],
                    "user_id": poll["user_id"],
                    "user_username": poll["user_username"],
                    "description": poll["description"],
                    "options": poll["options"],
                }
                if user.role == "PRO":
                    pdf_path = PremiumPDFReportGenerator(poll_dict).generate_pdf_report()
                    file = FSInputFile(pdf_path)
                    await message.answer_document(
                        document=file, caption=f'Статистика вашего опроса "{poll_name}":'
                    )
                    os.remove(pdf_path)
                    sent = True
                else:
                    visualizer = PollVisualizer(poll_dict)
                    graph = visualizer.generate_visual_report()
                    file = FSInputFile(graph)
                    await message.answer_photo(
                        photo=file, caption=f'Статистика вашего опроса "{poll_name}":'
                    )
                    os.remove(graph)
                    sent = True
        if sent:
            return None
        else:
            await message.answer("Нам не удалось найти принадлежащего вам опроса с таким именем")
            return None
    else:
        await message.answer("Голосование с таким названием не найдено.")
    await state.clear()
