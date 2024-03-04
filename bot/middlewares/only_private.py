from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message


class AnswerOnlyInPrivateChats(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        process = False
        if event.chat.type == 'private':
            process = True
        if event.chat.join_by_request:
            process = True
        if process:
            return await handler(event, data)
