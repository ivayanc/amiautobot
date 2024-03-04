from typing import Optional

import sqlalchemy as sa

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship

from flask_admin.contrib.sqla import ModelView

from database.base import Base
from configuration import ADMIN_PANEL_PAGE_SIZE

from datetime import datetime


class Event(Base):
    __tablename__ = 'events'
    id: Mapped[int] = mapped_column(sa.BigInteger(), primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(sa.Text())
    description: Mapped[str] = mapped_column(sa.Text())
    photo: Mapped[Optional[str]]
    max_capacity: Mapped[Optional[int]]
    is_registration_enabled: Mapped[Optional[bool]] = mapped_column(sa.Boolean(), default=False)
    first_division_invite_link: Mapped[Optional[str]]
    second_division_invite_link: Mapped[Optional[str]]
    first_division_chat_id: Mapped[Optional[str]]
    second_division_chat_id: Mapped[Optional[str]]

    def __repr__(self):
        return f'< Event: {self.id}, {self.title} >'


class EventView(ModelView):
    column_list = ('id', 'title', 'description', 'max_capacity')
    form_columns = ('id', 'title', 'description', 'photo', 'max_capacity', 'is_registration_enabled',
                    'first_division_invite_link', 'second_division_invite_link', 'first_division_chat_id',
                    'second_division_chat_id')
    column_searchable_list = ['title', 'description', 'id']
    page_size = ADMIN_PANEL_PAGE_SIZE


class EventRegistration(Base):
    __tablename__ = 'event_registrations'
    id: Mapped[int] = mapped_column(sa.BigInteger(), primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(sa.ForeignKey("events.id"))
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.telegram_id"))
    is_ami_student: Mapped[bool]
    codingame_username: Mapped[str]
    is_approved: Mapped[bool] = mapped_column(sa.Boolean(), default=False)
    division: Mapped[int]
    invite_link: Mapped[Optional[str]]
    member_chat_id: Mapped[Optional[str]]

    event = relationship("Event")
    user = relationship("User")

    def __repr__(self):
        return f'< Event registration: {self.id}, {self.event_id}>'


class EventRegistrationView(ModelView):
    column_list = ('id', 'event_id', 'user_id', 'is_ami_student', 'codingame_username', 'is_approved')
    form_columns = ('id', 'event_id', 'user_id', 'is_ami_student', 'codingame_username', 'is_approved')
    column_filters = ('event_id', 'is_approved')
    page_size = ADMIN_PANEL_PAGE_SIZE
