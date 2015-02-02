from application import app, db
from flask import render_template, jsonify, send_file, request
import io
import tarfile, gzip
import numpy

from application.models import Analogue, Spectrum
from sqlalchemy import or_, and_


@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page):
  searchword = request.args.get('q')
  if searchword:
    analogues = Analogue.query.filter(
      and_(Analogue.name.like('%' + word + '%') for word in searchword.split()))
    #analogues = Analogue.query.filter(Analogue.name.like('%' + searchword + '%'))
  else:
    analogues = Analogue.query
  analogues = analogues.paginate(page, app.config['ANALOGUES_PER_PAGE'], True)

  stats = {
    'analogues_count': Analogue.query.count(),
    'spectra_count': Spectrum.query.count()
  }
  return render_template('index.jade', analogues=analogues, stats=stats, q=searchword)


@app.route('/data/<int:analogue_id>', methods=['GET'])
def analogue_show(analogue_id):
  analogue = Analogue.query.get(analogue_id)
  temperatures = sorted([s.temperature for s in analogue.spectra])
  t = [str(t) for t in temperatures]
  spectra = db.session.query(Spectrum).filter_by(analogue_id=analogue.id).order_by(Spectrum.temperature)

  return render_template(
    'show.jade',
    analogue=analogue,
    spectra=spectra)


def split(arr, cond):
  return [arr[cond], arr[~cond]]

@app.route('/spectrum/<int:spectrum_id>.json', methods=['GET'])
def spectrum_show_json(spectrum_id):
  spectrum = Spectrum.query.get(spectrum_id)
  # Slice data to fewer samples to increase performance
  data = spectrum.read_h5()
  data = data[::round(len(data)/1000)]

  # Signal often starts with instrument noise (wavenumber < 500), cut that out
  parts = split(data, data[:,0] < 500)
  noise = parts[0]
  average = numpy.average(parts[1][:,1])
  maximum_distance = abs(average * 1.5)
  parts[0] = noise[abs(noise[:,1]-average) < maximum_distance]
  data = numpy.concatenate(parts)

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


@app.route('/spectrum/download/<int:analogue_id>.tar.gz', methods=['GET'])
def analogue_download_all_txt(analogue_id):
  spectra = Analogue.query.get(analogue_id).spectra
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


@app.route('/analogue/<int:analogue_id>.json', methods=['GET'])
def analogue_show_json(analogue_id):
  analogue = Analogue.query.get(analogue_id)

  # Annotate important wavenumbers
  annotations = {}
  #if '{H2O}' in analogue.name:
  #  annotations['H2O stretch'] =   3250 # cm-1
  #  annotations['H2O bending'] =   1700
  #  annotations['H2O libration'] = 770

  #if '{HCOOH}' in analogue.name:
  #  annotations['C=O stretch'] =   1714

  return jsonify(
    spectra=sorted([s.id for s in analogue.spectra]),
    annotations=annotations)
