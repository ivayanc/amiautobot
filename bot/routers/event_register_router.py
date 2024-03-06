from __future__ import annotations

from typing import Optional

from aiogram import Router, F

from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.types.chat_join_request import ChatJoinRequest
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods.delete_message import DeleteMessage
from aiogram.methods.ban_chat_member import BanChatMember

from sqlalchemy import select

from database.models.events import Event, EventRegistration
from database.models.user import User
from database.base import session

from bot.states.event import EventRegistrationForm
from bot.utils.keyboards import EventKeyboards, MainKeyboards
from bot.utils.utils import generate_event_text

from configuration import ua_config

event_router = Router()


async def send_event_registration(event_id: int, message: Message, back_button=True):
    with session() as s:
        event = s.query(Event).filter(Event.id == event_id).first()
    if not event or not event.is_registration_enabled:
        await message.answer(
            text=ua_config.get('event_registrations', 'registration_ends')
        )
    else:
        title = event.title
        description = event.description
        photo = event.photo
        event_text = await generate_event_text(title, description)
        await message.bot.send_photo(
            caption=event_text,
            photo=photo,
            reply_markup=EventKeyboards.generate_event_register(event_id, back_button),
            parse_mode=ParseMode.MARKDOWN_V2,
            chat_id=message.chat.id
        )


async def send_events_main_page(message: Message, state: FSMContext, reply: bool = True):
    await state.clear()
    with session() as s:
        events = s.query(Event).filter(Event.is_registration_enabled == True).all()
    events_to_render = []
    for event in events:
        events_to_render.append([event.id, event.title])
    if len(events_to_render) == 0:
        await message.answer(
            text=ua_config.get('event_registrations', 'no_events')
        )
    elif reply:
        await message.reply(
            text=ua_config.get('event_registrations', 'select_event'),
            reply_markup=EventKeyboards.generate_event_list(events_to_render),
        )
    else:
        await message.answer(
            text=ua_config.get('event_registrations', 'select_event'),
            reply_markup=EventKeyboards.generate_event_list(events_to_render),
        )


@event_router.message(F.text == ua_config.get('buttons', 'events'))
async def event_register_handler(message: Message, state: FSMContext) -> None:
    await send_events_main_page(message, state)


@event_router.callback_query(F.data.startswith('event_select_'))
async def event_register_selection_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.bot.delete_message(
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id
    )
    event_id = int(callback.data.split('_')[-1])
    await send_event_registration(event_id=event_id, message=callback.message)


@event_router.callback_query(F.data.startswith('event_register_'))
async def event_register_selection_handler(callback: CallbackQuery, state: FSMContext) -> None:
    event_id = int(callback.data.split('_')[-1])
    await callback.message.edit_reply_markup(
        reply_markup=None
    )
    with session() as s:
        event = s.query(Event).filter(Event.id == event_id).first()
        event_registration = s.query(EventRegistration).filter(EventRegistration.event_id == event_id, EventRegistration.user_id == callback.from_user.id).first()
    if not event or not event.is_registration_enabled:
        await state.clear()
        await callback.message.answer(
            text=ua_config.get('event_registrations', 'registration_ends')
        )
    elif event_registration:
        await state.clear()
        await callback.message.answer(
            text=ua_config.get('event_registrations', 'already_registered')
        )
    else:
        await state.set_state(EventRegistrationForm.ami_student)
        await state.update_data(event_id=event_id)
        await callback.message.reply(
            text=ua_config.get('event_registrations', 'is_ami_student'),
            reply_markup=MainKeyboards.yes_no_keyboard()
        )


@event_router.callback_query(EventRegistrationForm.ami_student)
async def event_register_is_ami_handler_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(is_ami_student=True if callback.data == 'yes' else False)
    await callback.message.edit_text(
        text=ua_config.get('event_registrations', 'enter_codingame_username'),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.set_state(EventRegistrationForm.codingame_username)


@event_router.message(EventRegistrationForm.codingame_username)
async def event_register_codingame_user_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(codingame_username=message.text)
    await message.answer(
        text=ua_config.get('event_registrations', 'division_selection_text'),
        reply_markup=EventKeyboards.generate_division_selection()
    )
    await state.set_state(EventRegistrationForm.division_selection)


@event_router.callback_query(EventRegistrationForm.division_selection)
async def event_register_codingame_user_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(division=1 if callback.data == 'first' else 2)
    await callback.message.edit_text(
        text=ua_config.get('event_registrations', 'personal_info_processing'),
        reply_markup=MainKeyboards.yes_keyboard()
    )
    await state.set_state(EventRegistrationForm.personal_info_processing_validation)


@event_router.callback_query(EventRegistrationForm.personal_info_processing_validation)
async def event_register_personal_info_processing_validation_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        text=ua_config.get('event_registrations', 'media_publishing_processing'),
        reply_markup=MainKeyboards.yes_keyboard()
    )
    await state.set_state(EventRegistrationForm.media_publishing_validation)


@event_router.callback_query(EventRegistrationForm.media_publishing_validation)
async def event_register_media_publishing_validation_handler(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    event_id = data['event_id']
    is_ami_student = data['is_ami_student']
    codingame_username = data['codingame_username']
    division = data['division']
    with session() as s:
        event = s.query(Event).filter(Event.id == event_id).first()
    if not event or not event.is_registration_enabled:
        await callback.message.edit_text(
            text=ua_config.get('event_registrations', 'registration_ends'),
            reply_markup=None
        )
    else:
        with session() as s:
            event_registration = EventRegistration(
                event_id=event_id,
                codingame_username=codingame_username,
                division=division,
                is_ami_student=is_ami_student,
                user_id=callback.from_user.id,
                invite_link=event.first_division_invite_link if division == 1 else event.second_division_invite_link,
                member_chat_id=event.first_division_chat_id if division == 1 else event.second_division_chat_id
            )
            s.add(event_registration)
            await callback.message.edit_text(
                text=ua_config.get('event_registrations', 'registration_completed'),
                reply_markup=None
            )


@event_router.callback_query(F.data.startswith('event_registration_back'))
async def event_registration_back_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id
    )
    await send_events_main_page(callback.message, state, False)


@event_router.chat_join_request()
async def event_chat_join_request(request: ChatJoinRequest) -> None:
    user_id = request.from_user.id
    chat_id = request.chat.id
    with session() as s:
        registration = s.query(EventRegistration).filter(EventRegistration.user_id == user_id,
                                                         EventRegistration.member_chat_id == str(chat_id),
                                                         EventRegistration.is_approved == True).first()
    if not registration:
        await request.bot.decline_chat_join_request(chat_id=chat_id, user_id=user_id)
    else:
        await request.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
