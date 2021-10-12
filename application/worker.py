from application import data_path, db
from application.models import Spectrum
from application.models import N_optc
from application.models import SC_spec
from sqlalchemy.event import listens_for

import os, time, gzip, h5py, warnings
from concurrent.futures import ThreadPoolExecutor as Pool

import os.path as op
import numpy as np

#"""
@listens_for(Spectrum, 'after_insert')
@listens_for(Spectrum, 'after_update')
def process_data(mapper, connection, target):
  t_start = time.time()
  #print("Processing spectrum #%s" % target.id)
  print("PROCESSING SPECTRUM #%s" % target.id)

  # GZip raw original data
  if target.gzipped() == False:
    with open(target.ungz_file_path(), 'r') as f_in:
      with gzip.open(target.gz_file_path(), 'wt') as f_out:
        f_out.writelines([process_line(line) for line in enumerate(f_in)])

    # Remove original TXT file
    os.remove(target.ungz_file_path())

  data = np.genfromtxt(target.gz_file_path(), delimiter=' ') # this takes 0.1 seconds

  generate_hpf5(target, data)
  detect_wavenumber_resolution(target, data)

  # print('Processing time was %.2f seconds' % (time.time()-t_start))


def generate_hpf5(target, data):
  print("GENERATING HPF5")
  data_folder = target.data_folder()
  os.makedirs(data_folder, exist_ok=True)

  h5 = h5py.File(target.h5_file_path(), 'w')

  dset = h5.create_dataset('spectrum', data.shape, dtype='float64', compression='lzf')
  dset[...] = data
  # dset.attrs['temperature'] = target.temperature
  h5.close()


def detect_wavenumber_resolution(target, data):
  print("DETECTING WAVENUMBER RESOLUTION SPEC")
  x = data[:,0]
  #resolution = np.average(np.diff(x))
  #resolution = 00
  #print("Resolution is:", resolution)
  wavenumber_range = "%d - %d" % (round(np.amin(x)), round(np.amax(x)))
  #db.session.query(Spectrum).filter_by(id=target.id).update({'resolution': resolution, 'wavenumber_range': wavenumber_range})
  db.session.query(Spectrum).filter_by(id=target.id).update({'wavenumber_range': wavenumber_range})
  #"""



#"""
###N-Val Will 26/04/2021

@listens_for(N_optc, 'after_insert')
@listens_for(N_optc, 'after_update')
def n_process_data(mapper, connection, target):
  t_start = time.time()
  print("Processing optical constant #%s" % target.id)

  # GZip raw original data
  if target.n_gzipped() == False:
    with open(target.n_ungz_file_path(), 'r') as f_in:
      with gzip.open(target.n_gz_file_path(), 'wt') as f_out:
        f_out.writelines([process_line(line) for line in enumerate(f_in)])

    # Remove original TXT file
    os.remove(target.n_ungz_file_path())

  data = np.genfromtxt(target.n_gz_file_path(), delimiter=' ') # this takes 0.1 seconds

  n_generate_hpf5(target, data)
  n_detect_wavenumber_resolution(target, data)

  # print('Processing time was %.2f seconds' % (time.time()-t_start))


def n_generate_hpf5(target, data):
  data_folder = target.n_data_folder()
  os.makedirs(data_folder, exist_ok=True)

  h5 = h5py.File(target.n_h5_file_path(), 'w')

  dset = h5.create_dataset('spectrum_nval', data.shape, dtype='float64', compression='lzf')
  dset[...] = data
  # dset.attrs['temperature'] = target.temperature
  h5.close()


def n_detect_wavenumber_resolution(target, data):
  print('DATA SHAPE IS:', data.shape)
  x = data[: , 0]
  print('X VALUE IS:', x)
  resolution = np.average(np.diff(x))
  wavenumber_range = "%d - %d" % (round(np.amin(x)), round(np.amax(x)))
  db.session.query(N_optc).filter_by(id=target.id).update({'resolution': resolution, 'wavenumber_range': wavenumber_range})
########
#"""


@listens_for(SC_spec, 'after_insert')
@listens_for(SC_spec, 'after_update')
def sc_process_data(mapper, connection, target):
  t_start = time.time()
  print("Processing optical constant #%s" % target.id)

  # GZip raw original data
  if target.sc_gzipped() == False:
    with open(target.sc_ungz_file_path(), 'r') as f_in:
      with gzip.open(target.sc_gz_file_path(), 'wt') as f_out:
        f_out.writelines([process_line(line) for line in enumerate(f_in)])

    # Remove original TXT file
    os.remove(target.sc_ungz_file_path())

  data = np.genfromtxt(target.sc_gz_file_path(), delimiter=' ') # this takes 0.1 seconds

  sc_generate_hpf5(target, data)
  sc_detect_wavenumber_resolution(target, data)

  # print('Processing time was %.2f seconds' % (time.time()-t_start))


def sc_generate_hpf5(target, data):
  data_folder = target.sc_data_folder()
  os.makedirs(data_folder, exist_ok=True)

  h5 = h5py.File(target.sc_h5_file_path(), 'w')

  dset = h5.create_dataset('spectrum_cont', data.shape, dtype='float64', compression='lzf')
  dset[...] = data
  # dset.attrs['temperature'] = target.temperature
  h5.close()


def sc_detect_wavenumber_resolution(target, data):
  print('DATA SHAPE IS:', data.shape)
  x = data[: , 0]
  print('X VALUE IS:', x)
  resolution = np.average(np.diff(x))
  wavenumber_range = "%d - %d" % (round(np.amin(x)), round(np.amax(x)))
  db.session.query(SC_spec).filter_by(id=target.id).update({'resolution': resolution, 'wavenumber_range': wavenumber_range})
########
#"""


def process_line(line):
  i, line = line
  normalized_line = ' '.join(line.split()).replace(', ', ' ')
  # Python can't cast comma floats, so turn into dots
  if ',' in normalized_line:
    if '.' not in normalized_line:
      # Comma was used as a dot
      normalized_line = normalized_line.replace(',', '.')
    else:
      # Comma was probably used to seperate thousands
      normalized_line = normalized_line.replace(',', '')
      
  if normalized_line[0] in ['#', 'A']:
    warnings.warn('Skipping line: %s' % normalized_line)
  else:
    # Test if line consists of X Y components
    if len(normalized_line.split()) == 2:
      if i == 0 and normalized_line.split()[1] == '0':
        warnings.warn('Skipping first line, zero point: %s' % normalized_line)
      else:
        return(normalized_line + '\n')
    else:
      warnings.warn('Missing X Y components in line: %s' % normalized_line)
  return ''
