from application import db, data_path
from application.models import *
from urllib.request import urlopen

import os.path as op
import hashlib
from shutil import copyfile
import time

# Normalize X Y data files
def write_data(f_in, target_file):
  with open(target_file, 'wt') as f_out:
    for line in f_in.readlines():
      normalized_line = ' '.join(line.decode('utf-8').strip().split())
      # Test if line consists of X Y components
      if len(normalized_line.split()) == 2:
        f_out.write(normalized_line + '\n')
      else:
        print('WARNING\t Skipping line with missing X Y components: %s' % normalized_line)


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

def add_spectra(mixture, spectra, temperature_parser):
  for spectrum in spectra:
    filename = download(spectrum)
    temperature = int(temperature_parser(spectrum))
    db.session.add(Spectrum(
      mixture_id=mixture.id,
      path=filename,
      temperature=temperature
    ))
  print('Committing %s spectra by %s' % (mixture.name, mixture.author))
  db.session.commit()

def fetch():
  "Fetches old database files from Leiden network"
  user_id = db.session.query(User).first().get_id()
  t_start = time.time()

  # HCOOH by Suzanne Bisschop
  # http://www.strw.leidenuniv.nl/lab/databases/hcooh/index.html
  mixture = Mixture(
    user_id=user_id,
    name='Pure $\ce{HCOOH}$',
    description='Deposited at 15K. Note that in the raw data the wavenumber range around 7-7.5 micron is not corrected for instrumental effects and is therefore difficult to use. In case spectra of this frequency range are required please contact Suzanne Bisschop directly (bisschop at strw dot leidenuniv dot nl).',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_105K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_120K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_135K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_150K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_15K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_165.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_30K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_60K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_75K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_90K.dat']

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

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_120K_d145K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_135K_d145K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_145K_d145K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_150K_d145K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_15K_d145K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_165K_d145K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_30K_d145K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_45K_d145K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_60K_d145K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_75K_d145K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh100_90K_d145K.dat']

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

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_15K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_30K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_45K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_60K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_75K.dat',
    # TODO: Check 90K spectrum, it's a flat line - mistake?
    #'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_90K.dat'
  ] 

  def temperature(url):
    return url.split('ch3oh90_')[1].split('K.dat')[0]

  add_spectra(mixture, spectra, temperature)


  # HCOOH 11% + CO 89% by Suzanne Bisschop
  mixture = Mixture(
    user_id=user_id,
    name='$\ce{HCOOH}$ 11% + $\ce{CO}$ 89%',
    description='',
    author='Suzanne Bisschop',
    DOI='10.1051/0004-6361:20077464'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh11+co89_105K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh11+co89_135K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh11+co89_15K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh11+co89_165K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh11+co89_45K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh11+co89_75K.dat']

  def temperature(url):
    return url.split('co89_')[1].split('K.dat')[0]

  add_spectra(mixture, spectra, temperature)


  # Pure H2O (10000 L) by Oberg et al. 2006
  mixture = Mixture(
    user_id=user_id,
    name='Pure $\ce{H2O}$ (10000 L)',
    description='Total thickness 10000 L',
    author='Öberg et al',
    DOI='10.1051/0004-6361:20065881'
  )
  db.session.add(mixture)
  db.session.commit()
  
  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_10000L/h2o_pure_10000l_15k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_10000L/h2o_pure_10000l_45k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_10000L/h2o_pure_10000l_75k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_10000L/h2o_pure_10000l_105k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_10000L/h2o_pure_10000l_135k.asc'] 

  def temperature(url):
    return url.split('pure_10000l_')[1].split('k.asc')[0]

  add_spectra(mixture, spectra, temperature)


  # Pure C 18O2 (10000 L) by Oberg et al. 2006
  mixture = Mixture(
    user_id=user_id,
    name='Pure $\ce{C{^{18}O2}}$ (10000 L)',
    description='Total thickness 10000 L',
    author='Öberg et al',
    DOI='10.1051/0004-6361:20065881'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/C18O2_PURE_10000L/c18o2_pure_10000l_15k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/C18O2_PURE_10000L/c18o2_pure_10000l_45k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/C18O2_PURE_10000L/c18o2_pure_10000l_75k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/C18O2_PURE_10000L/c18o2_pure_10000l_105k.asc']

  add_spectra(mixture, spectra, temperature)


  # Pure H2O (3000 L) by Oberg et al. 2006
  mixture = Mixture(
    user_id=user_id,
    name='Pure $\ce{H2O}$ (3000 L)',
    description='Total thickness 3000 L',
    author='Öberg et al',
    DOI='10.1051/0004-6361:20065881'
  )
  db.session.add(mixture)
  db.session.commit()
  
  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_3000L/h2o_pure_3000l_15k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_3000L/h2o_pure_3000l_45k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_3000L/h2o_pure_3000l_75k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_3000L/h2o_pure_3000l_105k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_PURE_3000L/h2o_pure_3000l_135k.asc'] 

  def temperature(url):
    return url.split('pure_3000l_')[1].split('k.asc')[0]

  add_spectra(mixture, spectra, temperature)


  # Pure C 18O2 (3000 L) by Oberg et al. 2006
  mixture = Mixture(
    user_id=user_id,
    name='Pure $\ce{C{^{18}O2}}$ (3000 L)',
    description='Total thickness 3000 L',
    author='Öberg et al',
    DOI='10.1051/0004-6361:20065881'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/C18O2_PURE_3000L/c18o2_pure_3000l_15k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/C18O2_PURE_3000L/c18o2_pure_3000l_45k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/C18O2_PURE_3000L/c18o2_pure_3000l_75k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/C18O2_PURE_3000L/c18o2_pure_3000l_105k.asc']

  add_spectra(mixture, spectra, temperature)


  # H2O 18O2 1:1 (20000 L) by Oberg et at al. 2006
  mixture = Mixture(
    user_id = user_id,
    name='$\ce{H2O}$:$\ce{C{^{18}O2}}$ 1:1 (20000 L)',
    description='Total thickness 20000 L',
    author='Öberg et al',
    DOI='10.1051/0004-6361:20065881'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_1_20000L/h2o_c18o2_1_1_20000l_15k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_1_20000L/h2o_c18o2_1_1_20000l_30k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_1_20000L/h2o_c18o2_1_1_20000l_45k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_1_20000L/h2o_c18o2_1_1_20000l_75k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_1_20000L/h2o_c18o2_1_1_20000l_105k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_1_20000L/h2o_c18o2_1_1_20000l_135k.asc']

  def temperature(url):
    return url.split('1_20000l_')[1].split('k.asc')[0]

  add_spectra(mixture, spectra, temperature)


  # H2O 18O2 1:2 (30000 L) by Oberg et at al. 2006
  mixture = Mixture(
    user_id = user_id,
    name='$\ce{H2O}$:$\ce{C{^{18}O2}}$ 1:2 (30000 L)',
    description='Total thickness 30000 L',
    author='Öberg et al',
    DOI='10.1051/0004-6361:20065881'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_2_30000L/h2o_c18o2_1_2_30000l_15k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_2_30000L/h2o_c18o2_1_2_30000l_30k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_2_30000L/h2o_c18o2_1_2_30000l_45k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_2_30000L/h2o_c18o2_1_2_30000l_75k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_2_30000L/h2o_c18o2_1_2_30000l_105k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_2_30000L/h2o_c18o2_1_2_30000l_135k.asc']

  def temperature(url):
    return url.split('2_30000l_')[1].split('k.asc')[0]

  add_spectra(mixture, spectra, temperature)


  # H2O 18O2 2:1 (15000 L) by Oberg et at al. 2006
  mixture = Mixture(
    user_id = user_id,
    name='$\ce{H2O}$:$\ce{C{^{18}O2}}$ 2:1 (15000 L)',
    description='Total thickness 15000 L',
    author='Öberg et al',
    DOI='10.1051/0004-6361:20065881'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_2_1_15000L/h2o_c18o2_2_1_15000l_15k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_2_1_15000L/h2o_c18o2_2_1_15000l_45k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_2_1_15000L/h2o_c18o2_2_1_15000l_75k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_2_1_15000L/h2o_c18o2_2_1_15000l_105k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_2_1_15000L/h2o_c18o2_2_1_15000l_135k.asc']

  def temperature(url):
    return url.split('1_15000l_')[1].split('k.asc')[0]

  add_spectra(mixture, spectra, temperature)


  # H2O 18O2 2:1 (4500 L) by Oberg et at al. 2006
  mixture = Mixture(
    user_id = user_id,
    name='$\ce{H2O}$:$\ce{C{^{18}O2}}$ 2:1 (4500 L)',
    description='Total thickness 4500 L',
    author='Öberg et al',
    DOI='10.1051/0004-6361:20065881'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_2_1_4500L/h2o_c18o2_2_1_4500l_15k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_2_1_4500L/h2o_c18o2_2_1_4500l_45k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_2_1_4500L/h2o_c18o2_2_1_4500l_75k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_2_1_4500L/h2o_c18o2_2_1_4500l_105k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_2_1_4500L/h2o_c18o2_2_1_4500l_135k.asc']

  def temperature(url):
    return url.split('1_4500l_')[1].split('k.asc')[0]

  add_spectra(mixture, spectra, temperature)


  # H2O 18O2 1:1 (6000 L) by Oberg et at al. 2006
  mixture = Mixture(
    user_id = user_id,
    name='$\ce{H2O}$:$\ce{C{^{18}O2}}$ 1:1 (6000 L)',
    description='Total thickness 6000 L',
    author='Öberg et al',
    DOI='10.1051/0004-6361:20065881'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_1_6000L/h2o_c18o2_1_1_6000l_15k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_1_6000L/h2o_c18o2_1_1_6000l_45k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_1_6000L/h2o_c18o2_1_1_6000l_75k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_1_6000L/h2o_c18o2_1_1_6000l_105k.asc',
    'http://www.strw.leidenuniv.nl/lab/databases/h2o_co2_ices/H2O_C18O2_1_1_6000L/h2o_c18o2_1_1_6000l_135k.asc']

  def temperature(url):
    return url.split('1_6000l_')[1].split('k.asc')[0]

  add_spectra(mixture, spectra, temperature)


  print('Fetching process took %.2f seconds' % (time.time()-t_start))
