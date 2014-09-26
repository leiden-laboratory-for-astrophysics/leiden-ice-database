from application import db, data_path
from application.models import *
from urllib.request import urlopen
import os.path as op
import time

def download(url):
  filename = url.split('/')[-1]
  print('Downloading %s..' % url)
  with urlopen(url) as f_in:
    with open(op.join(data_path, filename), 'wb') as f_out:
      f_out.writelines(f_in)
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
    author_email='bisschop@strw.leidenuniv.nl'
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
    author_email='bisschop@strw.leidenuniv.nl'
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
    author_email='bisschop@strw.leidenuniv.nl'
  )
  db.session.add(mixture)
  db.session.commit()

  spectra = [
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_15K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_30K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_45K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_60K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_75K.dat',
    'http://www.strw.leidenuniv.nl/lab/databases/hcooh/hcooh10+ch3oh90_90K.dat'] 

  def temperature(url):
    return url.split('ch3oh90_')[1].split('K.dat')[0]

  add_spectra(mixture, spectra, temperature)


  # Pure H2O by Oberg et al. 2006
  mixture = Mixture(
    user_id=user_id,
    name='Pure $\ce{H2O}$',
    description='Total thickness 10000 L',
    author='Oberg et al'
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


  # HCOOH 11% + CO 89% by Suzanne Bisschop
  mixture = Mixture(
    user_id=user_id,
    name='$\ce{HCOOH}$ 11% + $\ce{CO}$ 89%',
    description='',
    author='Suzanne Bisschop',
    author_email='bisschop@strw.leidenuniv.nl'
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


  print('Fetching process took %.2f seconds' % (time.time()-t_start))
