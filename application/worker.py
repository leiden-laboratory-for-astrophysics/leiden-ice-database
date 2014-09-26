from application import data_path
from application.models import Spectrum
from sqlalchemy.event import listens_for

import os, time, gzip, h5py

import os.path as op
import numpy as np

@listens_for(Spectrum, 'after_insert')
@listens_for(Spectrum, 'after_update')
def process_data(mapper, connection, target):
  # GZip raw original data
  if target.gzipped() == False:
    with open(target.ungz_file_path(), 'rb') as f_in:
      with gzip.open(target.gz_file_path(), 'wb') as f_out:
        f_out.writelines(f_in)
    os.remove(target.ungz_file_path())

  t_start = time.time()
  print("Processing spectrum #%s" % target.id)

  # Generate HPF5
  data = np.genfromtxt(target.gz_file_path())
  data_folder = target.data_folder()
  print("Saving spectrum data to", data_folder)
  os.makedirs(data_folder, exist_ok=True)

  t = time.time()
  h5 = h5py.File(target.h5_file_path(), 'w')

  dset = h5.create_dataset('spectrum', data.shape, dtype='float64', compression='lzf')
  dset[...] = data
  dset.attrs['temperature'] = target.temperature
  h5.close()

  print('+ Converted to HPF5 in %.2f seconds' % (time.time()-t))
  print('Overall processing time was %.2f seconds' % (time.time()-t_start))
