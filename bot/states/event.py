from aiogram.fsm.state import State, StatesGroup


class CreationEventForm(StatesGroup):
    title = State()
    description = State()
    photo = State()
    validate = State()


class EventRegistrationForm(StatesGroup):
    selected = State()
    ami_student = State()
    codingame_username = State()
    division_selection = State()
    personal_info_processing_validation = State()
    media_publishing_validation = State()


class RejectEventRegistrationForm(StatesGroup):
    rejection_reason = State()
