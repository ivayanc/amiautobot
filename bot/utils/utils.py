from configuration import ua_config

from bot.utils.constants import Gender


def gender_to_text(gender: Gender) -> str:
    if gender == Gender.female or gender == Gender.female.name:
        return ua_config.get('genders', 'female')
    if gender == Gender.male or gender == Gender.male.name:
        return ua_config.get('genders', 'male')
    if gender == Gender.other_gender or gender == Gender.other_gender.name:
        return ua_config.get('genders', 'other_gender')
    if gender == Gender.nonbinary_gender or gender == Gender.nonbinary_gender.name:
        return ua_config.get('genders', 'nonbinary_gender')
    return '-'


async def generate_event_text(title: str, description: str) -> str:
    return f'*{title}*\n\n{description}'
