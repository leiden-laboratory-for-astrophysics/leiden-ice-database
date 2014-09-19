from application import app, db
from flask import render_template, jsonify

from application.models import Mixture, Spectrum

@app.route('/')
def index():
  return render_template('index.jade')

@app.route('/data/<int:mixture_id>', methods=['GET'])
def mixture_show(mixture_id):
  mixture = Mixture.query.get(mixture_id)
  return render_template('show.jade', mixture=mixture)

@app.route('/spectrum/<int:spectrum_id>.json', methods=['GET'])
def spectrum_show_json(spectrum_id):
  spectrum = Spectrum.query.get(spectrum_id)
  data = spectrum.read_h5()
  return jsonify(
    temperature=spectrum.temperature,
    data=data.tolist())

@app.route('/mixture/<int:mixture_id>.json', methods=['GET'])
def mixture_show_json(mixture_id):
  mixture = Mixture.query.get(mixture_id)
  return jsonify(spectra=[m.id for m in mixture.spectra])
