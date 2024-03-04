from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.models.user import User
from database.base import session


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        with session() as s:
            user = s.query(User).filter(User.telegram_id == user_id).first()

        if user and user.is_admin:
            return True
        return False
