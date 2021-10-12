from application import db, data_path, data_path_optc, data_path_sc
from application.models import *
from application.config import Configuration
from urllib.request import urlopen
from urllib.error import HTTPError

# HTML parser
from bs4 import BeautifulSoup
import re

import os.path as op
import hashlib
from shutil import copyfile

# Concurrency - seed.py is multithreaded
from concurrent.futures import ThreadPoolExecutor as Pool
#from sqlalchemy.orm import scoped_session
#from sqlalchemy.orm import sessionmaker
import time
import numpy as np

# 869 spectra implemented

#Session = scoped_session(db.session)
pool_size = 4

# Normalize X Y data files
def write_data(f_in, target_file):
  with open(target_file, 'wt') as f_out:
    for i, line in enumerate(f_in.readlines()):
      normalized_line = ' '.join(line.decode('utf-8').strip().split())
      f_out.write(normalized_line + '\n')



def download_sc(url):
  filename = url.split('/')[-1]
  target_file = op.join(data_path_sc, filename)

  # Setup caching
  md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
  cache_dir = op.join(data_path_sc, '..', 'cache')
  try:
    os.mkdir(cache_dir)
  except OSError:
    pass
  cached_file = op.join(cache_dir, md5)

  # Load cache when available
  if op.isfile(cached_file):
    print('Loading data from cache for %s (%s)' % (url, md5))
    copyfile(cached_file, target_file)
  else:
    # Download file
    print('Downloading %s' % url)
    try:
      with urlopen(url) as f_in:
        write_data(f_in, target_file)
    except HTTPError as e:
      print('HTTP GET failed with error code', str(e.code))
      if e.code == 404:
        print('Retrying and replacing .DAT with .dat')
        url = url.replace('.DAT', '.dat')
        print('Downloading %s' % url)
        with urlopen(url) as f_in:
          write_data(f_in, target_file)
    copyfile(target_file, cached_file)

  return filename



# Add single data
def add_sc_single(sc_analogue, sc_spectrum, temperature = 15, cont_model='test'):
  filename = download_sc(sc_spectrum) if sc_spectrum[0:4] == 'http' else sc_spectrum

  db.session.add(SC_spec(
    sc_analogue_id = sc_analogue if type(sc_analogue) is int else sc_analogue.id,
    path = filename,
    temperature = temperature,
    cont_model=cont_model
  ))

# Add data to analogue
def add_spec_cont(sc_analogue, sc_val, temperature = 15, cont_model='test'):
  # Pre-download using multiple threads
  with Pool(max_workers=pool_size) as e:
    for sc_spectrum in e.map(download_sc, sc_val):
      temperature = temperature
      cont_model=cont_model
      add_sc_single(sc_analogue.id, sc_spectrum, temperature, cont_model)
  db.session.commit()


# Fetch remote data
def fetch_SC():
  "Fetches old database files from Leiden network"
  sc_user_id = db.session.query(SC_User).first().get_id()
  t_start = time.time()

  # HCOOH by Suzanne Bisschop
  # http://www.strw.leidenuniv.nl/lab/databases/hcooh/index.html


  sc_analogue = SC_Object(
    sc_user_id=sc_user_id,
    name='Pure $\ce{HCOOH}$',
    deposition_temperature=15, # Kelvin
    description='Deposited at 15K. Note that in the raw data the wavenumber range around 7-7.5 micron is not corrected for instrumental effects and is therefore difficult to use.',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )

  db.session.add(sc_analogue)
  db.session.commit()


  sc_val = []
  #T = [15, 30, 60, 75, 90, 105, 120, 135, 150, 165]
  T = [165]
  vn = np.linspace(10,len(T), len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    sc_val.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

  ##ADDINT TO OPTC FOLDER
  temperature = 165
  cont_model = 'test'
  add_spec_cont(sc_analogue, sc_val, temperature, cont_model)


  print('Fetching process took %.2f seconds' % (time.time()-t_start))
