import datetime, os, shutil, h5py

from sqlalchemy import func, Column, Integer, String, UnicodeText, Date, ForeignKey
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from application import db, manager, data_path
from sqlalchemy.event import listens_for
import os.path as op

# After changing a model, don't forget to run database migrations:
# $ python app.py db migrate -m 'Migration message'
# $ python app.py db upgrade
# For more information see: https://github.com/miguelgrinberg/Flask-Migrate

# Authentication
class User(db.Model):
  __tablename__ = 'users'
  id = Column(db.Integer, primary_key=True, autoincrement=True)
  username = Column(String(80), unique=True, nullable=False)
  password = Column(String, nullable=False)
  email = Column(String(120), nullable=False, unique=True)

  def set_password(self, password):
    self.password = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password, password)
  
  # Flask-Login integration
  def is_active(self):
    return True

  def is_authenticated(self):
    return True

  def get_id(self):
    return self.id

  def __str__(self):
    return self.username


# Spectra always belong to a specific ice mixture
class Mixture(db.Model):
  __tablename__ = 'mixtures'
  id = Column(Integer, primary_key=True, autoincrement=True)
  user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
  user = db.relationship('User', backref='mixtures')

  name = Column(String, nullable=False)
  description = Column(UnicodeText)
  author = Column(String)
  author_email = Column(String)
  pub_date = Column(Date, default=datetime.datetime.now)

  def __str__(self):
    return "%s by %s" % (self.name, self.author)


# A single measured spectrum
class Spectrum(db.Model):
  __tablename__ = 'spectra'
  id = Column(Integer, primary_key=True, autoincrement=True)
  mixture_id = Column(Integer, ForeignKey('mixtures.id'), nullable=False)
  mixture = db.relationship('Mixture', backref='spectra')

  temperature = Column(Integer, nullable=False)
  description = Column(UnicodeText)
  path = Column(String, nullable=False)

  def __str__(self):
    return "%s at %s K" % (self.mixture.name, self.temperature)
  
  def gzipped(self):
    return op.isfile(self.ungz_file_path()) == False

  def ungz_file_path(self):
    return op.join(data_path, self.path)
  
  def data_folder(self):
    return op.join(data_path, "%s" % self.id)

  def gz_file_path(self):
    return op.join(data_path, "%s.txt.gz" % self.id)

  def h5_file_path(self):
    return op.join(self.data_folder(), "%s.h5" % self.id)

  def read_h5(self):
    f = h5py.File(self.h5_file_path(), 'r')
    data = f['spectrum'].value
    f.close()
    return data

  def download_filename(self):
    return "%s_%sK" % (self.id, self.temperature)

  def gz_file_size(self):
    return os.path.getsize(self.gz_file_path())


# Delete hooks for models, delete files if models are getting deleted
@listens_for(Spectrum, 'after_delete')
def del_file(mapper, connection, target):
  if target.path:
    try:
      os.remove(op.join(data_path, target.path))
    except OSError:
      # Don't care if was not deleted because it does not exist
      pass
    try:
      shutil.rmtree(op.join(data_path, "%s" % target.id))
    except OSError:
      pass
    try:
      os.remove(op.join(data_path, "%s.gz" % target.path))
    except OSError:
      pass

@manager.command
def seed():
  "Add seed data to the database."
  if db.session.query(func.count(User.id)).scalar() == 0:
    print('Adding test user..')
    user = User(username='lab', email='olsthoorn@strw.leidenuniv.nl')
    user.set_password('test')
    db.session.add(user)
    db.session.commit() # commit to get user ID

  if db.session.query(func.count(Mixture.id)).scalar() == 0:
    print('Adding mixtures..')
    from application.seed import fetch
    fetch()
  
  print('Seed data successfully added to database')
