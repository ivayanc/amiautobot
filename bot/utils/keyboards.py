from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

from bot.utils.constants import Gender

from configuration import ua_config, DONATION_LINK


class MainKeyboards:

    @staticmethod
    def default_keyboard():
        """
        :param: ignore_admin - if True returns user keyboard for Admins and SuperAdmins
        """
        return MainKeyboards.guest_keyboard()

    @staticmethod
    def guest_keyboard():
        result_kb = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=ua_config.get('buttons', 'profile')),
                    KeyboardButton(text=ua_config.get('buttons', 'faq')),
                    KeyboardButton(text=ua_config.get('buttons', 'help'))
                ],
                [
                    KeyboardButton(text=ua_config.get('buttons', 'events')),
                    KeyboardButton(text=ua_config.get('buttons', 'tumbochka'))
                ]
            ],
            resize_keyboard=True
        )
        return result_kb

    @staticmethod
    def yes_no_keyboard():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=ua_config.get('yes_no', 'yes'), callback_data='yes'),
                    InlineKeyboardButton(text=ua_config.get('yes_no', 'no'), callback_data='no'),
                ]
            ],
        )
        return keyboard

    @staticmethod
    def yes_keyboard():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=ua_config.get('yes_no', 'yes'), callback_data='yes'),
                ]
            ],
        )
        return keyboard

    @staticmethod
    def tumbochka_keyboard():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=ua_config.get('buttons', 'donation_jar'), url=DONATION_LINK),
                ],
                [
                    InlineKeyboardButton(text=ua_config.get('buttons', 'close'), callback_data='close')
                ]
            ],
        )
        return keyboard


class ProfileKeyboards:
    @staticmethod
    def profile_keyboard():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=ua_config.get('buttons', 'change_data'), callback_data='manage_profile')
                ],
                [
                    InlineKeyboardButton(text=ua_config.get('buttons', 'my_events'), callback_data='my_events')
                ],
                [
                    InlineKeyboardButton(text=ua_config.get('buttons', 'close'), callback_data='close')
                ]
            ],

        )
        return keyboard

    @staticmethod
    def skip_question_keyboard():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=ua_config.get('buttons', 'skip_question'), callback_data='skip_question')
                ]
            ]
        )
        return keyboard

    @staticmethod
    def validate_keyboard():
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=ua_config.get('buttons', 'again'), callback_data='try_again'),
                InlineKeyboardButton(text=ua_config.get('buttons', 'validate'), callback_data='validate')
            ]
        ])
        return keyboard

    @staticmethod
    def gender_keyboard():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=ua_config.get('genders', 'female'),
                                         callback_data=str(Gender.female.name)),
                    InlineKeyboardButton(text=ua_config.get('genders', 'male'),
                                         callback_data=str(Gender.male.name))
                ],
                [
                    InlineKeyboardButton(text=ua_config.get('genders', 'nonbinary_gender'),
                                         callback_data=str(Gender.nonbinary_gender.name)),
                    InlineKeyboardButton(text=ua_config.get('genders', 'other_gender'),
                                         callback_data=str(Gender.other_gender.name))
                ],
                [
                    InlineKeyboardButton(text=ua_config.get('buttons', 'skip_question'), callback_data='skip_question')
                ]
            ]
        )
        return keyboard


class FAQKeyboards:

    @staticmethod
    def generate_faq_selection_list(faq_categories: list[list[int, str]], back_button: bool = False):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for category_id, category_title in faq_categories:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(text=category_title, callback_data=f'faq_category_select_{category_id}')
                ]
            )
        if not back_button:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(text=ua_config.get('buttons', 'close'), callback_data='close')
                ]
            )
        else:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(text=ua_config.get('buttons', 'back'), callback_data='faq_category_back')
                ]
            )
        return keyboard


class EventKeyboards:

    @staticmethod
    def generate_event_list(events: list[list[int, str]]):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for event_id, event_title in events:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(text=event_title, callback_data=f'event_select_{event_id}')
                ]
            )
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text=ua_config.get('buttons', 'close'), callback_data='close')
            ]
        )
        return keyboard

    @staticmethod
    def generate_my_event_list(events: list[list[int, str]], back_data='profile_back'):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for event_id, event_title in events:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(text=event_title, callback_data=f'my_event_select_{event_id}')
                ]
            )
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text=ua_config.get('buttons', 'back'), callback_data=back_data)
            ]
        )
        return keyboard

    @staticmethod
    def generate_event_register(event_id, back_button=True):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=ua_config.get('event_registrations', 'register_on_event'), callback_data=f'event_register_{event_id}')
            ]
        ])
        if back_button:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(text=ua_config.get('buttons', 'back'), callback_data='event_registration_back')
                ]
            )
        return keyboard

    @staticmethod
    def generate_division_selection():
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=ua_config.get('event_registrations', 'professional'),
                                     callback_data='first')
            ],
            [
                InlineKeyboardButton(text=ua_config.get('event_registrations', 'newbies'), callback_data='second')
            ]
        ])
        return keyboard

    @staticmethod
    def generate_chat_invite_keyboard(url):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=ua_config.get('event_admin_prompts', 'event_chat'),
                                     url=url)
            ]
        ])
        return keyboard
