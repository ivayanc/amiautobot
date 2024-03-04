import configparser
import os

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DB_URL')

BOT_TOKEN = os.getenv('TOKEN')
USE_REDIS = os.getenv('USE_REDIS')

ADMIN_PANEL_PAGE_SIZE = 20
ADMIN_PANEL_SECRET_KEY = os.getenv('ADMIN_PANEL_SECRET_KEY')
ADMIN_PANEL_BASIC_AUTH_USERNAME = os.getenv('ADMIN_PANEL_BASIC_AUTH_USERNAME')
ADMIN_PANEL_BASIC_AUTH_PASSWORD = os.getenv('ADMIN_PANEL_BASIC_AUTH_PASSWORD')

DONATION_LINK = os.getenv('DONATION_LINK')
DONATION_CARD_NUMBER = os.getenv('DONATION_CARD_NUMBER')

ua_config = configparser.ConfigParser()
ua_config.read('bot/locales/ua/strings.ini')
