import os
import os.path as op

from flask import Flask
from flask_bootstrap import Bootstrap

# Flask-Migrate (using Flask-Script) and SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand

# Science tools
#import matplotlib.pyplot as plt

app = Flask(__name__)
app.config.from_object('application.config.Configuration')

db = SQLAlchemy(app)
migrate = Migrate(app, db, directory='application/migrations')
manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server(host='0.0.0.0', port=5000))

Bootstrap(app)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

# Create directory for data file fields to use
data_path = op.join(op.dirname(__file__), 'data')
try:
  os.mkdir(data_path)
except OSError:
  pass

from application.auth import *
from application.admin import admin
from application.api import api
from application.models import *
from application.views import *
from application.debug import *
