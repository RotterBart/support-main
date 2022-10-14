from gevent import monkey
monkey.patch_all()

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_socketio import SocketIO
#from flask_caching import Cache

import os

# from flask_msearch import Search
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_searchable import make_searchable
from sqlalchemy import orm
from flask_ckeditor import CKEditor

app = Flask(__name__)
#cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.config.from_object(Config)

app.config['RESIZE_URL'] = 'http://10.10.2.191'
app.config['RESIZE_ROOT'] = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), app.config['UPLOADS_PATH'])



db = SQLAlchemy(app)
Base = declarative_base()
make_searchable(Base.metadata)
orm.configure_mappers()

db.create_all()
db.session.commit()

migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'Войдите, чтобы открыть страницу'
login.login_message_category = "info"

bootstrap = Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
mail = Mail(app)
moment = Moment(app)
socketio = SocketIO(app, async_mode='gevent')
socketio.init_app(app)
#search = Search(db=db)
#search.init_app(app)
ckeditor = CKEditor(app)

from app import routes, models, errors
