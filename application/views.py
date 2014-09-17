from application import app, db
from flask import render_template

from application.models import Mixture, Spectrum

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpld3
import numpy as np

@app.route('/')
def index():
  return render_template('index.jade')

@app.route('/data/<int:mixture_id>', methods=['GET'])
def mixture_show(mixture_id):
  mixture = Mixture.query.get(mixture_id)
  return render_template('show.jade', mixture=mixture)

@app.route('/spectrum/<int:spectrum_id>', methods=['GET'])
def spectrum_show(spectrum_id):
#  experiment = get_object_or_404(Experiment, Experiment.id==experiment_id)
  spectrum = Spectrum.query.get(spectrum_id)
  data = np.genfromtxt(spectrum.gz_file_path())
  (x, y) = (data[:,0], data[:,1])
  fig, ax = plt.subplots()
  ax.plot(x, y, 'k-')

  ax.set_xlabel(r'Wavenumber $\rm cm^{-1}$')
  ax.set_ylabel('Absorbance')

  ax.invert_xaxis()
  plt.ylim(-0.05, plt.ylim()[1])

  
  plt.title(
    "%s at %s K" % (spectrum.mixture.name.replace('$', '\$'), spectrum.temperature)
  )
  mpld3.plugins.clear(fig)
  return mpld3.fig_to_html(fig)
