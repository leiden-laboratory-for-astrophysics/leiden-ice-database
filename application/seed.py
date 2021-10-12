from application import db, data_path
from application.models import *
#from application.models import Spectrum, Analogue, User
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


# Download X Y data files
def download(url):
  filename = url.split('/')[-1]
  target_file = op.join(data_path, filename)

  # Setup caching
  md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
  cache_dir = op.join(data_path, '..', 'cache')
  try:
    os.mkdir(cache_dir)
  except OSError:
    pass
  cached_file = op.join(cache_dir, md5)

  # Load cache when available
  if op.isfile(cached_file):
    print('Loading data from cache for %s (%s)' % (url, md5))
    copyfile(cached_file, target_file)
    print('HERE 0')
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



# Add single spectrum
def add_spectrum(analogue, spectrum, temperature):
  print('HERE 1')
  filename = download(spectrum) if spectrum[0:4] == 'http' else spectrum
  print('HERE 2')

  db.session.add(Spectrum(
    analogue_id = analogue if type(analogue) is int else analogue.id,
    path = filename,
    temperature = temperature
  ))
  print('HERE 3')


# Add spectra to analogue
def add_spectra(analogue, spectra, temperature_parser):
  print('HERE 4')
  # Pre-download using multiple threads
  with Pool(max_workers=pool_size) as e:
    print('HERE 5')
    for spectrum in e.map(download, spectra):
      print('HERE 6', spectrum)
      temperature = float(temperature_parser(spectrum.split('_')[1].split('.txt')[0].replace('K', '').replace('.0','')))#temperature
      print('HERE 6X', temperature)
      add_spectrum(analogue.id, spectrum, temperature)
      print('HERE 6XX')
  print('STARTING DB SECTION COMMIT')
  db.session.commit()
  print('HERE 7')


# Fetch remote data
def fetch():
  print('HERE 8')
  "Fetches old database files from Leiden network"
  user_id = db.session.query(User).first().get_id()
  t_start = time.time()
  print('HERE 9')

  # HCOOH by Suzanne Bisschop
  # http://www.strw.leidenuniv.nl/lab/databases/hcooh/index.html
  analogue = Analogue(
    user_id=user_id,
    name='Pure $\ce{HCOOH}$',
    name2='Formic acid',
    name3 = 'Pure HCOOH',
    deposition_temperature=15, # Kelvin
    description='Deposited at 15K. Note that in the raw data the wavenumber range around 7-7.5 micron is not corrected for instrumental effects and is therefore difficult to use.',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464',
    path_annot='/Users/willrocha/T0/ice-database/application/annotations/HCOOH.dat'
  )
  print('HERE 10')
  
  db.session.add(analogue)
  db.session.commit()
  print('HERE 11')
  
  
  spectra = []
  #T = [15, 30, 60, 75, 90, 105, 120, 135, 150, 165]
  T = [15, 30, 60, 75, 90, 105, 120, 135, 150, 165]
  idx1 = 1
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
    #spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_' + str(T) + 'K.dat')
    #https://icedb.strw.leidenuniv.nl/spectrum/download/1/1_15.0K.txt

  def temperature(url):
    print('URL is:', url)
    return url

  #TT = temperature('hcooh100_')
  #print('Temperature is:', TT, type(TT))
  #temperature = [15,30]
  add_spectra(analogue, spectra, temperature)
  
  # HCOOH deposited at 145 K and warmed up by Suzanne Bisschop
  analogue = Analogue(
    user_id=user_id,
    name='Pure $\ce{HCOOH}$ deposited at 145 K',
    name2 = 'Formic acid',
    name3 = 'Pure HCOOH deposited at 145 K',
    deposition_temperature=145, # Kelvin
    description='Ice deposited at 145 K, cooled down to 15 K and subsequently warmed up.',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 45, 60, 75, 90, 120, 135, 145, 150, 165]
  idx1 = 11
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  

  
  # HCOOH 10% + CH3OH 90% by Suzanne Bisschop
  analogue = Analogue(
    user_id=user_id,
    name='$\ce{HCOOH}$ 10% + $\ce{CH3OH}$ 90%',
    name2 = 'Formic acid',
    name3 = 'HCOOH 10% + CH₃OH 90%',
    deposition_temperature=15,
    description='Note that in the raw data the wavenumber range around 7-7.5 micron is not corrected for instrumental effects and is therefore difficult to use. In case spectra of this frequency range are required please contact Suzanne Bisschop directly (bisschop at strw dot leidenuniv dot nl).',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()
  
  spectra = []
  T = [15, 30, 45, 60, 75]
  idx1 = 22
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  

  # HCOOH 11% + CO 89% by Suzanne Bisschop
  analogue = Analogue(
    user_id=user_id,
    name='$\ce{HCOOH}$ 11% + $\ce{CO}$ 89%',
    name2 = 'Formic acid',
    name3 = 'HCOOH 11% + CO 89%',
    deposition_temperature=15,
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()
  
  
  spectra = []
  T = [15, 30, 45, 75, 105, 135, 165]

  idx1 = 27
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  

  
  # HCOOH A% + H2O B% by Suzanne Bisschop
  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 20% + $\ce{H2O}$ 80%',
    name2 = 'Formic acid',
    name3 = 'HCOOH 20% + H₂O 80%',
    deposition_temperature=15, 
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()
  
  spectra = []
  T = [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]

  idx1 = 33
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  
  

  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 34% + $\ce{H2O}$ 66%',
    name2 = 'Formic acid',
    name3 = 'HCOOH 34% + H₂O 66%',
    deposition_temperature=15, 
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  
  spectra = []
  T = [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]

  idx1 = 44
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  # HCOOH A% + H2O B% by Suzanne Bisschop
  
  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 50% + $\ce{H2O}$ 50%',
    name2 = 'Formic acid',
    name3 = 'HCOOH 50% + H₂O 50%',
    deposition_temperature=15, 
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]

  idx1 = 55
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  
  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 6% + $\ce{H2O}$ 67% + $\ce{CO2}$ 27%',
    name2 = 'Formic acid',
    name3 = 'HCOOH 6% + H₂O 67% + CO₂ 27%',
    deposition_temperature=15,
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()
  
  spectra = []
  T = [15]
  idx1 = 66
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')  

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)

  
  
  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 6% + $\ce{H2O}$ 68% + $\ce{CH3OH}$ 26%',
    name2 = 'Formic acid',
    name3 = 'HCOOH 6% + H₂O 68% + CH₃OH 26%',
    deposition_temperature=15,
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()
  
  
  spectra = []
  T = [15]
  idx1 = 67
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)

  
  # HCOOH 8% + H2O 62% + CO 30% by Suzanne Bisschop
  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 8% + $\ce{H2O}$ 62% + $\ce{CO}$ 30%',
    name2 = 'Formic acid',
    name3 = 'HCOOH 8% + H₂O 62% + CO 30%',
    deposition_temperature=15,
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()
  
  spectra = []
  T = [15]
  idx1 = 68
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  
  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 9% + $\ce{CO2}$ 91%',
    name2 = 'Formic acid',
    name3 = 'HCOOH 9% + CO₂ 91%',
    deposition_temperature=15,
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()
  
  spectra = []
  T = [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]
  idx1 = 69
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)

  

  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 9% + $\ce{H2O}$ 91%',
    name2 = 'Formic acid',
    name3 = 'HCOOH 9% + H₂O 91%',
    deposition_temperature=15,
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()
  
  spectra = []
  T = [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]#, 135, 150, 165]
  idx1 = 80
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)

  
  analogue = Analogue(
    user_id=user_id,
    name='Pure $\ce{H2O}$ 10000 L',
    name2 = 'Water',
    name3 = 'Pure H₂O 10000 L',
    deposition_temperature=15,
    description='Total thickness 10000 L',
    author='Öberg et al',
    DOI='10.1051/0004-6361:20065881'
  )
  db.session.add(analogue)
  db.session.commit()
  
  spectra = []
  T = [15, 45, 75, 105, 135]

  idx1 = 91
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  analogue = Analogue(
    user_id=user_id,
    name='Pure $\ce{H2O}$ 3000 L',
    name2 = 'Water',
    name3 = 'Pure H₂O 3000 L',
    deposition_temperature=15,
    description='Total thickness 3000 L',
    author='Öberg et al',
    DOI='10.1051/0004-6361:20065881'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 45, 75, 105, 135]

  idx1 = 96
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)

  

  count = 1
  for thickness in ['10000', '3000']:
    analogue = Analogue(
      user_id=user_id,
      name='Pure $\ce{C{^{18}O2}}$ (' + thickness + ' L)',
      name2 = 'carbon_monoxide',
      name3 = 'Pure C¹⁸O₂ (' + thickness + ' L)',
      deposition_temperature=15,
      description='Total thickness ' + thickness + ' L',
      author='Öberg et al',
      DOI='10.1051/0004-6361:20065881'
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    T = [15, 45, 75, 105]
    if count == 1:
      idx1 = 101
    else:
      idx1 = 105
    idx2 = idx1 + len(T) - 1
    vn = np.linspace(idx1,idx2, len(T), dtype=int)
    print('VN is', vn)
    for i,j in zip(vn,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)
    count = count + 1
  
  
  
  # H2O 18O2 x:x (xxxxx L thickness) by Oberg et at al. 2006
  for attributes in [
    {'ratio': '1:1', 'thickness': '20000'},
    {'ratio': '1:2', 'thickness': '30000'},
    {'ratio': '2:1', 'thickness': '15000'},
    {'ratio': '2:1', 'thickness': '4500'},
    {'ratio': '1:1', 'thickness': '6000'},
    {'ratio': '1:2', 'thickness': '9000'},
    {'ratio': '4:1', 'thickness': '3750'},
    {'ratio': '1:4', 'thickness': '15000'},
    {'ratio': '1:1', 'thickness': '2000'}]:

    a = attributes['ratio'].split(':')[0]
    b = attributes['ratio'].split(':')[1]

    analogue = Analogue(
      user_id = user_id,
      name='$\ce{H2O}$:$\ce{C{^{18}O2}}$ ' + a + ':' + b + ' (' + attributes['thickness'] + ' L)',
      name2 = 'water',
      name3 = 'H₂O:C¹⁸O₂ ' + a + ':' + b + ' (' + attributes['thickness'] + ' L)',
      deposition_temperature=15,
      description='Total thickness ' + attributes['thickness'] + ' L',
      author='Öberg et al',
      DOI='10.1051/0004-6361:20065881'
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if attributes['thickness'] == '20000':
      T = [15, 30, 45, 75, 105, 135]
      idx1 = 109
    elif attributes['thickness'] == '30000':
      T = [15, 30, 45, 75, 105, 135]
      idx1 = 115
    elif attributes['thickness'] == '15000':
      T = [15, 45, 75, 105, 135]
      idx1 = 121
    elif attributes['thickness'] == '4500':
      T = [15, 45, 75, 105, 135]
      idx1 = 126
    elif attributes['thickness'] == '6000':
      T = [15, 45, 75, 105, 135]
      idx1 = 131
    elif attributes['thickness'] == '9000':
      T = [15, 45, 75, 105, 135]
      idx1 = 136
    elif attributes['thickness'] == '3750':
      T = [15, 45, 75, 105, 135]
      idx1 = 141
    elif attributes['thickness'] == '15000':
      T = [15, 45, 75, 105, 135]
      idx1 = 146
    elif attributes['thickness'] == '2000':
      T = [15, 45, 75, 105, 135]
      idx1 = 151
    idx2 = idx1 + len(T) - 1
    vn = np.linspace(idx1,idx2, len(T), dtype=int)
    print('VN is', vn)
    for i,j in zip(vn,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)
  

  analogue = Analogue(
    user_id=user_id,
    name='$\ce{H2O}$:$\ce{CO2}$ (10:1)',
    name2 = 'Water',
    name3 = 'H₂O:CO₂ (10:1)',
    deposition_temperature=10,
    description='None',
    author='Ehrenfreund and Schlemmer',
    DOI='NA'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [10, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 185]

  idx1 = 156
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  analogue = Analogue(
    user_id=user_id,
    name='$\ce{CO2}$:$\ce{H2O}$ (1:1)',
    name2 = 'Water',
    name3 = 'CO₂:H₂O (1:1)',
    deposition_temperature=10,
    description='None',
    author='Ehrenfreund and Schlemmer',
    DOI='NA'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [10, 30, 35, 40, 43, 50, 55, 60, 65, 70, 75, 80, 82, 85, 88, 90, 92, 95, 100, 105, 110, 115, 120, 125, 130, 138, 150, 155, 177, 187]

  idx1 = 174
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  for attributes in [
    {'ratio': '10:1'},
    {'ratio': '3:1'},
    {'ratio': '2:1'},
    {'ratio': '1:1'},
    {'ratio': '1:2'},
    {'ratio': '1:3'},
    {'ratio': '1:10'}]:

    a = attributes['ratio'].split(':')[0]
    b = attributes['ratio'].split(':')[1]

    analogue = Analogue(
      user_id = user_id,
      name='$\ce{CO2}$:$\ce{CH3OH}$ ' + '(' + a + ':' + b + ')',
      name2 = 'carbon dioxide',
      name3 = 'CO₂:CH₃OH ' + '(' + a + ':' + b + ')',
      deposition_temperature=10,
      description='',
      author='Ehrenfreund and Schlemmer',
      DOI=''
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if attributes['ratio'] == '10:1':
      T = [10, 20, 28, 38, 45, 50, 54, 63, 68, 75]
      idx1 = 201
    elif attributes['ratio'] == '3:1':
      T = [10, 38, 65, 90, 96, 105, 108, 112, 130]
      idx1 = 211
    elif attributes['ratio'] == '2:1':
      T = [10, 30, 40, 60, 75, 90, 105, 108, 110, 125, 145]
      idx1 = 220
    elif attributes['ratio'] == '1:1':
      T = [10, 58, 72, 84, 95, 100, 105, 108, 110, 115, 116, 120, 121, 130, 145]
      idx1 = 232
    elif attributes['ratio'] == '1:2':
      T = [10, 65, 80, 90, 112, 125, 140, 147, 155]
      idx1 = 247
    elif attributes['ratio'] == '1:3':
      T = [10, 65, 112, 125, 130, 140, 150, 160]
      idx1 = 257
    elif attributes['ratio'] == '1:10':
      T = [10, 65, 115, 125, 135, 140, 160, 180]
      idx1 = 265
    idx2 = idx1 + len(T) - 1
    vn = np.linspace(idx1,idx2, len(T), dtype=int)
    print('VN is', vn)
    for i,j in zip(vn,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)

  for attributes in [
    {'ratio': '9:1:2'},
    {'ratio': '0.2:0.6:1'},
    {'ratio': '0.4:0.6:1'},
    {'ratio': '1:0.6:1'},
    {'ratio': '0.7:0.7:1'},
    {'ratio': '0.8:0.9:1'},
    {'ratio': '1:1:1'},
    {'ratio': '0.7:1:1'},
    {'ratio': '0.6:1:0.8'},
    {'ratio': '1.2:0.7:1'},
    {'ratio': '0.5:1:1'},
    {'ratio': '0.9:1.4:1'},
    {'ratio': '0.2:0.5:1'},
    {'ratio': '0.3:0.5:1'},
    {'ratio': '0.3:0.7:1'},
    {'ratio': '1.1:1.2:1'},
    {'ratio': '0.9:0.3:1'}]:

    a = attributes['ratio'].split(':')[0]
    b = attributes['ratio'].split(':')[1]
    c = attributes['ratio'].split(':')[2]

    analogue = Analogue(
      user_id = user_id,
      name='$\ce{H2O}$:$\ce{CH3OH}$:$\ce{CO2}$ ' + '(' + a + ':' + b + ':' + c + ')',
      name2 = 'Water',
      name3 = 'H₂O:CH₃OH:CO₂ ' + '(' + a + ':' + b + ':' + c + ')',
      deposition_temperature=10,
      description='',
      author='Ehrenfreund and Schlemmer',
      DOI=''
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if attributes['ratio'] == '9:1:2':
      T = [10, 30, 45, 65, 70, 80, 85, 96, 107, 120, 130, 140, 150, 160, 165, 175,185]
      idx1 = 273
    elif attributes['ratio'] == '0.2:0.6:1':
      T = [10, 65, 80, 90, 103, 112, 120, 130, 140]
      idx1 = 290
    elif attributes['ratio'] == '0.4:0.6:1':
      T = [10, 50, 60, 80, 90, 100, 110, 120, 125, 130, 140]
      idx1 = 299
    elif attributes['ratio'] == '1:0.6:1':
      T = [10, 30, 42, 65, 80, 90, 96, 100, 106, 110, 115, 120, 125, 127, 130, 135, 137, 180]
      idx1 = 310
    elif attributes['ratio'] == '0.7:0.7:1':
      T = [10, 80, 90, 96, 105, 109, 110, 112, 114, 116, 118, 120, 122, 123, 127, 134, 141, 146]
      idx1 = 328
    elif attributes['ratio'] == '0.8:0.9:1':
      T = [10, 65, 82, 90, 100, 110, 114, 125, 135]
      idx1 = 346
    elif attributes['ratio'] == '1:1:1':
      T = [10, 65, 80, 90, 96, 105, 106, 110, 111, 112, 115, 116, 117, 117.5, 118, 119, 120, 121, 123, 130, 136, 145]
      idx1 = 355
    elif attributes['ratio'] == '0.7:1:1':
      T = [10, 65, 80, 92, 96, 105, 107, 108, 109, 110, 111, 112, 120]
      idx1 = 377
    elif attributes['ratio'] == '0.6:1:0.8':
      T = [10, 70, 80, 90, 105, 107, 112, 115, 120, 121]
      idx1 = 390
    elif attributes['ratio'] == '1.2:0.7:1':
      T = [10, 52, 87, 102, 119]
      idx1 = 400
    elif attributes['ratio'] == '0.7:0.9:1':
      T = [10, 48, 52, 62, 64, 69, 77, 83, 90, 94, 100, 108, 111, 119, 123, 134]
      idx1 = 405
    elif attributes['ratio'] == '0.5:1:1':
      T = [10]
      idx1 = 421
    elif attributes['ratio'] == '0.9:1.4:1':
      T = [10, 67, 77, 88, 101, 113, 120, 125]
      idx1 = 422
    elif attributes['ratio'] == '0.2:0.5:1':
      T = [10, 98]
      idx1 = 430
    elif attributes['ratio'] == '0.3:0.5:1':
      T = [10, 68, 85, 95]
      idx1 = 432
    elif attributes['ratio'] == '0.3:0.7:1':
      T = [10, 48, 53, 62, 67, 71, 73, 77, 79, 82]
      idx1 = 436
    elif attributes['ratio'] == '1.1:1.2:1':
      T = [10, 51, 97, 131]
      idx1 = 446
    elif attributes['ratio'] == '0.9:0.3:1':
      T = [10, 30, 52, 68, 74, 77, 80, 85, 87, 92, 98, 115]
      idx1 = 450
    
    idx2 = idx1 + len(T) - 1
    vn = np.linspace(idx1,idx2, len(T), dtype=int)
    print('VN is', vn)
    for i,j in zip(vn,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)
  
  
  analogue = Analogue(
    user_id=user_id,
    name='$\ce{H2O}$:$\ce{CH3OH}$:$\ce{CO2}$:$\ce{NH3}$ (0.7:0.7:1:0.7)',
    name2 = 'Water',
    name3 = 'H₂O:CH₃OH:CO₂:NH₃ (0.7:0.7:1:0.7)',
    deposition_temperature=10,
    description='None',
    author='Ehrenfreund and Schlemmer',
    DOI='NA'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [10, 51, 59, 69, 76, 84, 88, 94, 99, 104]

  idx1 = 462
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  

  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)
  
  for attributes in [
    {'ratio': '0.6:0.7:1:0.1'},
    {'ratio': '0.4:0.6:1:0.23'}]:

    a = attributes['ratio'].split(':')[0]
    b = attributes['ratio'].split(':')[1]
    c = attributes['ratio'].split(':')[2]
    d = attributes['ratio'].split(':')[3]

    analogue = Analogue(
      user_id = user_id,
      name='$\ce{H2O}$:$\ce{CH3OH}$:$\ce{CO2}$:$\ce{CH4}$ ' + '(' + a + ':' + b + ':' + c + ':' + d + ')',
      name2 = 'Water',
      name3 = 'H₂O:CH₃OH:CO₂:CH₄ ' + '(' + a + ':' + b + ':' + c + ':' + d + ')',
      deposition_temperature=10,
      description='',
      author='Ehrenfreund and Schlemmer',
      DOI=''
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if attributes['ratio'] == '0.6:0.7:1:0.1':
      T = [10, 51, 87, 119]
      idx1 = 472
    elif attributes['ratio'] == '0.4:0.6:1:0.23':
      T = [10]
      idx1 = 476
      
    idx2 = idx1 + len(T) - 1
    vn = np.linspace(idx1,idx2, len(T), dtype=int)
    print('VN is', vn)
    for i,j in zip(vn,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)



  for name in {
      'CH3OH',
      'CH4',
      'CO2',
      'CO',
      'HCOOH',
      'COmixCH3OH_1_1',
      'COmixCO2_1_1',
      'COmixHCOOH_1_1',
      'COoverCH3OH',
      'COoverCH4',
      'COoverCO2',
      'COoverHCOOH',
      'COunderCH3OH',
      'COunderCH4',
      'COunderCO2',
      'COunderHCOOH'
      }:

    if 'mix' in name:
      parts = name.split('_')[0].split('mix')
      display_name = '$\ce{'+parts[0]+'}$:$\ce{'+parts[1]+'}$ 1:1'
    elif 'over' in name:
      parts = name.split('over')
      display_name = '$\ce{'+parts[0]+'}$ over $\ce{'+parts[1]+'}$'
    elif 'under' in name:
      parts = name.split('under')
      display_name = '$\ce{'+parts[0]+'}$ under $\ce{'+parts[1]+'}$'
    else:
      display_name = 'Pure $\ce{'+name+'}$'

    analogue = Analogue(
      user_id = user_id,
      name=display_name,
      name2 = 'carbon monoxide',
      name3 = name,
      deposition_temperature=10,
      description='',
      author='Fraser',
      DOI='NA'
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if name == 'CH3OH':
      T = [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100, 115, 130, 145, 160]
      idx1 = 627
    elif name == 'CH4':
      T = [15, 18, 20, 22.5, 25, 28, 35, 40, 50]
      idx1 = 661
    elif name == 'CO2':
      T = [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100]
      idx1 = 688
    elif name == 'CO':
      T = [15, 18, 20, 22.5, 25, 28, 30, 35]
      idx1 = 519
    elif name == 'HCOOH':
      T = [14.1, 16, 19.5, 21.7, 24.5, 27.6, 29.5, 34.6, 39, 59.6, 79.8, 99.2, 160.3]
      idx1 = 477
    elif name == 'COmixCH3OH_1_1':
      T = [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100, 115, 130, 145, 160]
      idx1 = 589
    elif name == 'COmixCO2_1_1':
      T = [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100]
      idx1 = 490
    elif name == 'COmixHCOOH_1_1':
      T = [14.4, 17, 19.4, 22.7, 24.3, 27.1, 29.6, 34.5, 39.5, 59.3, 79.3, 99.8, 129, 160.1]
      idx1 = 556
    elif name == 'COoverCH3OH':
      T = [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100, 115, 130, 145, 160]
      idx1 = 570
    elif name == 'COoverCH4':
      T = [15, 18, 20, 22.5, 25, 28, 30, 35, 40]
      idx1 = 670
    elif name == 'COoverCO2':
      T = [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100]
      idx1 = 527
    elif name == 'COoverHCOOH':
      T = [14.3, 17.2, 19.5, 22.2, 24.5, 27.5, 29.5, 34.5, 39.1, 59.3, 79.2, 99.4, 129.5, 159.5]
      idx1 = 505
    elif name == 'COunderCH3OH':
      T = [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100, 115, 130, 145, 160]
      idx1 = 608
    elif name == 'COunderCH4':
      T = [15, 18, 20, 22.5, 25, 28, 30, 35, 40]
      idx1 = 679
    elif name == 'COunderCO2':
      T = [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100]
      idx1 = 646
    elif name == 'COunderHCOOH':
      T = [14.5, 17.7, 19.8, 22.3, 24.5, 27.2, 29.5, 34.6, 39.3, 59.6, 79.2, 99.3, 128.8, 159.2]
      idx1 = 542

      
    idx2 = idx1 + len(T) - 1
    vn = np.linspace(idx1,idx2, len(T), dtype=int)
    print('VN is', vn)
    for i,j in zip(vn,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
    
    

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)
  

  for name in {
    'CO',
    'CO2',
    'COoverCO2_1_1',
    'COoverCO2_1_2',
    'CO2overCO_1_1',
    'CO2overCO_2_1',
    'CO2overCO_3_1',
    'CO2overCO_10_1',
    'COmixCO2_2_1',
    'COmixCO2_1_1',
    'COmixCO2_1_10',
    }:

    if 'mix' in name:
      parts = name.split('mix')
      parts2 = parts[1].split('_')
      print('Parts:', parts)
      print('Parts2', parts2)
      display_name = '$\ce{'+parts[0]+'}$:$\ce{'+parts2[0]+'}$' + ' ' + '(' + str(parts2[1]) + ':' + str(parts2[2]) + ')'
    elif 'over' in name:
      parts = name.split('over')
      parts2 = parts[1].split('_')
      display_name = '$\ce{'+parts[0]+'}$ over $\ce{'+parts2[0]+'}$' + ' ' + '(' + str(parts2[1]) + ':' + str(parts2[2]) + ')'
    else:
      display_name = 'Pure $\ce{'+name+'}$'

    analogue = Analogue(
      user_id = user_id,
      name=display_name,
      name2 = 'carbon monoxide',
      name3 = name,
      deposition_temperature=15,
      description='',
      author='Suzanne Bisschop',
      DOI='NA'
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if name == 'CO':
      T = [15, 18, 20, 22, 25, 30, 35, 40, 45]
      idx1 = 703
    elif name == 'CO2':
      T = [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 130]
      idx1 = 712
    elif name == 'COoverCO2_1_1':
      T = [15, 18, 20, 22, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110]
      idx1 = 727
    elif name == 'COoverCO2_1_2':
      T = [15, 18, 20, 22, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110]
      idx1 = 743
    elif name == 'CO2overCO_1_1':
      T = [15, 18, 20, 22, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110]
      idx1 = 759
    elif name == 'CO2overCO_2_1':
      T = [15, 18, 20, 22, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110]
      idx1 = 775
    elif name == 'CO2overCO_3_1':
      T = [15, 18, 20, 22, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110]
      idx1 = 791
    elif name == 'CO2overCO_10_1':
      T = [15, 18, 20, 25, 30, 35, 40, 45, 60, 70, 80, 100, 110]
      idx1 = 807
    elif name == 'COmixCO2_2_1':
      T = [15, 18, 20, 22, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 130]
      idx1 = 820
    elif name == 'COmixCO2_1_1':
      T = [15, 18, 20, 22, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 130]
      idx1 = 837
    elif name == 'COmixCO2_1_10':
      T = [15, 18, 20, 22, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110]
      idx1 = 854

        
    idx2 = idx1 + len(T) - 1
    vn = np.linspace(idx1,idx2, len(T), dtype=int)
    print('VN is', vn)
    for i,j in zip(vn,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
      
      

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)


  analogue = Analogue(
    user_id=user_id,
    name='Pure $\ce{CH3CHO}$',
    name2 = 'Acetaldehyde',
    name3 = 'Pure CH₃CHO',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 90, 110, 120]
  idx1 = [873, 872, 874, 875, 877, 878]
  #idx2 = idx1 + len(T) - 1
  #vn = np.linspace(idx1,idx2, len(T), dtype=int)
  #print('VN is', vn)
  for i,j in zip(idx1,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)



  analogue = Analogue(
    user_id=user_id,
    name='$\ce{H2O}$:$\ce{CH3CHO}$ (20:1)',
    name2 = 'Acetaldehyde',
    name3 = 'H₂O:CH₃CHO (20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 90, 110, 120, 140, 160]
  idx1 = 890
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)



  analogue = Analogue(
    user_id=user_id,
    name='$\ce{CO}$:$\ce{CH3CHO}$ (20:1)',
    name2 = 'Acetaldehyde',
    name3 = 'CO:CH₃CHO (20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30]
  idx1 = 916
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  
  analogue = Analogue(
    user_id=user_id,
    name='$\ce{CH3OH}$:$\ce{CH3CHO}$ (20:1)',
    name2 = 'Acetaldehyde',
    name3 = 'CH₃OH:CH₃CHO (20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 90, 110, 120, 140]
  idx1 = 916
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)




  analogue = Analogue(
    user_id=user_id,
    name='$\ce{CO}$:$\ce{CH3OH}$:$\ce{CH3CHO}$ (20:20:1)',
    name2 = 'Acetaldehyde',
    name3 = 'CO:CH₃OH:CH₃CHO (20:20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 90, 110, 120]
  idx1 = 918
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)







  #ETHANOL
  analogue = Analogue(
    user_id=user_id,
    name='Pure $\ce{CH3CH2OH}$',
    name2 = 'Ethanol',
    name3 = 'Pure CH₃CH₂OH',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 100, 120, 130, 140, 150]
  idx1 = 924
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)



  analogue = Analogue(
    user_id=user_id,
    name='$\ce{H2O}$:$\ce{CH3CH2O}$ (20:1)',
    name2 = 'Ethanol',
    name3 = 'H₂O:CH₃CH₂OH (20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 100, 120, 130, 140, 150, 160]
  idx1 = 932
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)



  analogue = Analogue(
    user_id=user_id,
    name='$\ce{CO}$:$\ce{CH3CH2OH}$ (20:1)',
    name2 = 'Acetaldehyde',
    name3 = 'CO:CH₃CH₂OH (20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30]
  idx1 = 941
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  
  analogue = Analogue(
    user_id=user_id,
    name='$\ce{CH3OH}$:$\ce{CH3CH2OH}$ (20:1)',
    name2 = 'Acetaldehyde',
    name3 = 'CH₃OH:CH₃CH₂OH (20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 100, 120, 130, 140, 150]
  idx1 = 943
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)




  analogue = Analogue(
    user_id=user_id,
    name='$\ce{CO}$:$\ce{CH3OH}$:$\ce{CH3CH2OH}$ (20:20:1)',
    name2 = 'Acetaldehyde',
    name3 = 'CO:CH₃OH:CH₃CH₂OH (20:20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 100, 120, 130, 140, 150]
  idx1 = 951
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)






  #Dimethyl ether
  analogue = Analogue(
    user_id=user_id,
    name='Pure $\ce{CH3OCH3}$',
    name2 = 'Dimethyl ether',
    name3 = 'Pure CH₃OCH₃',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 90, 100]
  idx1 = 959
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)



  analogue = Analogue(
    user_id=user_id,
    name='$\ce{H2O}$:$\ce{CH3OCH3}$ (20:1)',
    name2 = 'Dimethyl ether',
    name3 = 'H₂O:CH₃OCH₃ (20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 90, 100, 120, 140, 160]
  idx1 = 964
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)



  analogue = Analogue(
    user_id=user_id,
    name='$\ce{CO}$:$\ce{CH3OCH3}$ (20:1)',
    name2 = 'Dimethyl ether',
    name3 = 'CO:CH₃OCH₃ (20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30]
  idx1 = 972
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)


  
  analogue = Analogue(
    user_id=user_id,
    name='$\ce{CH3OH}$:$\ce{CH3OCH3}$ (20:1)',
    name2 = 'Dimethyl ether',
    name3 = 'CH₃OH:CH₃OCH₃ (20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 90, 100, 120]
  idx1 = 974
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)




  analogue = Analogue(
    user_id=user_id,
    name='$\ce{CO}$:$\ce{CH3OH}$:$\ce{CH3OCH3}$ (20:20:1)',
    name2 = 'Dimethyl ether',
    name3 = 'CO:CH₃OH:CH₃OCH₃ (20:20:1)',
    deposition_temperature=15, # Kelvin
    description='',
    author='J. Terwisscha van Scheltinga',
    DOI='10.1051/0004-6361/201731998'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 90, 100]
  idx1 = 980
  idx2 = idx1 + len(T) - 1
  vn = np.linspace(idx1,idx2, len(T), dtype=int)
  print('VN is', vn)
  for i,j in zip(vn,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)



  #Dimethyl ether
  analogue = Analogue(
    user_id=user_id,
    name='Pure $\ce{C3H6O}$',
    name2 = 'Acetone',
    name3 = 'Pure C₃H₆O',
    deposition_temperature=15, # Kelvin
    description='',
    author='Marina Gomes Rachid',
    DOI='10.1051/0004-6361/202037497'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  T = [15, 30, 70, 90, 110, 120, 130, 140]
  idx1 = [986, 987, 988, 990, 991, 993, 994, 995]
  #idx2 = idx1 + len(T) - 1
  #vn = np.linspace(idx1,idx2, len(T), dtype=int)
  #print('VN is', vn)
  for i,j in zip(idx1,T):
    spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')
  
  def temperature(url):
    return url

  add_spectra(analogue, spectra, temperature)




  for attributes in [
    {'ratio': '1:5'},
    {'ratio': '1:20'}]:

    a = attributes['ratio'].split(':')[0]
    b = attributes['ratio'].split(':')[1]
    #c = attributes['ratio'].split(':')[2]
    #d = attributes['ratio'].split(':')[3]

    analogue = Analogue(
      user_id = user_id,
      name='$\ce{C3H6O}$:$\ce{H2O}$ ' + '(' + a + ':' + b + ')',
      name2 = 'Acetone',
      name3 = 'C₃H₆O:H₂O ' + '(' + a + ':' + b + ')',
      deposition_temperature=15,
      description='',
      author='Marina Gomes Rachid',
      DOI=''
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if attributes['ratio'] == '1:5':
      T = [15, 30, 70, 90, 100, 120, 140, 160]
      idx1 = 996
    elif attributes['ratio'] == '1:20':
      T = [15, 30, 70, 90, 100, 110, 120, 140, 160]
      idx1 = 1004
        
    idx2 = idx1 + len(T) - 1
    vn = np.linspace(idx1,idx2, len(T), dtype=int)
    print('VN is', vn)
    for i,j in zip(vn,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)


  for attributes in [
    {'ratio': '1:5'},
    {'ratio': '1:20'}]:

    a = attributes['ratio'].split(':')[0]
    b = attributes['ratio'].split(':')[1]
    #c = attributes['ratio'].split(':')[2]
    #d = attributes['ratio'].split(':')[3]

    analogue = Analogue(
      user_id = user_id,
      name='$\ce{C3H6O}$:$\ce{CO}$ ' + '(' + a + ':' + b + ')',
      name2 = 'Acetone',
      name3 = 'C₃H₆O:CO ' + '(' + a + ':' + b + ')',
      deposition_temperature=15,
      description='',
      author='Marina Gomes Rachid',
      DOI=''
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if attributes['ratio'] == '1:5':
      T = [15, 30]
      idx1 = 1013
    elif attributes['ratio'] == '1:20':
      T = [15, 30]
      idx1 = 1015
          
    idx2 = idx1 + len(T) - 1
    vn = np.linspace(idx1,idx2, len(T), dtype=int)
    print('VN is', vn)
    for i,j in zip(vn,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)

  

  for attributes in [
    {'ratio': '1:5'},
    {'ratio': '1:20'}]:

    a = attributes['ratio'].split(':')[0]
    b = attributes['ratio'].split(':')[1]
    #c = attributes['ratio'].split(':')[2]
    #d = attributes['ratio'].split(':')[3]

    analogue = Analogue(
      user_id = user_id,
      name='$\ce{C3H6O}$:$\ce{CO2}$ ' + '(' + a + ':' + b + ')',
      name2 = 'Acetone',
      name3 = 'C₃H₆O:CO₂ ' + '(' + a + ':' + b + ')',
      deposition_temperature=15,
      description='',
      author='Marina Gomes Rachid',
      DOI=''
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if attributes['ratio'] == '1:5':
      T = [15, 30, 70, 90, 100]
      idx1 = 1017
      idx2 = idx1 + len(T) - 1
      vn = np.linspace(idx1,idx2, len(T), dtype=int)
      print('VN is', vn)
    elif attributes['ratio'] == '1:20':
      T = [15, 30, 70, 90, 100]
      vn = [1022, 1023, 1024, 1025, 1027]
            
    #idx2 = idx1 + len(T) - 1
    #vn = np.linspace(idx1,idx2, len(T), dtype=int)
    #print('VN is', vn)
    for i,j in zip(vn,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)

  

  for attributes in [
    {'ratio': '1:5'},
    {'ratio': '1:20'}]:

    a = attributes['ratio'].split(':')[0]
    b = attributes['ratio'].split(':')[1]
    #c = attributes['ratio'].split(':')[2]
    #d = attributes['ratio'].split(':')[3]

    analogue = Analogue(
      user_id = user_id,
      name='$\ce{C3H6O}$:$\ce{CH3OH}$ ' + '(' + a + ':' + b + ')',
      name2 = 'Acetone',
      name3 = 'C₃H₆O:CH₃OH ' + '(' + a + ':' + b + ')',
      deposition_temperature=15,
      description='',
      author='Marina Gomes Rachid',
      DOI=''
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if attributes['ratio'] == '1:5':
      T = [15, 30, 70, 90, 100, 110, 120, 140]
      idx1 = 1028
    elif attributes['ratio'] == '1:20':
      T = [15, 30, 70, 90, 100, 110, 120, 140]
      idx1 = 1036
              
    idx2 = idx1 + len(T) - 1
    vn = np.linspace(idx1,idx2, len(T), dtype=int)
    print('VN is', vn)
    for i,j in zip(vn,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)


  
  for attributes in [
    {'ratio': '1:2.5:2.5'},
    {'ratio': '1:10:10'}]:

    a = attributes['ratio'].split(':')[0]
    b = attributes['ratio'].split(':')[1]
    c = attributes['ratio'].split(':')[2]
    #d = attributes['ratio'].split(':')[3]

    analogue = Analogue(
      user_id = user_id,
      name='$\ce{C3H6O}$:$\ce{H2O}$:$\ce{CO2}$ ' + '(' + a + ':' + b + ':' + c + ')',
      name2 = 'Acetone',
      name3 = 'C₃H₆O:H₂O:CO₂ ' + '(' + a + ':' + b + ':' + c + ')',
      deposition_temperature=15,
      description='',
      author='Marina Gomes Rachid',
      DOI=''
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if attributes['ratio'] == '1:2.5:2.5':
      T = [15, 30, 70, 90, 100, 110, 120, 140, 160]
      idx1 = [1044, 1048, 1049, 1050, 1057, 1053, 1058, 1059, 1060]
    elif attributes['ratio'] == '1:10:10':
      T = [15, 30, 70, 90, 100, 110, 120, 140]
      idx1 = [1045, 1061, 1062, 1063, 1065, 1066, 1067, 1064]
                
    #idx2 = idx1 + len(T) - 1
    #vn = np.linspace(idx1,idx2, len(T), dtype=int)
    #print('VN is', vn)
    for i,j in zip(idx1,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)


  


  for attributes in [
    {'ratio': '1:2.5:2.5'},
    {'ratio': '1:10:10'}]:

    a = attributes['ratio'].split(':')[0]
    b = attributes['ratio'].split(':')[1]
    c = attributes['ratio'].split(':')[2]
    #d = attributes['ratio'].split(':')[3]

    analogue = Analogue(
      user_id = user_id,
      name='$\ce{C3H6O}$:$\ce{CO}$:$\ce{CH3OH}$ ' + '(' + a + ':' + b + ':' + c + ')',
      name2 = 'Acetone',
      name3 = 'C₃H₆O:CO:CH₃OH ' + '(' + a + ':' + b + ':' + c + ')',
      deposition_temperature=15,
      description='',
      author='Marina Gomes Rachid',
      DOI=''
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    if attributes['ratio'] == '1:2.5:2.5':
      T = [15, 30, 70, 90, 100, 110, 120, 140]
      idx1 = [1046, 1068, 1069, 1070, 1071, 1072, 1073, 1074]
    elif attributes['ratio'] == '1:10:10':
      T = [15, 30, 70, 90, 100, 110, 120, 140]
      idx1 = [1047, 1075, 1076, 1077, 1078, 1079, 1080, 1081]
                  
    #idx2 = idx1 + len(T) - 1
    #vn = np.linspace(idx1,idx2, len(T), dtype=int)
    #print('VN is', vn)
    for i,j in zip(idx1,T):
      spectra.append('https://icedb.strw.leidenuniv.nl/spectrum/download/' + str(i) + '/' + str(i) + '_' + str(j) + '.' + str(0) + 'K.txt')

    def temperature(url):
      return url

    add_spectra(analogue, spectra, temperature)


  






  print('Fetching process took %.2f seconds' % (time.time()-t_start))
