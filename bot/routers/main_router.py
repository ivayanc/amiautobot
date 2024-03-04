from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command

from database.models.user import User

from bot.utils.keyboards import MainKeyboards
from bot.routers.profile_router import profile_router
from bot.routers.faq_router import faq_router
from bot.routers.admin_event_router import admin_event_router
from bot.routers.event_register_router import event_router

from configuration import ua_config

main_router = Router()
main_router.include_router(profile_router)
main_router.include_router(faq_router)
main_router.include_router(admin_event_router)
main_router.include_router(event_router)


async def send_welcome_message(message: Message, edit_message: bool = False) -> None:
    reply_keyboard = MainKeyboards.default_keyboard()
    welcome_text = ua_config.get('prompts', 'start_message')
    if edit_message:
        await message.bot.delete_message(chat_id=message.chat.id,
                                         message_id=message.message_id)
    await message.answer(welcome_text, reply_markup=reply_keyboard)


@main_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await send_welcome_message(message)


@main_router.message(F.text == ua_config.get('buttons', 'help'))
@main_router.message(Command(commands=['help']))
async def command_start_handler(message: Message) -> None:
    await message.answer(ua_config.get('prompts', 'help_message'))


@main_router.callback_query(F.data == 'close')
async def command_start_handler(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await send_welcome_message(call.message, edit_message=True)


@main_router.message(F.text == ua_config.get('buttons', 'tumbochka'))
async def command_start_handler(message: Message) -> None:
    await message.answer(ua_config.get('prompts', 'tumbochka_empty'), reply_markup=MainKeyboards.tumbochka_keyboard())
