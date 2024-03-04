from typing import Optional

import sqlalchemy as sa

from flask_admin.contrib.sqla import ModelView
from wtforms.fields import TextAreaField
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database.base import Base

from configuration import ADMIN_PANEL_PAGE_SIZE


class FAQCategory(Base):
    __tablename__ = 'faq_categories'
    id: Mapped[int] = mapped_column(sa.BigInteger(), primary_key=True, autoincrement=True)
    title: Mapped[Optional[str]]
    parent_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey("faq_categories.id"))
    parent = relationship("FAQCategory")
    leaf_category: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    category_answer: Mapped[Optional[str]] = mapped_column(sa.Text())

    def __repr__(self):
        return self.title


class FAQCategoryView(ModelView):
    column_list = ('id', 'title', 'parent_id', 'leaf_category')
    form_columns = ('id', 'title', 'parent_id', 'leaf_category', 'category_answer')
    column_filters = ['leaf_category']
    column_searchable_list = ['title']
    form_overrides = {
        'category_answer': TextAreaField
    }
    form_widget_args = {
        'category_answer': {
            'rows': 20,
        }
    }
    page_size = ADMIN_PANEL_PAGE_SIZE
