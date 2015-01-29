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
#from sqlalchemy.orm import scoped_session
#from sqlalchemy.orm import sessionmaker
import time

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

  # HCOOH by Suzanne Bisschop
  # http://www.strw.leidenuniv.nl/lab/databases/hcooh/index.html
  analogue = Analogue(
    user_id=user_id,
    name='Pure $\ce{HCOOH}$',
    deposition_temperature=15, # Kelvin
    description='Deposited at 15K. Note that in the raw data the wavenumber range around 7-7.5 micron is not corrected for instrumental effects and is therefore difficult to use.',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  for T in [15, 30, 60, 75, 90, 105, 120, 135, 150, 165]:
    if T == 165:
      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_' + str(T) + '.dat')
    else:
      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_' + str(T) + 'K.dat')

  def temperature(url):
    return url.split('hcooh100_')[1].split('.dat')[0].replace('K', '')

  add_spectra(analogue, spectra, temperature)


  # HCOOH deposited at 145 K and warmed up by Suzanne Bisschop
  analogue = Analogue(
    user_id=user_id,
    name='Pure $\ce{HCOOH}$ deposited at 145 K',
    deposition_temperature=145, # Kelvin
    description='Ice deposited at 145 K, cooled down to 15 K and subsequently warmed up.',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  for T in [15, 30, 45, 60, 75, 90, 120, 135, 145, 150, 165]:
    spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_' + str(T) + 'K_d145K.dat')

  def temperature(url):
    return url.split('hcooh100_')[1].split('K_d')[0]

  add_spectra(analogue, spectra, temperature)


  # HCOOH 10% + CH3OH 90% by Suzanne Bisschop
  analogue = Analogue(
    user_id=user_id,
    name='$\ce{HCOOH}$ 10% + $\ce{CH3OH}$ 90%',
    description='Note that in the raw data the wavenumber range around 7-7.5 micron is not corrected for instrumental effects and is therefore difficult to use. In case spectra of this frequency range are required please contact Suzanne Bisschop directly (bisschop at strw dot leidenuniv dot nl).',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  for T in [15, 30, 45, 60, 75]:
    spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_' + str(T) + 'K.dat')
    # TODO: Check 90K spectrum, it's a flat line - mistake?
    #'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_90K.dat'

  def temperature(url):
    return url.split('ch3oh90_')[1].split('K.dat')[0]

  add_spectra(analogue, spectra, temperature)


  # HCOOH 11% + CO 89% by Suzanne Bisschop
  analogue = Analogue(
    user_id=user_id,
    name='$\ce{HCOOH}$ 11% + $\ce{CO}$ 89%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  for T in [15, 45, 75, 105, 135, 165]:
    spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh11+co89_' + str(T) + 'K.dat')

  def temperature(url):
    return url.split('co89_')[1].split('K.dat')[0]

  add_spectra(analogue, spectra, temperature)


  # HCOOH A% + H2O B% by Suzanne Bisschop
  for ratios in ['20:80', '34:66', '50:50']:
    a = ratios.split(':')[0]
    b = ratios.split(':')[1]

    analogue = Analogue(
      user_id = user_id,
      name = '$\ce{HCOOH}$ '+a+'% + $\ce{H2O}$ '+b+'%',
      author='Suzanne Bisschop',
      DOI='10.1051/0004-6361:20077464'
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    for T in [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]:
      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh'+a+'+h2o'+b+'_'+str(T)+'K.dat')

    def temperature(url):
      return url.split('h2o'+b+'_')[1].split('K.dat')[0]

    add_spectra(analogue, spectra, temperature)


  # HCOOH 6% + H2O 67% + CO2 27% by Suzanne Bisschop
  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 6% + $\ce{H2O}$ 67% + $\ce{CO2}$ 27%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = ['http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh6+h2o67+co2_27_15K.dat']

  def temperature(url):
    return url.split('co2_27_')[1].split('K.dat')[0]

  add_spectra(analogue, spectra, temperature)


  # HCOOH 6% + H2O 68% + CH3OH 26% by Suzanne Bisschop
  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 6% + $\ce{H2O}$ 68% + $\ce{CH3OH}$ 26%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = ['http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh6+h2o68+ch3oh26_15K.dat']

  def temperature(url):
    return url.split('ch3oh26_')[1].split('K.dat')[0]

  add_spectra(analogue, spectra, temperature)


  # HCOOH 8% + H2O 62% + CO 30% by Suzanne Bisschop
  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 8% + $\ce{H2O}$ 62% + $\ce{CO}$ 30%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = ['http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh8+h2o62+co30_15K.dat']

  def temperature(url):
    return url.split('co30_')[1].split('K.dat')[0]

  add_spectra(analogue, spectra, temperature)


  # HCOOH 9% + CO2 91% by Suzanne Bisschop
  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 9% + $\ce{CO2}$ 91%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  for T in [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]:
    spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh9_co2_91_'+str(T)+'K.dat')

  def temperature(url):
    return url.split('co2_91_')[1].split('K.dat')[0]

  add_spectra(analogue, spectra, temperature)


  # HCOOH 9% + H2O 91% by Suzanne Bisschop
  analogue = Analogue(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 9% + $\ce{H2O}$ 91%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(analogue)
  db.session.commit()

  spectra = []
  for T in [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]:
    spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh9+h2o91_'+str(T)+'K.dat')

  def temperature(url):
    return url.split('h2o91_')[1].split('K.dat')[0]

  add_spectra(analogue, spectra, temperature)


  # Pure H2O (thickness L) by Oberg et al. 2006
  for thickness in ['10000', '3000']:
    analogue = Analogue(
      user_id=user_id,
      name='Pure $\ce{H2O}$ (' + thickness + ' L)',
      description='Total thickness ' + thickness + ' L',
      author='Öberg et al',
      DOI='10.1051/0004-6361:20065881'
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    for T in [15, 45, 75, 105, 135]:
      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_' + thickness + 'L/h2o_pure_' + thickness + 'l_'+str(T)+'k.asc')

    def temperature(url):
      return url.split('pure_' + thickness + 'l_')[1].split('k.asc')[0]

    add_spectra(analogue, spectra, temperature)


  # Pure C 18O2 (xxxxx L) by Oberg et al. 2006
  for thickness in ['10000', '3000']:
    analogue = Analogue(
      user_id=user_id,
      name='Pure $\ce{C{^{18}O2}}$ (' + thickness + ' L)',
      description='Total thickness ' + thickness + ' L',
      author='Öberg et al',
      DOI='10.1051/0004-6361:20065881'
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    for T in [15, 45, 75, 105]:
      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/C18O2_PURE_' + thickness + 'L/c18o2_pure_' + thickness + 'l_'+str(T)+'k.asc')

    def temperature(url):
      return url.split('pure_' + thickness + 'l_')[1].split('k.asc')[0]

    add_spectra(analogue, spectra, temperature)


  # H2O 18O2 x:x (xxxxx L thickness) by Oberg et at al. 2006
  for attributes in [
    {'ratio': '1:1', 'thickness': '20000', '30k': True},
    {'ratio': '1:2', 'thickness': '30000', '30k': True},
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
      description='Total thickness ' + attributes['thickness'] + ' L',
      author='Öberg et al',
      DOI='10.1051/0004-6361:20065881'
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    for T in [15, 30, 45, 75, 105, 135]:
      if T == 30 and '30k' not in attributes:
        # Not all analogues have 30 K spectrum
        continue

      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_'+a+'_'+b+'_'+attributes['thickness']+'L/h2o_c18o2_'+a+'_'+b+'_'+attributes['thickness']+'l_'+str(T)+'k.asc')

    def temperature(url):
      return url.split(b+'_'+attributes['thickness']+'l_')[1].split('k.asc')[0]

    add_spectra(analogue, spectra, temperature)


  # Pascale Ehrenfreund & Stephan Schlemmer
  # This database contains 325 infrared spectra of thermally processed H2O-CH3OH-CO2 ice analogues in the wavelength range 6000-400 cm-1.
  # It's faster to parse the single page featuring the spectra
  page = 'http://www.strw.leidenuniv.nl/lab/databases/iso_www3/index.html'
  analogues = []
  analogue = None

  print('Downloading Pascale Ehrenfreund & Stephan Schlemmer\'s database HTML page..')
  with urlopen(page) as f:
    html = f.read()
    soup = BeautifulSoup(html)

    for p in soup.find_all('p'):
      if not p.a:
        continue

      spectrum = p.a.get('href')
      text = re.sub(r'\s+', ' ', p.text.strip()) # normalize spaces

      if not spectrum:
        continue
      if text == '[s1]Currently not available, sorry':
        continue

      meta = text.split(' ')
      composition = meta[1]
      temperature = meta[2]

      if spectrum in ['CROSS22W1', 'CROSS22W2', 'CROSS22W3']:
        # These spectra are not available (404 error)
        continue

      print('Detected', spectrum, composition, temperature, 'K')

      if composition not in analogues:
        # Add new analogue to database
        # Wrap composition molecules in LateX \ce{}
        molecules, weights = composition.split('=')
        molecules = molecules.split(':')
        molecules = '$\ce{{{}}}$'.format('}$:$\ce{'.join(molecules))
        analogue_name = molecules + ' ' + weights
        print('Adding new analogue:', analogue_name)

        analogue = Analogue(
          user_id = user_id,
          name = analogue_name,
          author = 'Ehrenfreund and Schlemmer',
          DOI = ''
        )
        analogues.append(composition)
        db.session.add(analogue)
        db.session.commit()

      absolute_url = 'http://www.strw.leidenuniv.nl/lab/databases/iso_www3/' + spectrum
      add_spectrum(analogue.id, absolute_url, float(temperature))
    db.session.commit()


  # Fraser 2004 warm-up spectra
  for name, temperatures in {
        'CH3OH': [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100, 115, 130, 145, 160],
        'CH4': [15, 18, 20, 22.5, 25, 28, 35, 40, 50],
        'CO2': [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100],
        'CO':  [15, 18, 20, 22.5, 25, 28, 30, 35],
        'HCOOH': [14.1, 16, 19.5, 21.7, 24.5, 27.6, 29.5, 34.6, 39, 59.6, 79.8, 99.2, 160.3],
        'COmixCH3OH_1_1': [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100, 115, 130, 145, 160],
        'COmixCO2_1_1': [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100],
        'COmixHCOOH_1_1': [14.4, 17, 19.4, 22.7, 24.3, 27.1, 29.6, 34.5, 39.5, 59.3, 79.3, 99.8, 129, 160.1],
        'COoverCH3OH': [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100, 115, 130, 145, 160],
        'COoverCH4': [15, 18, 20, 22.5, 25, 28, 30, 35, 40],
        'COoverCO2': [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100],
        'COoverHCOOH': [14.3, 17.2, 19.5, 22.2, 24.5, 27.5, 29.5, 34.5, 39.1, 59.3, 79.2, 99.4, 129.5, 159.5],
        'COunderCH3OH': [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100, 115, 130, 145, 160],
        'COunderCH4': [15, 18, 20, 22.5, 25, 28, 30, 35, 40],
        'COunderCO2': [15, 18, 20, 22.5, 25, 28, 30, 35, 40, 50, 60, 70, 80, 90, 100],
        'COunderHCOOH': [14.5, 17.7, 19.8, 22.3, 24.5, 27.2, 29.5, 34.6, 39.3, 59.6, 79.2, 99.3, 128.8, 159.2]
        }.items():

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
      description='',
      author='Fraser',
      DOI='10.1016/j.asr.2003.04.003'
    )
    db.session.add(analogue)
    db.session.commit()

    spectra = []
    for T in temperatures:
      spectra.append('http://www.strw.leidenuniv.nl/astrochem/co_laboratory_spectra_database/Warm-Up_Spectra/'+name+'_'+str(T)+'K.DAT')

    def temperature(url):
      return url.split(name+'_')[1].split('K.DAT')[0]

    add_spectra(analogue, spectra, temperature)


  # Mixed/layered ices by ??? TODO: Find out who measured these
  # http://www.strw.leidenuniv.nl/lab/databases/mixed_layered_co_co2/index.html
  page = 'http://www.strw.leidenuniv.nl/lab/databases/mixed_layered_co_co2/index.html'

  print('Downloading mixed/layered database HTML page..')
  with urlopen(page) as f:
    soup = BeautifulSoup(f.read())

    for a in soup.find_all('a'):
      if '/' in a.text:
        molecules = a.text.split('/')
        ratio = ':'.join(a.get('href').split('/')[1].split('_')[:2])
        analogue_name = '$\ce{' + molecules[0] + '}$ over $\ce{' + molecules[1] + '}$ ' + ratio
      elif ':' in a.text:
        molecules = a.text.split(':')
        ratio = ':'.join(a.get('href').split('/')[1].split('_'))
        analogue_name = '$\ce{' + molecules[0] + '}$:$\ce{' + molecules[1] + '}$ ' + ratio
      else:
        analogue_name = 'Pure $\ce{' + a.text + '}$'

      analogue = Analogue(
        user_id = user_id,
        name = analogue_name,
        author = 'Suzanne Bisschop',
        DOI = '',
        description = 'Thesis: Complex Molecules in the Laboratory and Star Forming Regions'
      )
      db.session.add(analogue)
      db.session.commit()

      print('Downloading spectra of', analogue_name, a.get('href'))
      analogue_url = 'http://www.strw.leidenuniv.nl/lab/databases/mixed_layered_co_co2/' + a.get('href')

      with urlopen(analogue_url) as af:
        analogue_soup = BeautifulSoup(af.read())

        for t in analogue_soup.find_all('a'):
          if t.text == 'Back':
            continue

          absolute_url = '/'.join(analogue_url.split('/')[:-1]) + '/' + t.get('href')
          if absolute_url == 'http://www.strw.leidenuniv.nl/lab/databases/mixed_layered_co_co2/layered_ices/10_1_CO2_CO/230104w03.dat':
            continue # TODO: spectrum is missing (404 error)
          if absolute_url == 'http://www.strw.leidenuniv.nl/lab/databases/mixed_layered_co_co2/layered_ices/10_1_CO2_CO/230104w09.dat':
            continue # TODO: spectrum is missing (404 error)
          if absolute_url == 'http://www.strw.leidenuniv.nl/lab/databases/mixed_layered_co_co2/layered_ices/10_1_CO2_CO/230104w13.dat':
            continue # TODO: spectrum is missing (404 error)
          add_spectrum(analogue.id, absolute_url, float(t.text))
        db.session.commit()


  print('Fetching process took %.2f seconds' % (time.time()-t_start))
