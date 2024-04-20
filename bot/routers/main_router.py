from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.utils.deep_linking import decode_payload

from database.models.user import User

from bot.utils.keyboards import MainKeyboards
from bot.routers.profile_router import profile_router
from bot.routers.faq_router import faq_router
from bot.routers.admin_event_router import admin_event_router
from bot.routers.event_register_router import event_router, send_event_registration

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
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args
    if args and 'event_select_' in args:
        event_id = int(args.split('_')[-1])
        await send_event_registration(event_id=event_id, message=message, back_button=False)
    elif args and 'uniweek' in args:
        await message.bot.send_photo(chat_id=message.chat.id, caption=ua_config.get('uniweek', 'uniweek_test'),
                                     photo='https://marbled-equinox-e70.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F60786ec7-afcf-40c9-89e0-063dc40af5f5%2F97a12e0c-5794-4bee-858d-6e6d6e0056f4%2F%25D0%2597%25D0%25BD%25D1%2596%25D0%25BC%25D0%25BE%25D0%25BA_%25D0%25B5%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0_2024-04-19_014732.png?table=block&id=f41b32cb-6429-493d-9ffc-51faf294e053&spaceId=60786ec7-afcf-40c9-89e0-063dc40af5f5&width=2000&userId=&cache=v2')
    else:
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
