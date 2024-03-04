from __future__ import annotations

from typing import Optional

from aiogram import Router, F

from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from database.models.faq import FAQCategory
from database.base import session

from bot.utils.keyboards import FAQKeyboards

from bot.states.faq import FAQForm

from configuration import ua_config

faq_router = Router()


async def get_repositories_categories(parent_id: bool[int] = None):
    faq_categories = []
    with session() as s:
        if parent_id:
            res = s.query(FAQCategory).filter(FAQCategory.parent_id == parent_id)
        else:
            res = s.query(FAQCategory).filter(FAQCategory.leaf_category != None, FAQCategory.parent_id == None)
        res = res.all()
        for r in res:
            faq_categories.append([r.id, r.title])
    return faq_categories


async def send_main_faq_info(message: Message, inline_keyboard, change_message: bool = False) -> None:
    if change_message:
        await message.bot.edit_message_text(
            text=ua_config.get('faq', 'faq_main'),
            reply_markup=inline_keyboard,
            chat_id=message.chat.id,
            message_id=message.message_id
        )
    else:
        await message.reply(text=ua_config.get('faq', 'faq_main'), reply_markup=inline_keyboard)


@faq_router.message(F.text == ua_config.get('buttons', 'faq'))
async def faq_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FAQForm.selecting)
    faq_categories = await get_repositories_categories()
    await send_main_faq_info(message, inline_keyboard=FAQKeyboards.generate_faq_selection_list(faq_categories))


@faq_router.callback_query(F.data.startswith('faq_category_select_'))
async def process_category_select(callback: CallbackQuery, state: FSMContext) -> None:
    current_id = int(callback.data.split('_')[-1])
    data = await state.get_data()
    new_parent = data.get('current_parent')
    new_parent = await generate_new_parent_key(data.get('parent_id', ''), new_parent)
    await state.update_data(**new_parent)
    with session() as s:
        current_category = s.query(FAQCategory).get(current_id)
    if current_category.leaf_category:
        await callback.message.bot.edit_message_text(
            text=current_category.category_answer,
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=FAQKeyboards.generate_faq_selection_list([], True),
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    else:
        await state.update_data(current_parent=current_id)
        faq_categories = await get_repositories_categories(parent_id=current_id)
        await send_main_faq_info(callback.message, inline_keyboard=FAQKeyboards.generate_faq_selection_list(faq_categories, True), change_message=True)


@faq_router.callback_query(F.data == 'faq_category_back')
async def process_category_back(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    parent_id = data.get('parent_id')
    current_parent = await get_new_current_parent(parent_id)
    await state.update_data(**current_parent)
    if parent_id is None or parent_id == '':
        faq_categories = await get_repositories_categories()
        await send_main_faq_info(callback.message,
                                 inline_keyboard=FAQKeyboards.generate_faq_selection_list(faq_categories), change_message=True)
    else:
        faq_categories = await get_repositories_categories(int(parent_id.split(';')[-1]))
        new_parent = await generate_new_parent_key(parent_id)
        await state.update_data(**new_parent)
        await send_main_faq_info(callback.message, inline_keyboard=FAQKeyboards.generate_faq_selection_list(faq_categories, True), change_message=True)


async def generate_new_parent_key(parent_id: str, new_id: Optional[str] = None):
    if new_id:
        if parent_id:
            parent_id = parent_id.split(';')
        else:
            parent_id = []
        parent_id.append(str(new_id))
    else:
        parent_id = parent_id.split(';')[:-1]
    update_data = {
        'parent_id': ';'.join(parent_id)
    }
    return update_data


async def get_new_current_parent(parent_id: str):
    if parent_id:
        current_parent = parent_id.split(';')[-1]
    else:
        current_parent = None
    update_data = {
        'current_parent': current_parent
    }
    return update_data
