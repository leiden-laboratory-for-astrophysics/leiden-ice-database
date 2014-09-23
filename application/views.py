from application import app, db
from flask import render_template, jsonify, send_file
import io, os
import tarfile, gzip

from application.models import Mixture, Spectrum

@app.route('/')
def index():
  mixtures = Mixture.query.all()
  return render_template('index.jade', mixtures=mixtures)

@app.route('/data/<int:mixture_id>', methods=['GET'])
def mixture_show(mixture_id):
  mixture = Mixture.query.get(mixture_id)
  temperatures = sorted([s.temperature for s in mixture.spectra])
  t = [str(t) for t in temperatures]
  spectra = db.session.query(Spectrum).filter_by(mixture_id=mixture.id).order_by(Spectrum.temperature)

  return render_template('show.jade', mixture=mixture, temperatures=t, spectra=spectra)

@app.route('/spectrum/<int:spectrum_id>.json', methods=['GET'])
def spectrum_show_json(spectrum_id):
  spectrum = Spectrum.query.get(spectrum_id)
  # Slice data to ::8 (only show 1 in 8 samples) to increase performance
  data = spectrum.read_h5()[::8]
  return jsonify(temperature=spectrum.temperature, data=data.tolist())

@app.route('/spectrum/download/<int:spectrum_id>/<string:download_filename>.txt.gz', methods=['GET'])
def spectrum_download_gz(spectrum_id, download_filename):
  spectrum = Spectrum.query.get(spectrum_id)
  return send_file(spectrum.gz_file_path(), mimetype='application/x-gzip')

@app.route('/spectrum/download/<int:spectrum_id>/<string:download_filename>.txt', methods=['GET'])
def spectrum_download_txt(spectrum_id, download_filename):
  spectrum = Spectrum.query.get(spectrum_id)
  with gzip.open(spectrum.gz_file_path(), 'r') as f:
    data = f.read()
  mimetype = 'text/plain'
  rv = app.response_class(data, mimetype=mimetype, direct_passthrough=True)
  return rv

@app.route('/spectrum/download/<int:mixture_id>.tar.gz', methods=['GET'])
def mixture_download_all_txt(mixture_id):
  spectra = Mixture.query.get(mixture_id).spectra
  stream = io.BytesIO()
  with tarfile.open(mode='w:gz', fileobj=stream) as tar:
    for spectrum in spectra:
      with gzip.open(spectrum.gz_file_path(), 'r') as f:
        buff = f.read()
        tarinfo = tarfile.TarInfo(name=str(spectrum.temperature)+'K.txt')
        tarinfo.size = len(buff)
        tar.addfile(tarinfo=tarinfo, fileobj=io.BytesIO(buff))
  data = stream.getvalue()
  mimetype = 'application/x-tar'
  rv = app.response_class(data, mimetype=mimetype, direct_passthrough=True)
  return rv


@app.route('/mixture/<int:mixture_id>.json', methods=['GET'])
def mixture_show_json(mixture_id):
  mixture = Mixture.query.get(mixture_id)
  return jsonify(spectra=[s.id for s in mixture.spectra])
