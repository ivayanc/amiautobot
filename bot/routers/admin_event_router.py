from __future__ import annotations

from typing import Optional

from aiogram import Router, F

from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from database.models.events import Event, EventRegistration
from database.base import session

from bot.filters.role_filter import AdminFilter
from bot.utils.keyboards import MainKeyboards, EventKeyboards
from bot.utils.utils import generate_event_text

from bot.states.event import CreationEventForm, RejectEventRegistrationForm

from configuration import ua_config

admin_event_router = Router()


@admin_event_router.message(Command(commands=['event_creation']), AdminFilter())
async def event_creation_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(CreationEventForm.title)
    await message.reply(text=ua_config.get('event_creation', 'title'))


@admin_event_router.message(CreationEventForm.title)
async def event_creation_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(CreationEventForm.description)
    await message.reply(text=ua_config.get('event_creation', 'description'))


@admin_event_router.message(CreationEventForm.description)
async def event_creation_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(CreationEventForm.photo)
    await message.reply(text=ua_config.get('event_creation', 'photo'))


@admin_event_router.message(CreationEventForm.photo)
async def event_creation_handler(message: Message, state: FSMContext) -> None:
    if isinstance(message.photo, list) and len(message.photo) > 0:
        await state.update_data(photo=message.photo[0].file_id)
    await state.set_state(CreationEventForm.validate)
    data = await state.get_data()
    title = data['title']
    description = data['description']
    photo = data['photo']
    event_text = await generate_event_text(title, description)
    creation_text = ua_config.get('event_creation', 'approve_creation_text')
    await message.bot.send_photo(
        caption=f'{creation_text}\n\n{event_text}',
        photo=photo,
        reply_markup=MainKeyboards.yes_no_keyboard(),
        chat_id=message.chat.id,
        parse_mode=ParseMode.MARKDOWN_V2
    )


@admin_event_router.callback_query(CreationEventForm.validate)
async def event_creation_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    if callback.data == 'yes':
        await state.set_state(CreationEventForm.validate)
        data = await state.get_data()
        title = data['title']
        description = data['description']
        photo = data['photo']
        with session() as s:
            event = Event(
                title=title,
                description=description,
                photo=photo
            )
            s.add(event)
        await callback.message.reply(
            text=ua_config.get('event_creation', 'event_created')
        )
    else:
        await callback.message.reply(
            text=ua_config.get('event_creation', 'event_creation_canceled')
        )
    await state.clear()


@admin_event_router.message(Command(commands=['approve_event_registration']), AdminFilter())
async def approve_event_registration_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    registration_id = int(message.text.split()[-1])
    with session() as s:
        registration = s.query(EventRegistration).filter(EventRegistration.id == registration_id, EventRegistration.is_approved == False).first()
        if registration:
            registration.is_approved = True
            event = registration.event
    if registration:
        user_to_sent = registration.user_id
        await message.bot.send_message(
            chat_id=user_to_sent,
            text=ua_config.get('event_admin_prompts', 'registration_approved').format(event_name=event.title),
            reply_markup=EventKeyboards.generate_chat_invite_keyboard(registration.invite_link)
        )
        await message.reply(
            text='Sent'
        )


@admin_event_router.message(Command(commands=['reject_event_registration']), AdminFilter())
async def reject_event_registration_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(RejectEventRegistrationForm.rejection_reason)
    registration_id = int(message.text.split()[-1])
    await state.update_data(registration_id=registration_id)
    await message.reply(text=ua_config.get('event_admin_prompts', 'enter_reject_reason'))


@admin_event_router.message(RejectEventRegistrationForm.rejection_reason)
async def rejection_reason_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    registration_id = data['registration_id']
    with session() as s:
        registration = s.query(EventRegistration).filter(EventRegistration.id == registration_id, EventRegistration.is_approved == False).first()
        if registration:
            registration.is_approved = True
            event = registration.event
            s.delete(registration)
    if registration:
        user_to_sent = registration.user_id
        await message.bot.send_message(
            chat_id=user_to_sent,
            text=ua_config.get('event_admin_prompts', 'reject_registration').format(event_name=event.title, decline_reason=message.text)
        )
        await message.reply(
            text='Sent'
        )
    await state.clear()
