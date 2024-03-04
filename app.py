import logging

from flask import Flask
from flask_admin import Admin
from flask_basicauth import BasicAuth

from configuration import DB_URL, ADMIN_PANEL_SECRET_KEY, ADMIN_PANEL_BASIC_AUTH_PASSWORD, ADMIN_PANEL_BASIC_AUTH_USERNAME

from database.models.user import User, UserView
from database.models.faq import FAQCategory, FAQCategoryView
from database.models.events import Event, EventView, EventRegistration, EventRegistrationView
from database.base import current_session


app = Flask(__name__)
logger = logging.getLogger(__name__)

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

admin = Admin(app, name='amihelper', template_mode='bootstrap3', url='/extra-wh-2020/')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SECRET_KEY'] = ADMIN_PANEL_SECRET_KEY
app.config['BASIC_AUTH_USERNAME'] = ADMIN_PANEL_BASIC_AUTH_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = ADMIN_PANEL_BASIC_AUTH_PASSWORD
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)

admin.add_view(UserView(User, current_session))
admin.add_view(FAQCategoryView(FAQCategory, current_session))
admin.add_view(EventView(Event, current_session))
admin.add_view(EventRegistrationView(EventRegistration, current_session))

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    logger.error("Starting admin panel")
    http_server = WSGIServer(('localhost', 4000), app)
    logger.error("Http server configured")
    http_server.serve_forever()
