import datetime, os, shutil, h5py, numpy

from sqlalchemy import func, Column, Float, Integer, String, UnicodeText, Date, ForeignKey
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


# Spectra always belong to a specific ice analogue
class Analogue(db.Model):
  __tablename__ = 'analogues'
  id = Column(Integer, primary_key=True, autoincrement=True)
  user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
  user = db.relationship('User', backref='analogues')

  name = Column(String, nullable=False)
  deposition_temperature = Column(Float)
  description = Column(UnicodeText)
  author = Column(String)
  DOI = Column(String)
  pub_date = Column(Date, default=datetime.datetime.now)

  def __str__(self):
    return "%s" % (self.name)

  def DOI_url(self):
    return "http://doi.org/%s" % self.DOI

  def average_resolution(self):
    return numpy.average([s.resolution for s in self.spectra])

  def temperatures_to_sentence(self):
    temperatures = sorted([s.temperature for s in self.spectra])
    t = [str(int(t)) if t.is_integer() else str(t) for t in temperatures]
    if len(t) > 1:
      return ', '.join(t[:-1]) + ' and ' + t[-1] + ' K'
    else:
      return t[0] + ' K'


# A single measured spectrum
class Spectrum(db.Model):
  __tablename__ = 'spectra'
  id = Column(Integer, primary_key=True, autoincrement=True)
  analogue_id = Column(Integer, ForeignKey('analogues.id'), nullable=False)
  analogue = db.relationship('Analogue', backref='spectra')

  temperature = Column(Float, nullable=False)
  category = Column(Integer, default=0)
  resolution = Column(Float, nullable=True)
  wavenumber_range = Column(String, nullable=True)
  description = Column(UnicodeText)
  path = Column(String, nullable=False)

  def __str__(self):
    return "%s at %s K" % (self.analogue.name, self.temperature)

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
    with h5py.File(self.h5_file_path(), 'r') as f:
      data = f['spectrum'].value
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
      # Don't care it was not deleted because it does not exist
      pass
    try:
      shutil.rmtree(op.join(data_path, "%s" % target.id))
    except OSError:
      pass
    try:
      os.remove(op.join(data_path, "%s.gz" % target.id))
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

  if db.session.query(func.count(Analogue.id)).scalar() == 0:
    print('Adding ice analogues..')
    from application.seed import fetch
    fetch()

  print('Seed data successfully added to database')
