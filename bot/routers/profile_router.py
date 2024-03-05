from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from database.models.user import User
from database.models.events import EventRegistration
from database.base import session

from bot.utils.keyboards import MainKeyboards
from bot.utils.keyboards import ProfileKeyboards, EventKeyboards
from bot.utils.utils import gender_to_text, generate_event_text
from bot.states.profile_managment import ManageProfileForm

from configuration import ua_config

profile_router = Router()


async def send_main_profile_info(message: Message, user: User, edit_message: bool = False) -> None:
    gender = gender_to_text(user.gender)
    profile_text = f"{ua_config.get('profile_prompts', 'profile_details').format(username=user.username, full_name=user.full_name or '-', instagram=user.instagram or '-', academic_group=user.academic_group or '-', gender=gender)}"
    reply_markup = ProfileKeyboards.profile_keyboard()
    if not edit_message:
        await message.reply(
            text=profile_text,
            reply_markup=reply_markup
        )
    else:
        await message.bot.edit_message_text(
            text=profile_text,
            reply_markup=reply_markup,
            chat_id=message.chat.id,
            message_id=message.message_id
        )


@profile_router.message(F.text == ua_config.get('buttons', 'profile'))
async def profile_handler(message: Message, user: User, state: FSMContext) -> None:
    await state.clear()
    await send_main_profile_info(message, user)


@profile_router.callback_query(F.data == 'manage_profile')
async def command_start_profile_editing(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ManageProfileForm.full_name)
    await state.update_data(prev_message_id=call.message.message_id)
    await call.message.bot.edit_message_text(text=ua_config.get('profile_prompts', 'enter_full_name'),
                                             message_id=call.message.message_id,
                                             chat_id=call.message.chat.id,
                                             reply_markup=ProfileKeyboards.skip_question_keyboard())


@profile_router.callback_query(F.data == 'validate')
async def process_validate_callback(call: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    data = await state.get_data()
    reply_markup = None
    new_message = False
    text = 'Please use keyboard'
    if current_state == ManageProfileForm.full_name.state:
        await state.update_data(full_name=data.get('reply_info'))
        await state.set_state(ManageProfileForm.academic_group)
        text = ua_config.get('profile_prompts', 'enter_academic_group')
        reply_markup = ProfileKeyboards.skip_question_keyboard()
    elif current_state == ManageProfileForm.academic_group.state:
        await state.update_data(academic_group=data.get('reply_info'))
        await state.set_state(ManageProfileForm.instagram)
        text = ua_config.get('profile_prompts', 'enter_instagram')
        reply_markup = ProfileKeyboards.skip_question_keyboard()
    elif current_state == ManageProfileForm.instagram.state:
        await state.update_data(instagram=data.get('reply_info'))
        await state.set_state(ManageProfileForm.gender)
        text = ua_config.get('profile_prompts', 'enter_gender')
        reply_markup = ProfileKeyboards.gender_keyboard()
        new_message = True

    if new_message:
        await call.message.edit_reply_markup(reply_markup=None)
        message = await call.bot.send_message(chat_id=call.message.chat.id,
                                              text=text, reply_markup=reply_markup)
    else:
        message = await call.bot.edit_message_text(message_id=call.message.message_id,
                                                   chat_id=call.message.chat.id,
                                                   text=text,
                                                   reply_markup=reply_markup)
    await state.update_data(prev_message_id=message.message_id)


@profile_router.callback_query(F.data == 'try_again')
async def process_try_again_callback(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == ManageProfileForm.full_name.state:
        text = ua_config.get('profile_prompts', 'enter_full_name')
    elif current_state == ManageProfileForm.instagram.state:
        text = ua_config.get('profile_prompts', 'enter_instagram')
    elif current_state == ManageProfileForm.academic_group.state:
        text = ua_config.get('profile_prompts', 'enter_academic_group')
    else:
        text = "Unknown state"

    await call.message.edit_reply_markup(reply_markup=None)
    message = await call.bot.edit_message_text(message_id=call.message.message_id,
                                               chat_id=call.message.chat.id,
                                               text=text,
                                               reply_markup=ProfileKeyboards.skip_question_keyboard())
    await state.update_data(prev_message_id=message.message_id)


@profile_router.callback_query(ManageProfileForm.gender)
async def process_gender(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.bot.edit_message_reply_markup(
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
        reply_markup=None
    )
    gender = callback.data if callback.data != 'skip_question' else None
    data = await state.get_data()
    with session() as s:
        telegram_id = callback.from_user.id
        user = s.query(User).filter(User.telegram_id == telegram_id).first()
        user.gender = gender
        user.full_name = data.get('full_name')
        user.academic_group = data.get('academic_group')
        user.instagram = data.get('instagram')

    gender = gender_to_text(user.gender)
    text = (f"{ua_config.get('profile_prompts', 'profile_updated')}\n\n"
            f"{ua_config.get('profile_prompts', 'profile_details').format(username=user.username, full_name=user.full_name or '-', instagram=user.instagram or '-', academic_group=user.academic_group or '-', gender=gender)}")
    await callback.message.answer(text)


@profile_router.message(ManageProfileForm.full_name)
@profile_router.message(ManageProfileForm.academic_group)
@profile_router.message(ManageProfileForm.instagram)
async def process_manage_profile_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    prev_message_id = data.get('prev_message_id')
    print(prev_message_id)
    if prev_message_id:
        await message.bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=prev_message_id,
            reply_markup=None
        )
    await state.update_data(reply_info=message.text)
    await message.reply(ua_config.get(
        'profile_prompts', 'validate_data'
    ).format(data=message.text), reply_markup=ProfileKeyboards.validate_keyboard())


@profile_router.callback_query(ManageProfileForm.full_name)
@profile_router.callback_query(ManageProfileForm.academic_group)
@profile_router.callback_query(ManageProfileForm.instagram)
async def process_manage_profile_reply(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'skip_question':
        await state.update_data(reply_info=None)
        message = await callback.message.bot.edit_message_text(
            text=ua_config.get('profile_prompts', 'validate_skip_data'),
            reply_markup=ProfileKeyboards.validate_keyboard(),
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id
        )
        await state.update_data(prev_message_id=message.message_id)


@profile_router.callback_query(F.data == 'my_events')
async def my_events_handler(callback: CallbackQuery, state: FSMContext) -> None:
    my_events = []
    with session() as s:
        registrations = s.query(EventRegistration).filter(EventRegistration.user_id == callback.from_user.id).limit(5)
        for registration in registrations:
            my_events.append(
                [registration.id, registration.event.title]
            )
    await callback.message.bot.edit_message_text(
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
        text=ua_config.get('profile_prompts', 'my_events'),
        reply_markup=EventKeyboards.generate_my_event_list(my_events)
    )


@profile_router.callback_query(F.data.startswith('my_event_select_'))
async def my_event_selection_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id
    )
    registration_id = int(callback.data.split('_')[-1])
    with session() as s:
        registration = s.query(EventRegistration).filter(EventRegistration.id == registration_id).first()
        event = registration.event
    title = event.title
    description = event.description
    final_text = await generate_event_text(title, description)
    current_status = ua_config.get('profile_prompts',
                                   'registration_approved') if registration.is_approved else ua_config.get(
        'profile_prompts', 'registration_awaiting_approval')
    final_text = f'{final_text}\n\n*{current_status}*'
    await callback.message.bot.send_photo(
        chat_id=callback.message.chat.id,
        caption=final_text,
        photo=event.photo,
        reply_markup=EventKeyboards.generate_my_event_list([], 'my_event_back'),
        parse_mode=ParseMode.MARKDOWN_V2
    )


@profile_router.callback_query(F.data == 'profile_back')
async def profile_back_handler(callback: CallbackQuery, state: FSMContext) -> None:
    with session() as s:
        user = s.query(User).filter(User.telegram_id == callback.from_user.id).first()
    await send_main_profile_info(message=callback.message, user=user, edit_message=True)


@profile_router.callback_query(F.data == 'my_event_back')
async def my_event_back_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id
    )
    my_events = []
    with session() as s:
        registrations = s.query(EventRegistration).filter(EventRegistration.user_id == callback.from_user.id)
        for registration in registrations:
            my_events.append(
                [registration.id, registration.event.title]
            )
    await callback.message.answer(
        text=ua_config.get('profile_prompts', 'my_events'),
        reply_markup=EventKeyboards.generate_my_event_list(my_events)
    )
