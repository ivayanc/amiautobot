from typing import Optional

import sqlalchemy as sa

from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database.base import Base

from configuration import ADMIN_PANEL_PAGE_SIZE

from bot.utils.constants import Gender


class User(Base):
    __tablename__ = 'users'
    telegram_id: Mapped[int] = mapped_column(sa.BigInteger(), primary_key=True)
    username: Mapped[Optional[str]]
    full_name: Mapped[Optional[str]]
    academic_group: Mapped[Optional[str]]
    instagram: Mapped[Optional[str]]
    is_banned: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    gender: Mapped[Optional[Gender]]

    def __repr__(self):
        return f'< Username: {self.username}, Telegram Id: {self.telegram_id} >'


class UserView(ModelView):
    column_list = ('telegram_id', 'username', 'full_name', 'academic_group', 'instagram', 'is_banned',
                   'gender', 'is_admin')
    form_columns = ('telegram_id', 'username', 'full_name', 'academic_group', 'instagram', 'is_banned',
                    'gender', 'is_admin')
    column_searchable_list = ['telegram_id', 'username', 'instagram']
    column_filters = ['academic_group', 'is_banned', 'is_admin']
    page_size = ADMIN_PANEL_PAGE_SIZE
