from application import db, data_path
from application.models import *
from urllib.request import urlopen

# HTML parser
from bs4 import BeautifulSoup
import re

import os.path as op
import hashlib
from shutil import copyfile
import time

# Normalize X Y data files
def write_data(f_in, target_file):
  with open(target_file, 'wt') as f_out:
    for i, line in enumerate(f_in.readlines()):
      normalized_line = ' '.join(line.decode('utf-8').strip().split())
      # Test if line consists of X Y components
      if len(normalized_line.split()) == 2:
        if i == 0 and normalized_line.split()[1] == '0':
          print('WARNING\t Skipping first line, zero point:', normalized_line)
          continue
        f_out.write(normalized_line + '\n')
      else:
        print('WARNING\t Skipping line with missing X Y components:', normalized_line)


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
    with open(cached_file, 'rb') as f_cache:
      write_data(f_cache, target_file)
  else:
    # Download file
    print('Downloading %s' % url)
    with urlopen(url) as f_in:
      write_data(f_in, target_file)
    copyfile(target_file, cached_file)

  return filename


# Add single spectrum
def add_spectrum(mixture, spectrum, temperature):
  filename = download(spectrum)

  db.session.add(Spectrum(
    mixture_id=mixture.id,
    path=filename,
    temperature=temperature
  ))


# Add spectra to mixture
def add_spectra(mixture, spectra, temperature_parser):
  for spectrum in spectra:
    temperature = int(temperature_parser(spectrum))
    add_spectrum(mixture, spectrum, temperature)

  print('Committing %s spectra by %s' % (mixture.name, mixture.author))
  db.session.commit()

# Fetch remote data
def fetch():
  "Fetches old database files from Leiden network"
  user_id = db.session.query(User).first().get_id()
  t_start = time.time()

  # HCOOH by Suzanne Bisschop
  # http://www.strw.leidenuniv.nl/lab/databases/hcooh/index.html
  mixture = Mixture(
    user_id=user_id,
    name='Pure $\ce{HCOOH}$',
    description='Deposited at 15K. Note that in the raw data the wavenumber range around 7-7.5 micron is not corrected for instrumental effects and is therefore difficult to use.',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = []
  for T in [15, 30, 60, 75, 90, 105, 120, 135, 150, 165]:
    if T == 165:
      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_' + str(T) + '.dat')
    else:
      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_' + str(T) + 'K.dat')

  def temperature(url):
    return url.split('hcooh100_')[1].split('.dat')[0].replace('K', '')

  add_spectra(mixture, spectra, temperature)


  # HCOOH deposited at 145 K and warmed up by Suzanne Bisschop
  mixture = Mixture(
    user_id=user_id,
    name='Pure $\ce{HCOOH}$ deposited at 145 K',
    description='Ice deposited at 145 K, cooled down to 15 K and subsequently warmed up.',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = []
  for T in [15, 30, 45, 60, 75, 90, 120, 135, 145, 150, 165]:
    spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_' + str(T) + 'K_d145K.dat')

  def temperature(url):
    return url.split('hcooh100_')[1].split('K_d')[0]

  add_spectra(mixture, spectra, temperature)


  # HCOOH 10% + CH3OH 90% by Suzanne Bisschop
  mixture = Mixture(
    user_id=user_id,
    name='$\ce{HCOOH}$ 10% + $\ce{CH3OH}$ 90%',
    description='Note that in the raw data the wavenumber range around 7-7.5 micron is not corrected for instrumental effects and is therefore difficult to use. In case spectra of this frequency range are required please contact Suzanne Bisschop directly (bisschop at strw dot leidenuniv dot nl).',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = []
  for T in [15, 30, 45, 60, 75]:
    spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_' + str(T) + 'K.dat')
    # TODO: Check 90K spectrum, it's a flat line - mistake?
    #'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_90K.dat'

  def temperature(url):
    return url.split('ch3oh90_')[1].split('K.dat')[0]

  add_spectra(mixture, spectra, temperature)


  # HCOOH 11% + CO 89% by Suzanne Bisschop
  mixture = Mixture(
    user_id=user_id,
    name='$\ce{HCOOH}$ 11% + $\ce{CO}$ 89%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = []
  for T in [15, 45, 75, 105, 135, 165]:
    spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh11+co89_' + str(T) + 'K.dat')

  def temperature(url):
    return url.split('co89_')[1].split('K.dat')[0]

  add_spectra(mixture, spectra, temperature)

  
  # HCOOH A% + H2O B% by Suzanne Bisschop
  for ratios in ['20:80', '34:66', '50:50']:
    a = ratios.split(':')[0]
    b = ratios.split(':')[1]

    mixture = Mixture(
      user_id = user_id,
      name = '$\ce{HCOOH}$ '+a+'% + $\ce{H2O}$ '+b+'%',
      author='Suzanne Bisschop',
      DOI='10.1051/0004-6361:20077464'
    )
    db.session.add(mixture)
    db.session.commit()

    spectra = []
    for T in [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]:
      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh'+a+'+h2o'+b+'_'+str(T)+'K.dat')

    def temperature(url):
      return url.split('h2o'+b+'_')[1].split('K.dat')[0]

    add_spectra(mixture, spectra, temperature)


  # HCOOH 6% + H2O 67% + CO2 27% by Suzanne Bisschop
  mixture = Mixture(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 6% + $\ce{H2O}$ 67% + $\ce{CO2}$ 27%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = ['http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh6+h2o67+co2_27_15K.dat']

  def temperature(url):
    return url.split('co2_27_')[1].split('K.dat')[0]

  add_spectra(mixture, spectra, temperature)


  # HCOOH 6% + H2O 68% + CH3OH 26% by Suzanne Bisschop
  mixture = Mixture(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 6% + $\ce{H2O}$ 68% + $\ce{CH3OH}$ 26%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = ['http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh6+h2o68+ch3oh26_15K.dat']

  def temperature(url):
    return url.split('ch3oh26_')[1].split('K.dat')[0]

  add_spectra(mixture, spectra, temperature)


  # HCOOH 8% + H2O 62% + CO 30% by Suzanne Bisschop
  mixture = Mixture(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 8% + $\ce{H2O}$ 62% + $\ce{CO}$ 30%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = ['http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh8+h2o62+co30_15K.dat']

  def temperature(url):
    return url.split('co30_')[1].split('K.dat')[0]

  add_spectra(mixture, spectra, temperature)


  # HCOOH 9% + CO2 91% by Suzanne Bisschop
  mixture = Mixture(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 9% + $\ce{CO2}$ 91%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = []
  for T in [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]:
    spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh9_co2_91_'+str(T)+'K.dat')

  def temperature(url):
    return url.split('co2_91_')[1].split('K.dat')[0]

  add_spectra(mixture, spectra, temperature)


  # HCOOH 9% + H2O 91% by Suzanne Bisschop
  mixture = Mixture(
    user_id = user_id,
    name = '$\ce{HCOOH}$ 9% + $\ce{H2O}$ 91%',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = []
  for T in [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165]:
    spectra.append('http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh9+h2o91_'+str(T)+'K.dat')

  def temperature(url):
    return url.split('h2o91_')[1].split('K.dat')[0]

  add_spectra(mixture, spectra, temperature)


  # Pure H2O (thickness L) by Oberg et al. 2006
  for thickness in ['10000', '3000']:
    mixture = Mixture(
      user_id=user_id,
      name='Pure $\ce{H2O}$ (' + thickness + ' L)',
      description='Total thickness ' + thickness + ' L',
      author='Öberg et al',
      DOI='10.1051/0004-6361:20065881'
    )
    db.session.add(mixture)
    db.session.commit()
  
    spectra = []
    for T in [15, 45, 75, 105, 135]:
      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_' + thickness + 'L/h2o_pure_' + thickness + 'l_'+str(T)+'k.asc')

    def temperature(url):
      return url.split('pure_' + thickness + 'l_')[1].split('k.asc')[0]

    add_spectra(mixture, spectra, temperature)


  # Pure C 18O2 (xxxxx L) by Oberg et al. 2006
  for thickness in ['10000', '3000']:
    mixture = Mixture(
      user_id=user_id,
      name='Pure $\ce{C{^{18}O2}}$ (' + thickness + ' L)',
      description='Total thickness ' + thickness + ' L',
      author='Öberg et al',
      DOI='10.1051/0004-6361:20065881'
    )
    db.session.add(mixture)
    db.session.commit()

    spectra = []
    for T in [15, 45, 75, 105]:
      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/C18O2_PURE_' + thickness + 'L/c18o2_pure_' + thickness + 'l_'+str(T)+'k.asc')

    def temperature(url):
      return url.split('pure_' + thickness + 'l_')[1].split('k.asc')[0]

    add_spectra(mixture, spectra, temperature)


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

    mixture = Mixture(
      user_id = user_id,
      name='$\ce{H2O}$:$\ce{C{^{18}O2}}$ ' + a + ':' + b + ' (' + attributes['thickness'] + ' L)',
      description='Total thickness ' + attributes['thickness'] + ' L',
      author='Öberg et al',
      DOI='10.1051/0004-6361:20065881'
    )
    db.session.add(mixture)
    db.session.commit()
    
    spectra = []
    for T in [15, 30, 45, 75, 105, 135]:
      if T == 30 and '30k' not in attributes:
        continue

      spectra.append('http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_'+a+'_'+b+'_'+attributes['thickness']+'L/h2o_c18o2_'+a+'_'+b+'_'+attributes['thickness']+'l_'+str(T)+'k.asc')

    def temperature(url):
      return url.split(b+'_'+attributes['thickness']+'l_')[1].split('k.asc')[0]

    add_spectra(mixture, spectra, temperature)

  # Pascale Ehrenfreund & Stephan Schlemmer
  # This database contains 325 infrared spectra of thermally processed H2O-CH3OH-CO2 ice mixtures in the wavelength range 6000-400 cm-1.
  # It's faster to parse the single page featuring the spectra
  page = 'http://www.strw.leidenuniv.nl/lab/databases/iso_www3/index.html'
  mixtures = []
  mixture = None

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

      # TODO: Float temperature values not supported
      # There's one spectrum at 117.5 K
      if '.' in temperature:
        continue

      if spectrum in ['CROSS22W1', 'CROSS22W2', 'CROSS22W3']:
        # These spectra are not available (404 error)
        continue

      print('Detected', spectrum, composition, temperature, 'K')

      if composition not in mixtures:
        # Add new mixture to database
        # Wrap composition molecules in LateX \ce{}
        molecules, weights = composition.split('=')
        molecules = molecules.split(':')
        molecules = '$\ce{{{}}}$'.format('}$:$\ce{'.join(molecules))
        mixture_name = molecules + ' ' + weights
        print('Adding new mixture:', mixture_name)

        mixture = Mixture(
          user_id = user_id,
          name = mixture_name,
          author = 'Pascale Ehrenfreund and Stephan Schlemmer',
          DOI = ''
        )
        mixtures.append(composition)
        db.session.add(mixture)
        db.session.commit()


      absolute_url = 'http://www.strw.leidenuniv.nl/lab/databases/iso_www3/' + spectrum
      add_spectrum(mixture, absolute_url, int(temperature))
    
    db.session.commit()


  print('Fetching process took %.2f seconds' % (time.time()-t_start))
