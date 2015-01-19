from application import db, data_path
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
import time

# 869 spectra implemented

pool_size = 4

# Normalize X Y data files
def write_data(f_in, target_file):
  with open(target_file, 'wt') as f_out:
    f_out.write(f_in.readall().decode('utf-8'))


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
  filename = download(spectrum) if spectrum[0:4] == 'http' else spectrum

  db.session.add(Spectrum(
    analogue_id = analogue if type(analogue) is int else analogue.id,
    path = filename,
    temperature = temperature
  ))


# Add spectra to analogue
def add_spectra(analogue, spectra, temperature_parser):
  # Pre-download using multiple threads
  with Pool(max_workers=pool_size) as e:
    for spectrum in e.map(download, spectra):
      temperature = float(temperature_parser(spectrum))
      add_spectrum(analogue.id, spectrum, temperature)
  db.session.commit()


# Fetch remote data
def fetch():
  "Fetches old database files from Leiden network"
  user_id = db.session.query(User).first().get_id()
  t_start = time.time()

  page = 'https://www.strw.leidenuniv.nl/lab/databases/databases%202007.htm'
  base = 'https://www.strw.leidenuniv.nl/lab/databases/'
  print('Downloading', page)
  with urlopen(page) as f:
    html = f.read()
    soup = BeautifulSoup(html)

    for a in soup.find_all('a'):
      link = a.get('href')
      if '.pdf' not in link:
        print('->', link)
        fetch_database(base + link)
        
  print('Fetching process took %.2f seconds' % (time.time()-t_start))


def fetch_database(page):
  "Fetches a single part of the database"
  with urlopen(page) as f:
    html = f.read()
    soup = BeautifulSoup(html)

    for a in soup.find_all('a'):
      link = a.get('href')
      if '.pdf' in link.lower()
        continue
