from aiogram.fsm.state import State, StatesGroup


class ManageProfileForm(StatesGroup):
    full_name = State()
    academic_group = State()
    instagram = State()
    gender = State()
