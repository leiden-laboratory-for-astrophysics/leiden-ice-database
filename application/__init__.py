import os
import os.path as op

from flask import Flask
from flask_bootstrap import Bootstrap

# Flask-Migrate (using Flask-Script) and SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config.from_object('application.config.Configuration')

db = SQLAlchemy(app)
migrate = Migrate(app, db, directory='application/migrations')
manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server(host='0.0.0.0', port=5000))
manager.add_command('server', Server(host='0.0.0.0', port=5000))

Bootstrap(app)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

# Create directory for data file fields to use
data_path = op.join(op.dirname(__file__), 'data')
try:
  os.mkdir(data_path)
except OSError:
  pass

## Change - Will 23/04/2021
# Create directory for data file fields to use
data_path_optc = op.join(op.dirname(__file__), 'data_opt_const')
try:
  os.mkdir(data_path_optc)
except OSError:
  pass

data_path_sc = op.join(op.dirname(__file__), 'data_sc')
try:
  os.mkdir(data_path_sc)
except OSError:
  pass

data_path_annot = op.join(op.dirname(__file__), 'annotation_test')
try:
  os.mkdir(data_path_annot)
except OSError:
  pass

from application.auth import *
from application.admin import admin
from application.api import api
from application.models import *
from application.views import *
from application.debug import *
