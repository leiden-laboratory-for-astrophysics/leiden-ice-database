from application import data_path, db
from application.models import Spectrum
from sqlalchemy.event import listens_for

import os, time, gzip, h5py, warnings

import os.path as op
import numpy as np

@listens_for(Spectrum, 'after_insert')
@listens_for(Spectrum, 'after_update')
def process_data(mapper, connection, target):
  # t_start = time.time()
  print("Processing spectrum #%s" % target.id)

  # GZip raw original data
  if target.gzipped() == False:
    with open(target.ungz_file_path(), 'r') as f_in:
      with gzip.open(target.gz_file_path(), 'wt') as f_out:
        for i, line in enumerate(f_in):
          process_line(i, line, f_out)

    # Remove original TXT file
    os.remove(target.ungz_file_path())


  # Generate HPF5
  data = np.genfromtxt(target.gz_file_path())
  data_folder = target.data_folder()
  os.makedirs(data_folder, exist_ok=True)

  # t = time.time()
  h5 = h5py.File(target.h5_file_path(), 'w')

  dset = h5.create_dataset('spectrum', data.shape, dtype='float64', compression='lzf')
  dset[...] = data

  # Detect wavenumber resolution
  resolution = np.average(np.diff(data[:,0]))
  db.session.query(Spectrum).filter_by(id=target.id).update({'resolution': resolution})

  dset.attrs['temperature'] = target.temperature
  h5.close()

  # print('Processing time was %.2f seconds' % (time.time()-t_start))


def process_line(i, line, f_out):
  normalized_line = ' '.join(line.strip().split())
  # Test if line consists of X Y components
  if len(normalized_line.split()) == 2:
    if i == 0 and normalized_line.split()[1] == '0':
      warnings.warn('Skipping first line, zero point: %s' % normalized_line)
    else:
      f_out.write(normalized_line + '\n')
  else:
    warnings.warn('Missing X Y components in line: %s' % normalized_line)
