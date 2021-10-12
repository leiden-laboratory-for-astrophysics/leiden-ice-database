import datetime, os, shutil, h5py, numpy

from sqlalchemy import func, Column, Float, Integer, String, UnicodeText, Date, ForeignKey
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from application import db, manager, data_path, data_path_optc, data_path_sc
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
  name2 = Column(String, nullable=True)
  name3 = Column(String, nullable=True)
  name4 = Column(String, nullable=True)
  name5 = Column(String, nullable=True)
  deposition_temperature = Column(Float, nullable=False)
  description = Column(UnicodeText)
  author = Column(String)
  DOI = Column(String, nullable=False)
  pub_date = Column(Date, default=datetime.datetime.now)
  path_annot = Column(String, nullable=True)

  def __str__(self):
    return "%s" % (self.name3)

  def DOI_url(self):
    return "http://doi.org/%s" % self.DOI

  def average_resolution(self):
    print('Models avg_res', numpy.average([s.resolution for s in self.spectra]))
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
  exposure_time = Column(Integer, nullable=True)
  column_density = Column(Float, nullable=True)
  ice_thickness = Column(Float, nullable=True)
  resolution = Column(Float, nullable=True)
  wavenumber_range = Column(String, nullable=True)
  description = Column(UnicodeText)
  path = Column(String, nullable=False)

  CATEGORIES = [('0', 'Warm-up'), ('1', 'Exposure time'), ('2', 'Other')]

  def category_str(self):
    return [category for category in Spectrum.CATEGORIES if int(category[0]) == self.category][0][1]

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
      data = f['spectrum'][()]
    return data

  def download_filename(self):
    return "%s_%sK" % (self.id, self.temperature)

  def gz_file_size(self):
    return os.path.getsize(self.gz_file_path())

# Delete hooks for models, delete files if models are getting deleted
@listens_for(Spectrum, 'after_delete')
def del_file(mapper, connection, target):
  print("I AM DEL FILEEEE")
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


# Authentication
class N_User(db.Model):
  __bind_key__ = 'n'
  __tablename__ = 'n_users'
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
class N_Analogue(db.Model):
  __bind_key__ = 'n'
  __tablename__ = 'n_analogues'
  id = Column(Integer, primary_key=True, autoincrement=True)
  n_user_id = Column(Integer, ForeignKey('n_users.id'), nullable=False)
  n_user = db.relationship('N_User', backref='n_analogues')

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

  def n_average_resolution(self):
    return numpy.average([s.resolution for s in self.n_val])

  def n_temperatures_to_sentence(self):
    temperatures = sorted([s.temperature for s in self.n_val])
    t = [str(int(t)) if t.is_integer() else str(t) for t in temperatures]
    if len(t) > 1:
      return ', '.join(t[:-1]) + ' and ' + t[-1] + ' K'
    else:
      return t[0] + ' K'


# A single measured N (real part of refractive index)
class N_optc(db.Model):
  __bind_key__ = 'n'
  __tablename__ = 'n_val'
  id = Column(Integer, primary_key=True, autoincrement=True)
  n_analogue_id = Column(Integer, ForeignKey('n_analogues.id'), nullable=False)
  n_analogue = db.relationship('N_Analogue', backref='n_val')

  temperature = Column(Float, nullable=False)
  category = Column(Integer, default=0)
  exposure_time = Column(Integer, nullable=True)
  resolution = Column(Float, nullable=True)
  wavenumber_range = Column(String, nullable=True)
  description = Column(UnicodeText)
  path = Column(String, nullable=False)

  N_CATEGORIES = [('0', 'Warm-up N'), ('1', 'Warm-up K'), ('2', 'Other')]

  def n_category_str(self):
    return [category for category in N_optc.N_CATEGORIES if int(category[0]) == self.category][0][1]

  def __str__(self):
    return "%s at %s K" % (self.n_analogue.name, self.temperature)

  def n_gzipped(self):
    return op.isfile(self.n_ungz_file_path()) == False

  def n_ungz_file_path(self):
    return op.join(data_path_optc, self.path)

  def n_data_folder(self):
    return op.join(data_path_optc, "%s" % self.id)

  def n_gz_file_path(self):
    return op.join(data_path_optc, "%s.txt.gz" % self.id)

  def n_h5_file_path(self):
    return op.join(self.n_data_folder(), "%s.h5" % self.id)

  def n_read_h5(self):
    with h5py.File(self.n_h5_file_path(), 'r') as f:
      data = f['spectrum_nval'][()]
    return data

  def n_download_filename(self):
    return "%s_%sK" % (self.id, self.temperature)

  def n_gz_file_size(self):
    return os.path.getsize(self.n_gz_file_path())


# Delete hooks for models, delete files if models are getting deleted
@listens_for(N_optc, 'after_delete')
def n_del_file(mapper, connection, target):
  if target.path:
    try:
      os.remove(op.join(data_path_optc, target.path))
    except OSError:
      # Don't care it was not deleted because it does not exist
      pass
    try:
      shutil.rmtree(op.join(data_path_optc, "%s" % target.id))
    except OSError:
      pass
    try:
      os.remove(op.join(data_path_optc, "%s.gz" % target.id))
    except OSError:
      pass

##########

# Authentication
class SC_User(db.Model):
  __bind_key__ = 'sc'
  __tablename__ = 'sc_users'
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
class SC_Object(db.Model):
  __bind_key__ = 'sc'
  __tablename__ = 'sc_analogues'
  id = Column(Integer, primary_key=True, autoincrement=True)
  sc_user_id = Column(Integer, ForeignKey('sc_users.id'), nullable=False)
  sc_user = db.relationship('SC_User', backref='sc_analogues')

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

  def sc_average_resolution(self):
    return numpy.average([s.resolution for s in self.sc_val])

  def sc_temperatures_to_sentence(self):
    temperatures = sorted([s.temperature for s in self.sc_val])
    t = [str(int(t)) if t.is_integer() else str(t) for t in temperatures]
    if len(t) > 1:
      return ', '.join(t[:-1]) + ' and ' + t[-1] + ' K'
    else:
      return t[0] + ' K'


# A single measured N (real part of refractive index)
class SC_spec(db.Model):
  __bind_key__ = 'sc'
  __tablename__ = 'sc_val'
  id = Column(Integer, primary_key=True, autoincrement=True)
  sc_analogue_id = Column(Integer, ForeignKey('sc_analogues.id'), nullable=False)
  sc_analogue = db.relationship('SC_Object', backref='sc_val')

  temperature = Column(Float, nullable=True)
  category = Column(Integer, default=0)
  cont_model = Column(String, nullable=False)
  resolution = Column(Float, nullable=True)
  wavenumber_range = Column(String, nullable=True)
  description = Column(UnicodeText)
  path = Column(String, nullable=False)

  SC_CATEGORIES = [('0', 'Polynomial'), ('1', 'Kurucz'), ('2', 'Other')]

  def sc_category_str(self):
    return [category for category in SC_optc.N_CATEGORIES if int(category[0]) == self.category][0][1]

  def __str__(self):
    return "%s at %s K" % (self.sc_analogue.name, self.temperature)

  def sc_gzipped(self):
    return op.isfile(self.sc_ungz_file_path()) == False

  def sc_ungz_file_path(self):
    return op.join(data_path_sc, self.path)

  def sc_data_folder(self):
    return op.join(data_path_sc, "%s" % self.id)

  def sc_gz_file_path(self):
    return op.join(data_path_sc, "%s.txt.gz" % self.id)

  def sc_h5_file_path(self):
    return op.join(self.sc_data_folder(), "%s.h5" % self.id)

  def sc_read_h5(self):
    with h5py.File(self.sc_h5_file_path(), 'r') as f:
      data = f['spectrum_cont'][()]
    return data

  def sc_download_filename(self):
    return "%s_%sK" % (self.id, self.temperature)

  def sc_gz_file_size(self):
    return os.path.getsize(self.sc_gz_file_path())


# Delete hooks for models, delete files if models are getting deleted
@listens_for(SC_spec, 'after_delete')
def sc_del_file(mapper, connection, target):
  if target.path:
    try:
      os.remove(op.join(data_path_sc, target.path))
    except OSError:
      # Don't care it was not deleted because it does not exist
      pass
    try:
      shutil.rmtree(op.join(data_path_sc, "%s" % target.id))
    except OSError:
      pass
    try:
      os.remove(op.join(data_path_sc, "%s.gz" % target.id))
    except OSError:
      pass
############


@manager.command
def seed():
  "Add seed data to the database."
  if db.session.query(func.count(User.id)).scalar() == 0:
    print('Adding test user..')
    #user = User(username='lab', email='olsthoorn@strw.leidenuniv.nl')
    user = User(username='lab', email='rocha@strw.leidenuniv.nl') #changed in 17/03/2021
    user.set_password('test')
    db.session.add(user)
    db.session.commit() # commit to get user ID

  if db.session.query(func.count(Analogue.id)).scalar() == 0:
    print('Adding ice analogues..')
    from application.seed import fetch
    fetch()

  print('Seed data successfully added to database')


@manager.command
def seed_refrac_index():
  "Add N_seed data to the database."
  if db.session.query(func.count(N_User.id)).scalar() == 0:
    print('Adding test user..')
    #user = User(username='lab', email='olsthoorn@strw.leidenuniv.nl')
    n_user = N_User(username='lab', email='rocha@strw.leidenuniv.nl') #changed in 17/03/2021
    n_user.set_password('test')
    db.session.add(n_user)
    db.session.commit() # commit to get user ID

  if db.session.query(func.count(N_Analogue.id)).scalar() == 0:
    print('Adding ice analogues.. (refrac index)')
    from application.seed_refrac_index import fetch_N
    fetch_N()

  print('Refrac index Seed data successfully added to database')

@manager.command
def seed_sc():
  "Add SC_seed data to the database."
  if db.session.query(func.count(SC_User.id)).scalar() == 0:
    print('Adding test user..')
    #user = User(username='lab', email='olsthoorn@strw.leidenuniv.nl')
    sc_user = SC_User(username='lab', email='rocha@strw.leidenuniv.nl') #changed in 17/03/2021
    sc_user.set_password('test')
    db.session.add(sc_user)
    db.session.commit() # commit to get user ID

  if db.session.query(func.count(SC_Object.id)).scalar() == 0:
    print('Adding ice analogues.. (refrac index)')
    from application.seed_spec_cont import fetch_SC
    fetch_SC()

  print('Refrac index Seed data successfully added to database')
