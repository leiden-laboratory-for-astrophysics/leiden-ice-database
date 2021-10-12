from bokeh.models import callbacks, layouts, renderers
from bokeh.models.tools import FreehandDrawTool
from bokeh.models.widgets import widget
from application import app, db
from flask import render_template, jsonify, send_file, request
import io
import tarfile, gzip
import numpy
import numpy as np
import h5py
import sqlite3
from bokeh.plotting import output_file, figure, show
from bokeh.models import LinearAxis,LogAxis, Range1d, LogScale, LinearScale, Text
import os
from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource, Grid, ImageURL, LinearAxis, Plot, Range1d

from flask import Flask, request, render_template, abort, Response
from bokeh.plotting import figure, curdoc
from bokeh.embed import components
from bokeh.models import ColumnDataSource, MultiLine, Div, Select, Slider, TextInput, HoverTool, CrosshairTool, Legend, LegendItem, CheckboxGroup
from bokeh.io import curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import figure, output_file, show
from bokeh.colors import RGB
from bokeh.layouts import column, row, widgetbox
from bokeh.io import output_file, show
from bokeh.layouts import layout
from bokeh.models import BoxAnnotation, Toggle
from bokeh.models.widgets import CheckboxGroup, Button, TextInput
from bokeh.models import Label, LabelSet
import math
import zipfile
import os
from flask import send_file,Flask,send_from_directory
from wtforms import SelectField
from flask_wtf import FlaskForm
from application.forms import ContactForm
import pandas as pd


from application.models import Analogue, Spectrum, N_Analogue, N_optc, SC_Object, SC_spec 
from sqlalchemy import or_, and_

@app.route('/')
#@app.route('/page/<int:page>')
def index():
  DIR = os.getcwd() + '/'
  if os.path.isdir(DIR + 'Statistics') == False:
    os.makedirs('Statistics')

  from datetime import datetime
  today = datetime.today()
  current_month = today.month
  current_year = today.year
  counter_index = open('Statistics/counter_'+ str(current_month) + '_' + str(current_year) + '.txt', 'a')
  #counter_index.write('hello')
  counter_index.write('{0:s} \n'.format('hello'))
  counter_index.close()

  return render_template('index_p0.jade')



@app.route('/Credit')
#@app.route('/page/<int:page>')
def credit_func():
  return render_template('Credit.jade')




@app.route('/formpage', methods=["GET", "POST"])
def get_contact():
    DIR = os.getcwd() + '/'
    if os.path.isdir(DIR + 'Contacts') == False:
      os.makedirs('Contacts')

    from datetime import datetime
    now = datetime.now()
    form = ContactForm()
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        institution = request.form["institution"]
        message = request.form["message"]
        res = pd.DataFrame({'name': name, 'email': email, 'institution': institution, 'message': message}, index=[0])
        res.to_csv('Contacts/contact_message_'+str(now.day)+'_'+str(now.month)+'_'+str(now.year)+'_'+str(now.hour)+'_'+str(now.minute)+'_'+str(now.second)+'.csv')
        flash(u'Thanks for your message. We will get back to you at the earliest.','success')
        return render_template('formpage.jade', form=form)
    else:
        return render_template('formpage.jade', form=form)




#"""
@app.route('/spectrum_data', defaults={'page': 1})
@app.route('/page/<int:page>')
def spectrum(page):
  #Remove files created in Kramers-Kroning tool if they exist
  DIR = os.getcwd() + '/'
  import shutil
  if os.path.isdir(DIR + 'application/uploads/') == True:
    shutil.rmtree(DIR + 'application/uploads/')
  else:
    pass
  
  if os.path.isdir(DIR + 'Cont_test/') == True:
    shutil.rmtree(DIR + 'Cont_test/')
  else:
    pass
  
  try:
    os.remove('Test_continuum.txt')
  except FileNotFoundError:
    pass
  
  try:
    os.remove('Test_append.txt')
  except FileNotFoundError:
    pass
  
  try:
    os.remove('Requested_continuum.txt')
  except FileNotFoundError:
    pass
  ###########################################################

  searchword = request.args.get('q')
  #print('LEN is:', len(searchword.split()))
  if searchword:
    if len(searchword.split()) >= 2:
      analogues = Analogue.query.filter(and_(Analogue.name.like('%' + word + '%') for word in searchword.split()))
    else:
      analogues = Analogue.query.filter(or_(Analogue.name.like('%' + searchword + '%'),
      Analogue.name2.like('%' + searchword + '%'),
      Analogue.name3.like('%' + searchword + '%'),
      Analogue.name4.like('%' + searchword + '%'),
      Analogue.name5.like('%' + searchword + '%')
      ))
  else:
    analogues = Analogue.query
  analogues = analogues.paginate(page, app.config['ANALOGUES_PER_PAGE'], True)

  stats = {
    'analogues_count': Analogue.query.count(),
    'spectra_count': Spectrum.query.count()
  }
  return render_template('spectrum_data.jade', analogues=analogues, stats=stats, q=searchword)
  #"""


@app.route('/data/<int:analogue_id>', methods=['GET'])
def analogue_show(analogue_id):
  analogue = Analogue.query.get(analogue_id)
  temperatures = sorted([s.temperature for s in analogue.spectra])
  t = [str(t) for t in temperatures]
  spectra = db.session.query(Spectrum).filter_by(analogue_id=analogue.id).order_by(Spectrum.temperature)

  
  DIR = os.getcwd() + '/'

  con = sqlite3.connect(DIR+'application/db/development.db')
  cur = con.cursor()
  all_analogues = []
  all_spectrum = []
  for row in cur.execute('SELECT * FROM spectra'):
    #print('reading development database...')
    #print(row[0], row[1])
    all_analogues.append(row[1])
    all_spectrum.append(row[0])
    #print("--------------------------------------")
  
  #print('All_analogues are:', all_analogues)
  #print('All_spectrum are:', all_spectrum)
  
  spec_idx_list = []
  for i,j in zip(range(len(all_analogues)), range(len(all_analogues))):
    if all_analogues[i] == analogue_id:
      spec_idx_list.append(all_spectrum[j])

  
  def temperatureRGB(minimum, maximum, value):
    x = (value - minimum) / (maximum - minimum)
    return int(255*x),int(0), int(255*(1-x))
  
  colours = []
  for t_ind in range(len(temperatures)):
    if len(temperatures) == 1:
      color = RGB(r = 255, g = 0, b = 0)
      colours.append(color)
    else:
      cc = temperatureRGB(min(temperatures),max(temperatures),temperatures[t_ind])
      color = RGB(r = cc[0], g = cc[1], b = cc[2])
      colours.append(color)
  
  p = figure(plot_height=300, sizing_mode='scale_both')
  
  miny = []
  maxy = []
  select_y = []
  for idx, temp, color in zip(range(len(spec_idx_list)), t, colours):
    print('reading idx:', idx)
    
    val = spectrum_show_json(spec_idx_list[idx])
    miny.append(min(val[1]))
    maxy.append(max(val[1]))
    source = ColumnDataSource(data=dict(x=val[0], y=val[1], x_top = 1e4/val[0]))
    r = p.line('x', 'y', source = source, line_width=2, color=color, line_alpha=1.0, hover_color=color, hover_alpha=1.0, hover_width=3,
           muted_color=color, muted_alpha=0.2, legend_label=temp+'K')
    

    try:
      annot = analogue_show_json(analogue_id)
      nu00, nu0, nu1, label, mol_name = annot[0], annot[1], annot[2], annot[3], annot[4]
      xx = val[0]
      yy = val[1]

      
      mol_name0 = str(":"+analogue.name2)
      mol_name = f'"{mol_name0}"'
      #mol_name0 = str(":"+mol_name)
      #print('ANNOT_4 IS', mol_name0, f'"{mol_name0}"')
      #mol_name = f'"{mol_name0}"'

      

      peak = np.interp(nu00, xx,yy)
      print('Values are:', nu00, peak.tolist())
      select_y.append(peak.tolist())

      reshape_select_y = np.array(select_y)
      col_n, row_n = reshape_select_y.shape[0], reshape_select_y.shape[1]
      
      top_y_annot = []
      for irow in range(row_n):
        top_y_annot.append(max(reshape_select_y[:,irow]))


    except TypeError:
      analogue_name = analogue.name2.replace(' ','_').replace('$','').replace('\ce','').replace('{','').replace('}','').replace('(','').replace(')','')
      analogue_name_pass = analogue_name.split()[0].replace('Pure_', '')
      #print('Name pass:', analogue_name_pass[0])
      mol_name0 = str(":"+analogue.name2)
      mol_name = f'"{mol_name0}"'
      print('Mol_name exception:', mol_name, analogue.name2)
      
      nu00, nu0, nu1, label = [0], [0], [0], ['none']
      top_y_annot = [-100]
      
  
  
  print('X positions are:', nu00)

  seg_h = p.segment(x0=nu0, y0=top_y_annot+0.07*np.array(max(maxy)), x1=nu1, y1=top_y_annot+0.07*np.array(max(maxy)), color="grey", line_width=2)
  seg_v = p.segment(x0=nu00, y0=top_y_annot+0.02*np.array(max(maxy)), x1=nu00, y1=top_y_annot+0.07*np.array(max(maxy)), color="green", line_width=3)
  seg_v_1 = p.segment(x0=nu0, y0=top_y_annot+0.02*np.array(max(maxy)), x1=nu0, y1=top_y_annot+0.07*np.array(max(maxy)), color="grey", line_width=2)
  seg_v_2 = p.segment(x0=nu1, y0=top_y_annot+0.02*np.array(max(maxy)), x1=nu1, y1=top_y_annot+0.07*np.array(max(maxy)), color="grey", line_width=2)
  
  source2 = ColumnDataSource(data=dict(height=top_y_annot+0.07*np.array(max(maxy)),
                                    weight=nu00,
                                    names=label))
  
  angle = math.radians(90)
  labels = LabelSet(x='weight', y='height', text='names',
              x_offset=7, y_offset=3, source=source2, render_mode='canvas', angle=angle, text_color='green')
  p.add_layout(labels)

  toggle1 = Toggle(label="Show/Hide annotation", button_type="warning", active=True)
  toggle1.js_link('active', seg_h, 'visible')
  toggle1.js_link('active', seg_v, 'visible')
  toggle1.js_link('active', seg_v_1, 'visible')
  toggle1.js_link('active', seg_v_2, 'visible')
  toggle1.js_link('active', labels, 'visible')
  widgets = column(toggle1, height=500, width=10)

  
  TOOLTIPS = """
  <div>
      <div>
          <span style="font-size: 18px;">Wavenumber</span>
          <span style="font-size: 18px; color: #696;">($x cm⁻¹)</span>
      </div>
      <div>
          <span style="font-size: 18px;">Wavelength:</span>
          <span style="font-size: 18px; color: #696;">(@x_top μm)</span>
      </div>
      <div>
          <span style="font-size: 18px;">Absorbance:</span>
          <span style="font-size: 18px; color: #696;">($y)</span>
      </div>
    </div>
  </div>"""
  
  
  p.add_tools(HoverTool(show_arrow=True, line_policy='interp', tooltips=TOOLTIPS))
  p.add_tools(CrosshairTool(line_color='grey', line_width=0.5))
  
  p.legend.location = "top_right"
  p.legend.label_text_font_size="16px"
  p.legend.click_policy="mute"
  p.x_scale = LogScale()
  p.xaxis.axis_label = 'Wavenumber (cm⁻¹)'
  p.xaxis.axis_label_text_font_style = "normal"
  p.xaxis.axis_label_text_font_size = '20px'
  p.yaxis.axis_label = 'Absorbance'
  p.yaxis.axis_label_text_font_style = "normal"
  p.yaxis.axis_label_text_font_size = '20px'
  #p.y_range=Range1d(start = min(miny) - 0.1*min(miny), end = max(maxy)+0.1*max(maxy))
  p.y_range=Range1d(start = min(miny)+0.05*min(miny), end = max(maxy)+0.4*max(maxy))
  p.x_range=Range1d(start = max(val[0]), end = min(val[0]))
  p.yaxis.major_label_text_font_size = '16px'
  p.xaxis.major_label_text_font_size = '16px'
  p.add_layout(LinearAxis(major_label_text_font_size = '1px'), 'right')
  #p.xaxis.ticker = [400, 500, 600, 700, 800, 1000, 1400, 1800, 2000, 3000, 4000, 5000]
  

  #p.x_scale = LinearScale()
  p.extra_x_ranges = {"x_mic": Range1d(1e4/max(val[0]), 1e4/min(val[0]))}
  top_axis = LogAxis(x_range_name = "x_mic", axis_label="Wavelength (μm)", axis_label_text_font_style='normal', axis_label_text_font_size='20px', major_label_text_font_size = '16px')
  p.add_layout(top_axis, 'above')
  p.toolbar.autohide = False

  #show(p)


  content = column(layout([p, widgets]), height=650, sizing_mode='stretch_width')
  script, div = components(content)

  #inp_column = column(toggle)
  #layout_row = row([inp_column, p])

  return render_template(
          'Spec_show.jade',
          analogue=analogue,
          mol_name=mol_name,
          spectra=spectra,
          plot_script=script,
          plot_div=div,
          js_resources=INLINE.render_js(),
          css_resources=INLINE.render_css(),
      ).encode(encoding='UTF-8')
  
  
  
  """return render_template(
    'show.jade',
    analogue=analogue,
    spectra=spectra)"""


def split(arr, cond):
  return [arr[cond], arr[~cond]]

@app.route('/spectrum/<int:spectrum_id>.json', methods=['GET'])
def spectrum_show_json(spectrum_id):
  spectrum = Spectrum.query.get(spectrum_id)
  print('Spec_id is:', spectrum_id)
  print('Spectrum is:', spectrum)
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

  dataX = data[:,0]
  dataY = data[:,1]

  return dataX, dataY 
  #return jsonify(temperature=spectrum.temperature, data=data.tolist())


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
  analogue = Analogue.query.get(analogue_id)
  analogue_name = analogue.name.replace(' ','_').replace('$','').replace('\ce','').replace('{','').replace('}','').replace('(','').replace(')','')
  counter_download = open('Statistics/counter_download_tar_gz.dat', 'a')
  counter_download.write('{0:s} {1:d}\n'.format(analogue_name, 1))
  counter_download.close()
  print('Spectra:', analogue_id)
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
  
  try:
    analogue = Analogue.query.get(analogue_id)

    DIR = os.getcwd() + '/'
    

    analogue_name = analogue.name.replace(' ','_').replace('$','').replace('\ce','').replace('{','').replace('}','').replace('(','').replace(')','')

    nuc, nui, nuf= np.loadtxt(DIR+'application/annotations/'+analogue_name+'.csv',dtype=float, delimiter=',', usecols=(0,1,2)).T
    annotation = np.loadtxt(DIR+'application/annotations/'+analogue_name+'.csv',dtype=str, delimiter=',', usecols=(3)).T

    print('Testing annotation:', nuc.tolist(), nui.tolist(), nuf.tolist(), annotation.tolist())
    print('Analogue name is hehe:', analogue_name.split()[0].replace('Pure_', ''))
    analogue_name_pass = analogue_name.split()[0].replace('Pure_', '')
    

    return nuc.tolist(), nui.tolist(), nuf.tolist(), annotation.tolist(), analogue_name_pass
  except OSError:
    pass

from application import nkabsv_log_leiden
import os
from flask import Flask, render_template, request, redirect, url_for, abort, flash
from werkzeug.utils import secure_filename

DIR = os.getcwd() + '/'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 # 500 Kb
app.config['UPLOAD_EXTENSIONS'] = ['.dat', '.txt']
if os.path.isdir(DIR + 'application/uploads/') == False:
  os.makedirs(DIR + 'application/uploads/')
else:
  pass
app.config['UPLOAD_PATH'] = DIR+'application/uploads/'

import imghdr

def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/index00')
def index00():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('Kramers_Kronig_nograph.jade', files=files)

@app.route('/index00', methods=['GET','POST'])
def upload_files():
    import glob
    DIR = os.getcwd() + '/'
    if os.path.isdir(DIR + 'application/uploads/') == False:
      os.makedirs(DIR + 'application/uploads/')
    elif len(glob.glob(DIR + 'application/uploads/*.txt')) > 1:
      flash(u'Two potential input files were identified. Please, press the button "Clear and Restart" before continue.','error')
      return redirect(url_for('kramers'))
    else:
      pass
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                file_ext == validate_image(uploaded_file.stream):
            flash(u'File extension not accepted. Please, use txt or dat','error')
            return redirect(url_for('kramers'))
            #abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        flash('File successfully uploaded!', 'success')
    else:
      flash('Please, upload a file!', 'error')
    return redirect(url_for('index00'))

@app.route('/uploads/<filename>')
def upload(filename):
    #message = 'File upload successfully!'
    return send_from_directory(app.config['UPLOAD_PATH'], filename)




@app.route('/Kramers_Kronig')
#@app.route('/page/<int:page>')
def kramers():
  print('READING HERE!')
  inp_thickness = request.args.get("inp_thickness", "")
  inp_nvis = request.args.get("inp_nvis", "")
  inp_nsubs = request.args.get("inp_nsubs", "")
  inp_mape = request.args.get("inp_mape", "")
  outputs = nkabsv_log_leiden.kramers_kronig(inp_thickness, inp_nvis, inp_nsubs,inp_mape)
  
  DIR = os.getcwd() + '/'
  if os.path.isfile(DIR+'application/uploads/K.txt') == True:
    #flash('Calculation in progress...', 'success')   
    xk,yk = np.loadtxt(DIR+'application/uploads/K.txt', dtype=float, usecols=(0,1)).T
    xn,yn = np.loadtxt(DIR+'application/uploads/N.txt', dtype=float, usecols=(0,1)).T
        
    #pcont = figure(plot_height=250, sizing_mode='scale_both')
    pn = figure(plot_height=450, plot_width = 1100, sizing_mode='fixed')
    source = ColumnDataSource(data=dict(x=xk, y=yk, x_top = 1e4/xk))
    r = pn.line('x', 'y', source = source, line_width=2, color='blue', line_alpha=1.0, hover_color='black', hover_alpha=1.0, hover_width=3,
          muted_color='grey', muted_alpha=0.2, legend_label='K')
    
    TOOLTIPS = """
    <div>
        <div>
            <span style="font-size: 18px;">Wavenumber</span>
            <span style="font-size: 18px; color: #696;">($x cm⁻¹)</span>
        </div>
        <div>
            <span style="font-size: 18px;">Wavelength:</span>
            <span style="font-size: 18px; color: #696;">(@x_top μm)</span>
        </div>
        <div>
            <span style="font-size: 18px;">Refrac_index:</span>
            <span style="font-size: 18px; color: #696;">($y)</span>
        </div>
      </div>
    </div>"""
        
        
    pn.add_tools(HoverTool(show_arrow=True, line_policy='interp', tooltips=TOOLTIPS))
    pn.add_tools(CrosshairTool(line_color='grey', line_width=0.5))
        
    pn.legend.location = "top_right"
    pn.legend.label_text_font_size="16px"
    pn.legend.click_policy="mute"
    pn.x_scale = LogScale()
    pn.xaxis.axis_label = 'Wavenumber (cm⁻¹)'
    pn.xaxis.axis_label_text_font_style = "normal"
    pn.xaxis.axis_label_text_font_size = '20px'
    pn.yaxis.axis_label = 'Refractive index'
    pn.yaxis.axis_label_text_font_style = "normal"
    pn.yaxis.axis_label_text_font_size = '20px'
    #p.y_range=Range1d(start = min(miny) - 0.1*min(miny), end = max(maxy)+0.1*max(maxy))
    #p.y_range=Range1d(start = min(miny)+0.05*min(miny), end = max(maxy)+0.4*max(maxy))
    pn.x_range=Range1d(start = max(xk), end = min(xk))
    pn.yaxis.major_label_text_font_size = '16px'
    pn.xaxis.major_label_text_font_size = '16px'
    pn.add_layout(LinearAxis(major_label_text_font_size = '1px'), 'right')
    #p.xaxis.ticker = [400, 500, 600, 700, 800, 1000, 1400, 1800, 2000, 3000, 4000, 5000]

    #p.x_scale = LinearScale()
    pn.extra_x_ranges = {"x_mic": Range1d(1e4/max(xk), 1e4/min(xk))}
    top_axis = LogAxis(x_range_name = "x_mic", axis_label="Wavelength (μm)", axis_label_text_font_style='normal', axis_label_text_font_size='20px', major_label_text_font_size = '16px')
    pn.add_layout(top_axis, 'above')
    pn.toolbar.autohide = False
    
    pk = figure(plot_height=450, plot_width = 1100, sizing_mode='fixed')
    source2 = ColumnDataSource(data=dict(x=xn, y=yn, x_top = 1e4/xn))
    r2 = pk.line('x', 'y', source = source2, line_width=2, color='red', line_alpha=1.0, hover_color='black', hover_alpha=1.0, hover_width=3,
    muted_color='grey', muted_alpha=0.2, legend_label='N')

    TOOLTIPS = """
    <div>
        <div>
            <span style="font-size: 18px;">Wavenumber</span>
            <span style="font-size: 18px; color: #696;">($x cm⁻¹)</span>
        </div>
        <div>
            <span style="font-size: 18px;">Wavelength:</span>
            <span style="font-size: 18px; color: #696;">(@x_top μm)</span>
        </div>
        <div>
            <span style="font-size: 18px;">Refrac_index:</span>
            <span style="font-size: 18px; color: #696;">($y)</span>
        </div>
      </div>
    </div>"""
        
        
    pk.add_tools(HoverTool(show_arrow=True, line_policy='interp', tooltips=TOOLTIPS))
    pk.add_tools(CrosshairTool(line_color='grey', line_width=0.5))
        
    pk.legend.location = "top_right"
    pk.legend.label_text_font_size="16px"
    pk.legend.click_policy="mute"
    pk.x_scale = LogScale()
    pk.xaxis.axis_label = 'Wavenumber (cm⁻¹)'
    pk.xaxis.axis_label_text_font_style = "normal"
    pk.xaxis.axis_label_text_font_size = '20px'
    pk.yaxis.axis_label = 'Refractive index'
    pk.yaxis.axis_label_text_font_style = "normal"
    pk.yaxis.axis_label_text_font_size = '20px'
    #p.y_range=Range1d(start = min(miny) - 0.1*min(miny), end = max(maxy)+0.1*max(maxy))
    #p.y_range=Range1d(start = min(miny)+0.05*min(miny), end = max(maxy)+0.4*max(maxy))
    pk.x_range=Range1d(start = max(xk), end = min(xk))
    pk.yaxis.major_label_text_font_size = '16px'
    pk.xaxis.major_label_text_font_size = '16px'
    pk.add_layout(LinearAxis(major_label_text_font_size = '1px'), 'right')
    #p.xaxis.ticker = [400, 500, 600, 700, 800, 1000, 1400, 1800, 2000, 3000, 4000, 5000]

    #p.x_scale = LinearScale()
    pk.extra_x_ranges = {"x_mic": Range1d(1e4/max(xk), 1e4/min(xk))}
    top_axis = LogAxis(x_range_name = "x_mic", axis_label="Wavelength (μm)", axis_label_text_font_style='normal', axis_label_text_font_size='20px', major_label_text_font_size = '16px')
    pk.add_layout(top_axis, 'above')
    pk.toolbar.autohide = False
    #content = column(p, pcont, sizing_mode='stretch_height')
    content = column(pk, pn, height=550, sizing_mode='stretch_height')
    script, div = components(content)
    return render_template('Kramers_Kronig.jade', plot_script=script, plot_div=div, js_resources=INLINE.render_js(), css_resources=INLINE.render_css(),).encode(encoding='UTF-8')
  else:
    print('READING THERE!')
    inp_thickness = request.args.get("inp_thickness", "")
    inp_nvis = request.args.get("inp_nvis", "")
    inp_nsubs = request.args.get("inp_nsubs", "")
    inp_mape = request.args.get("inp_mape", "")
    outputs = nkabsv_log_leiden.kramers_kronig(inp_thickness, inp_nvis, inp_nsubs,inp_mape)
    return render_template('Kramers_Kronig_nograph.jade')



@app.route('/return-files')
def download_optc_const():
  try:
    import shutil
    DIR = os.getcwd() + '/'
    p = DIR+'outputs_optc_const.zip'
    shutil.rmtree(DIR+'/application/uploads/')
    return send_file(p,as_attachment=True)
  except FileNotFoundError:
    flash(u'The outputs were not created yet.','error')
    return redirect(url_for('kramers'))

@app.route('/delete_optc_files/', methods=['GET', 'POST'])
def delete_optc_files():
    import glob
    import shutil
    DIR = os.getcwd() + '/'
    filename1 = (DIR+'/application/uploads/')
    filename2 = DIR+'outputs_optc_const.zip'
    try:
      shutil.rmtree(filename1)
      os.remove(filename2)
    except FileNotFoundError:
      pass
    return redirect(url_for('kramers'))




class Form(FlaskForm):
    #ice_analogue = SelectField('analogue_id', choices=[('1', 'HCOOH'), ('2', 'H2O')])
    ice_analogue = SelectField('analogue_id', choices=[])
    ice_spectrum = SelectField('spectrum', choices=[])

class Form_Cont(FlaskForm):
    #ice_analogue = SelectField('analogue_id', choices=[('1', 'HCOOH'), ('2', 'H2O')])
    cont_analogue = SelectField('sc_analogue_id', choices=[])
    cont_spectrum = SelectField('spectrum_cont', choices=[])



@app.route('/Synt_Spec', methods=['GET', 'POST'])
def synthetic():
    #Delete files from Kramers_Kroning
    DIR = os.getcwd() + '/'
    import shutil
    if os.path.isdir(DIR + 'application/uploads/') == True:
      shutil.rmtree(DIR + 'application/uploads/')
    else:
      pass

    form = Form()
    #form.ice_spectrum.choices = [(ice_spectrum.id, ice_spectrum.temperature) for ice_spectrum in Spectrum.query.filter_by(analogue_id='1').all()]
    form.ice_analogue.choices = [(ice_analogue.id, ice_analogue.name3) for ice_analogue in Analogue.query.all()]

    form_cont = Form_Cont()
    form_cont.cont_analogue.choices = [(cont_analogue.id, cont_analogue.name) for cont_analogue in SC_Object.query.all()]

    if request.method == 'POST':
      if "form_analogue" in request.form:
        ice_analogue = Analogue.query.filter_by(id=form.ice_analogue.data).first()
        ice_spectrum = Spectrum.query.filter_by(id=form.ice_spectrum.data).first()
        
        sample0 = ice_analogue.name3.replace(' ','_').replace('$', '').replace('\ce{', '').replace('}','')
        try:
          sample = sample0+'_@_'+str(ice_spectrum.temperature)+'K'
        except AttributeError:
          flash(u'Please, select the temperature for the analogue.','error')
          return redirect(url_for('synthetic'))
        analogue_request_is = form.ice_analogue.data
        temp_request_is = ice_spectrum.temperature
        cd_request_is = ice_spectrum.column_density
        #thickness_request_is = 6e-4 #6e-4 cm = 10000 ML (using 1 ML = 0.6 nm).
        spec_id_request_is = ice_spectrum.id
        print('Analogue_Request is:', analogue_request_is, sample, ice_analogue.name3)
        print('Temp_Request is:', temp_request_is, spec_id_request_is)
        print('CD_Request is:', cd_request_is)
        default_name = cd_request_is
        input_cd = request.form.get('cd_scale', default_name)
        #input_num_den = request.form.get('num_dens', thickness_request_is)
        print('Input cd:', input_cd)
        #print('Input num_dens:', input_num_den)
        
        if cd_request_is is None:
          factor = 1.
          #factor_num_dens = 1.
          print('Column density not provided in the database')
          flash(u'Attention: Column density not provided in the database!','warning')
        elif input_cd == '':
          flash(u'Please, provide a value of column density','error')
          return redirect(url_for('synthetic'))
        else:
          try:
            factor = float(input_cd)/cd_request_is
            flash(u'Data parsed successfully!','success')
            print('DATA is:', input_cd, factor)
          except TypeError:
            flash(u'Data parsed successfully!','success')
            factor = input_cd/cd_request_is
            print('DATA is:', input_cd, factor)
        

        f = open('Test_append.txt', 'a')
        f.write('{0:d} {1:d} {2:s} {3:f} \n'.format(spec_id_request_is, spec_id_request_is, sample, factor))
        f.close()

      elif "form_continuum" in request.form:
        ######Section for Continuum
        cont_analogue = SC_Object.query.filter_by(id=form_cont.cont_analogue.data).first()
        cont_spectrum = SC_spec.query.filter_by(id=form_cont.cont_spectrum.data).first()
        ##Continuum Requests:
        obj0 = cont_analogue.name.replace(' ','_')
        Object_request = form_cont.cont_analogue.data
        #temp_request = cont_spectrum.temperature
        print('Continuum requests areXXXX:', Object_request,obj0)
        f = open('Requested_continuum.txt', 'w')
        f.write('{0:d} {1:d} {2:s} \n'.format(int(Object_request), int(Object_request), obj0))
        f.close()
      else:
        print("NOTHING WAS REQUESTED!")



      ######
    
    
    inp_lam1 = request.args.get("inp_lam1", "")
    inp_lam2 = request.args.get("inp_lam2", "")


    p = figure(plot_height=450, plot_width = 1100, sizing_mode='fixed')
    summed_data = 0
    DIR = os.getcwd() + '/'
    from pathlib import Path
    myfile = Path(DIR+'Test_append.txt')
    myfile.touch(exist_ok=True)
    try:
      an_id,sp_id = np.loadtxt(DIR+'Test_append.txt', dtype=int, usecols=(0,1)).T
      name = np.loadtxt(DIR+'Test_append.txt', dtype=str, usecols=(2)).T
      sc_factor = np.loadtxt(DIR+'Test_append.txt', dtype=float, usecols=(3)).T
      print('Reading Test_append file...')
      print(an_id, name, sc_factor)
      print('------------------------------')
    except ValueError:
      an_id,sp_id,name, sc_factor = 1,1,'test',1
    
    lstX = []
    lstY = []
    lstN = []
    lstC = []
    lstSF = []

    from scipy.interpolate import interp1d
    colors=['red', 'blue', 'green', 'magenta', 'purple', 'darkorange','gold','darkorchid','aqua','cadetblue','darkolivegreen','burlywood','chartreuse','chocolate','coral','cornflowerblue','black','darkkhaki','pink','moccasin','limegreen']

    try:
      print('Reading TWO component!')
      count = 1
      for i,j,n,c,scf in zip(an_id,sp_id,name,colors, sc_factor):
        print('Parameters:', i,j,n,c,scf)
        con = DIR+'application/data/'+str(i)+'/'+str(j)+'.h5'
        with h5py.File(con, 'r') as f:
          data = f['spectrum'][()]

        data = data[::round(len(data)/1000)]

        # Signal often starts with instrument noise (wavenumber < 500), cut that out
        parts = split(data, data[:,0] < 500)
        noise = parts[0]
        average = numpy.average(parts[1][:,1])
        maximum_distance = abs(average * 1.5)
        parts[0] = noise[abs(noise[:,1]-average) < maximum_distance]
        data = numpy.concatenate(parts)

        
        dataX = data[:,0]
        try:
          if os.path.isdir(DIR + 'Cont_test') == False:
            os.makedirs('Cont_test')
          
          print('USING M1')
          if input_cd:
            print('FACTOR IS:', factor)
            print('USING THE COLUMN DENSITY METHOD')
            #print('FACTOR_NUM_DENS IS:', factor_num_dens)
            dataY = scf*data[:,1]
          elif input_num_den:
            print('FACTOR_NUM_DENS IS:', sc_factor)
            print('USING THE NUMBER DENSITY METHOD')
            dataY = scf*data[:,1]
        except UnboundLocalError:
          print('M1: Factor NOT applied!')
          dataY = data[:,1]
        
        new_data = interp1d(dataX,dataY)
        if inp_lam1:
          xinit,xend = 1e4/float(inp_lam2), 1e4/float(inp_lam1)
          xnew = np.linspace(xinit,xend,5000)
          print('Inputs are:', inp_lam1, inp_lam2, 1e4/float(inp_lam2), 1e4/float(inp_lam1))
        else:
          xnew = np.linspace(dataX[0],dataX[len(dataX)-1],5000)
          print('Argument not provided')
        
        try:
          ynew = new_data(xnew)
        except ValueError:
          flash(u'Interval is out of the range of the experimental data. Please, provide another range.','error')

        #lstX.append(dataX)
        #lstY.append(dataY)
        lstX.append(xnew)
        lstY.append(ynew)
        lstN.append(n)
        lstC.append(c)
        lstSF.append(scf)

        summed_data += ynew
        #print('Max SUM_DATA1 is:', max(summed_data))
        np.savetxt('Cont_test/component_'+str(count)+'.dat', np.transpose([xnew, ynew]))
        np.savetxt('Cont_test/total_components.txt', np.transpose([xnew, summed_data]))
        count = count + 1
    except TypeError:
      print('Reading one component!')
      con = DIR+'application/data/'+str(an_id)+'/'+str(sp_id)+'.h5'
      with h5py.File(con, 'r') as f:
        data = f['spectrum'][()]

      data = data[::round(len(data)/1000)]

      # Signal often starts with instrument noise (wavenumber < 500), cut that out
      parts = split(data, data[:,0] < 500)
      noise = parts[0]
      average = numpy.average(parts[1][:,1])
      maximum_distance = abs(average * 1.5)
      parts[0] = noise[abs(noise[:,1]-average) < maximum_distance]
      data = numpy.concatenate(parts)

      
      dataX = data[:,0]
      
      try:
        print('USING M2')
        if input_cd:
          print('FACTOR IS:', factor)
          print('USING THE COLUMN DENSITY METHOD')
          #print('FACTOR_NUM_DENS IS:', factor_num_dens)
          dataY = sc_factor*data[:,1]
        elif input_num_den:
          print('FACTOR_NUM_DENS IS:', factor)
          print('USING THE NUMBER DENSITY METHOD')
          dataY = sc_factor*data[:,1]
      except UnboundLocalError:
        print('M2: Factor NOT applied!')
        dataY = data[:,1]
      
      new_data = interp1d(dataX,dataY)
      #xnew = np.linspace(dataX[0],dataX[len(dataX)-1],5000)
      if inp_lam1:
        xinit,xend = 1e4/float(inp_lam2), 1e4/float(inp_lam1)
        xnew = np.linspace(xinit,xend,5000)
        print('Inputs are:', inp_lam1, inp_lam2)
      else:
        xnew = np.linspace(dataX[0],dataX[len(dataX)-1],5000)
        print('Argument not provided')
      try:
        ynew = new_data(xnew)
      except ValueError:
        flash(u'Interval is out of the range of the experimental data. Please, provide another range.','error')
        return redirect(url_for('synthetic'))

      lstX.append(xnew)
      lstY.append(ynew)
      lstN.append(name)
      lstC.append(colors[0])
      lstSF.append(sc_factor)

      #summed_data += sp_id*data[:,1]
      summed_data += ynew
      #print('Max SUM_DATA2 is:', max(summed_data))


    #print('Max SUM_DATA3 is:', max(summed_data))
    
    try:
      if os.path.isdir(DIR + 'Cont_test/Final') == False:
        os.makedirs('Cont_test/Final')
      DIR = os.getcwd() + '/'
      from pathlib import Path
      myfile_c = Path(DIR+'Requested_continuum.txt')
      myfile_c.touch(exist_ok=True)
      
      obj_id,spec_id = np.loadtxt(DIR+'Requested_continuum.txt', dtype=int, usecols=(0,1)).T
      name_c = np.loadtxt(DIR+'Requested_continuum.txt', dtype=str, usecols=(2)).T
      
      con = DIR+'application/data_sc/'+str(obj_id)+'/'+str(spec_id)+'.h5'
      with h5py.File(con, 'r') as f:
        data_cont = f['spectrum_cont'][()]
        
      xcont, ycont = data_cont[:,0], data_cont[:,1]
      #print('Ycont1:', xcont, ycont)

      import scipy.interpolate as spi
      new_cont = spi.interp1d(1e4/xcont, ycont, fill_value="extrapolate")
      #print('New_cont:', new_cont)
      if inp_lam1:
        xinit_c,xend_c = 1e4/float(inp_lam2), 1e4/float(inp_lam1)
        xnew_c = np.linspace(xinit_c, xend_c,5000)
        print('Cont_ranges are:', xnew_c)
      else:
        xnew_c = np.linspace(xcont[0],xcont[len(xcont)-1],5000)
        print('Argument not provided')
      
      ynew_c = new_cont(xnew_c)
      #print('Ycont2:', ynew_c)
      #print('Max SUM_DATA4 is:', max(summed_data))
      import glob
      sc_factor = np.loadtxt(DIR+'Test_append.txt', dtype=float, usecols=(3)).T
      all_comp = sorted(glob.glob(DIR+'Cont_test/*.dat'))
      #print('sc_factor:', sc_factor, len(all_comp))

      summed = 0
      lstXc = []
      lstYc = []
      count2 = 1
      for index in range(len(all_comp)):
        #print('Count is:', count2)
        #print('Index:', index)
        #print('Components:', all_comp[index])
        x_sum,y_sum = np.loadtxt(all_comp[index], dtype=float, usecols=(0,1)).T
        comp = y_sum*sc_factor[index]
        lstXc.append(x_sum)
        lstYc.append(comp)
        summed += y_sum*sc_factor[index]
        np.savetxt('Cont_test/Final/component_'+str(count2)+'.dat', np.transpose([x_sum, comp]))
        np.savetxt('Cont_test/Final/total_components.txt', np.transpose([x_sum, summed]))
        count2 = count2 + 1
      
      Flux = ynew_c*np.exp(-2.3*summed)
      #print('Flux is', Flux)
      #print('Wav is', xnew_c, len(xnew_c))
      #print('Wav2 is:', xnew, len(xnew))

      import pandas as pd
      df = pd.DataFrame({
        'col1': 1e4/x_sum,
        'col2': Flux
      })
      df_sorted = df.sort_values(by='col1', ascending=True)
      np.savetxt('Cont_test/Final/Synthetic_spec.txt', np.transpose([df_sorted['col1'], df_sorted['col2']]))
      import shutil
      from shutil import make_archive
      shutil.make_archive('outputs', 'zip','/Users/willrocha/T0/ice-database/Cont_test/Final/')
      #pcont = figure(plot_height=250, sizing_mode='scale_both')
      pcont = figure(plot_height=450, plot_width = 1100, sizing_mode='fixed')
      source_continuum = ColumnDataSource(data=dict(x=1e4/xnew_c, y=Flux))
      r_cont = pcont.line('x', 'y', source = source_continuum, line_width=2, color='black', line_alpha=1.0, hover_color='black', hover_alpha=1.0, hover_width=3,
            muted_color='grey', muted_alpha=0.2, legend_label=str(name_c))
      pcont.legend.location = "top_right"
      pcont.legend.label_text_font_size="16px"
      pcont.legend.click_policy="mute"
      pcont.x_scale = LogScale()
      pcont.y_scale = LogScale()
      pcont.xaxis.axis_label = 'Wavelength (μm)'
      pcont.xaxis.axis_label_text_font_style = "normal"
      pcont.xaxis.axis_label_text_font_size = '20px'
      pcont.yaxis.axis_label = 'Flux (Jy)'
      pcont.yaxis.axis_label_text_font_style = "normal"
      pcont.yaxis.axis_label_text_font_size = '20px'
      #p.y_range=Range1d(start = min(miny) - 0.1*min(miny), end = max(maxy)+0.1*max(maxy))
      #p.y_range=Range1d(start = min(miny)+0.05*min(miny), end = max(maxy)+0.4*max(maxy))
      pcont.x_range=Range1d(start = 1e4/xnew_c[len(xnew_c)-1], end = 1e4/xnew_c[0])
      pcont.yaxis.major_label_text_font_size = '16px'
      pcont.xaxis.major_label_text_font_size = '16px'
      pcont.add_layout(LinearAxis(major_label_text_font_size = '1px'), 'right')
      #pcont.y_range.flipped = True
      pcont.extra_x_ranges = {"x_wn": Range1d(max(xnew_c), min(xnew_c))}
      top_axis_cont = LogAxis(x_range_name = "x_wn", axis_label="Wavenumber (cm⁻¹)", axis_label_text_font_style='normal', axis_label_text_font_size='20px', major_label_text_font_size = '16px')
      pcont.add_layout(top_axis_cont, 'above')

      ##STARTING DATA WITHOUT

      data_m = {'xs': lstXc,'ys': lstYc, 'labels': lstN, 'color':lstC}
      source_m = ColumnDataSource(data_m)
      p.multi_line(xs='xs', ys='ys', line_width=1, legend_group='labels', color='color', source=source_m, muted_color='grey', muted_alpha=0.2)
      
      source = ColumnDataSource(data=dict(x=xnew, y=summed, x_top = 1e4/xnew))
      r = p.line('x', 'y', source = source, line_width=2, color='black', line_alpha=1.0, hover_color='black', hover_alpha=1.0, hover_width=3,
            muted_color='grey', muted_alpha=0.2, legend_label='Synthetic spectrum')
      
      TOOLTIPS = """
      <div>
          <div>
              <span style="font-size: 18px;">Wavenumber</span>
              <span style="font-size: 18px; color: #696;">($x cm⁻¹)</span>
          </div>
          <div>
              <span style="font-size: 18px;">Wavelength:</span>
              <span style="font-size: 18px; color: #696;">(@x_top μm)</span>
          </div>
          <div>
              <span style="font-size: 18px;">Absorbance:</span>
              <span style="font-size: 18px; color: #696;">($y)</span>
          </div>
        </div>
      </div>"""
      
      
      p.add_tools(HoverTool(show_arrow=True, line_policy='interp', tooltips=TOOLTIPS))
      p.add_tools(CrosshairTool(line_color='grey', line_width=0.5))
      
      p.legend.location = "top_right"
      p.legend.label_text_font_size="16px"
      p.legend.click_policy="mute"
      p.x_scale = LogScale()
      p.xaxis.axis_label = 'Wavenumber (cm⁻¹)'
      p.xaxis.axis_label_text_font_style = "normal"
      p.xaxis.axis_label_text_font_size = '20px'
      p.yaxis.axis_label = 'Optical depth'
      p.yaxis.axis_label_text_font_style = "normal"
      p.yaxis.axis_label_text_font_size = '20px'
      #p.y_range=Range1d(start = min(miny) - 0.1*min(miny), end = max(maxy)+0.1*max(maxy))
      #p.y_range=Range1d(start = min(miny)+0.05*min(miny), end = max(maxy)+0.4*max(maxy))
      p.x_range=Range1d(start = max(xnew), end = min(xnew))
      p.yaxis.major_label_text_font_size = '16px'
      p.xaxis.major_label_text_font_size = '16px'
      p.add_layout(LinearAxis(major_label_text_font_size = '1px'), 'right')
      #p.xaxis.ticker = [400, 500, 600, 700, 800, 1000, 1400, 1800, 2000, 3000, 4000, 5000]
      

      #p.x_scale = LinearScale()
      p.extra_x_ranges = {"x_mic": Range1d(1e4/max(xnew), 1e4/min(xnew))}
      top_axis = LogAxis(x_range_name = "x_mic", axis_label="Wavelength (μm)", axis_label_text_font_style='normal', axis_label_text_font_size='20px', major_label_text_font_size = '16px')
      p.add_layout(top_axis, 'above')
      p.toolbar.autohide = False
      content = column(p, pcont, sizing_mode='stretch_height')
      script, div = components(content)
      
      return render_template('Synt_Spec.jade', form=form, form_cont=form_cont, plot_script=script, plot_div=div, js_resources=INLINE.render_js(), css_resources=INLINE.render_css(),).encode(encoding='UTF-8')
    except (ValueError, UnboundLocalError, OSError):
      
      print('Passing Continuum section!!!')
      pass

    
    data_m = {'xs': lstX,'ys': lstY, 'labels': lstN, 'color':lstC}
    source_m = ColumnDataSource(data_m)
    p.multi_line(xs='xs', ys='ys', line_width=1, legend_group='labels', color='color', source=source_m, muted_color='grey', muted_alpha=0.2)
    
    source = ColumnDataSource(data=dict(x=xnew, y=summed_data, x_top = 1e4/xnew))
    r = p.line('x', 'y', source = source, line_width=2, color='black', line_alpha=1.0, hover_color='black', hover_alpha=1.0, hover_width=3,
          muted_color='grey', muted_alpha=0.2, legend_label='Synthetic spectrum')
    
    TOOLTIPS = """
    <div>
        <div>
            <span style="font-size: 18px;">Wavenumber</span>
            <span style="font-size: 18px; color: #696;">($x cm⁻¹)</span>
        </div>
        <div>
            <span style="font-size: 18px;">Wavelength:</span>
            <span style="font-size: 18px; color: #696;">(@x_top μm)</span>
        </div>
        <div>
            <span style="font-size: 18px;">Absorbance:</span>
            <span style="font-size: 18px; color: #696;">($y)</span>
        </div>
      </div>
    </div>"""
    
    
    p.add_tools(HoverTool(show_arrow=True, line_policy='interp', tooltips=TOOLTIPS))
    p.add_tools(CrosshairTool(line_color='grey', line_width=0.5))
    
    p.legend.location = "top_right"
    p.legend.label_text_font_size="16px"
    p.legend.click_policy="mute"
    p.x_scale = LogScale()
    p.xaxis.axis_label = 'Wavenumber (cm⁻¹)'
    p.xaxis.axis_label_text_font_style = "normal"
    p.xaxis.axis_label_text_font_size = '20px'
    p.yaxis.axis_label = 'Optical depth'
    p.yaxis.axis_label_text_font_style = "normal"
    p.yaxis.axis_label_text_font_size = '20px'
    #p.y_range=Range1d(start = min(miny) - 0.1*min(miny), end = max(maxy)+0.1*max(maxy))
    #p.y_range=Range1d(start = min(miny)+0.05*min(miny), end = max(maxy)+0.4*max(maxy))
    p.x_range=Range1d(start = max(xnew), end = min(xnew))
    p.yaxis.major_label_text_font_size = '16px'
    p.xaxis.major_label_text_font_size = '16px'
    p.add_layout(LinearAxis(major_label_text_font_size = '1px'), 'right')
    #p.xaxis.ticker = [400, 500, 600, 700, 800, 1000, 1400, 1800, 2000, 3000, 4000, 5000]
    

    #p.x_scale = LinearScale()
    p.extra_x_ranges = {"x_mic": Range1d(1e4/max(xnew), 1e4/min(xnew))}
    top_axis = LogAxis(x_range_name = "x_mic", axis_label="Wavelength (μm)", axis_label_text_font_style='normal', axis_label_text_font_size='20px', major_label_text_font_size = '16px')
    p.add_layout(top_axis, 'above')
    p.toolbar.autohide = False
    content = column(p, height=550, sizing_mode='fixed')
    script, div = components(content)
    
    return render_template('Synt_Spec.jade', form=form, form_cont=form_cont, plot_script=script, plot_div=div, js_resources=INLINE.render_js(), css_resources=INLINE.render_css(),).encode(encoding='UTF-8')

@app.route('/pick_analogue/<int:analogue_id>')
def spec(analogue_id):
  all_spec = Spectrum.query.filter_by(analogue_id=analogue_id).all()
  print('Specs are:', all_spec)
  
  all_specArray = []
  
  for ice_spectrum in all_spec:
    ice_spectrumObj = {}
    ice_spectrumObj['id'] = ice_spectrum.id
    ice_spectrumObj['temperature'] = ice_spectrum.temperature
    all_specArray.append(ice_spectrumObj)
  print('All_spec are:', all_specArray)
  return jsonify({'all_spec' : all_specArray})

@app.route('/pick_object/<int:sc_analogue_id>')
def spec_cont(sc_analogue_id):
  all_spec = SC_spec.query.filter_by(sc_analogue_id=sc_analogue_id).all()
  
  all_specArray = []
  
  for cont_spectrum in all_spec:
    cont_spectrumObj = {}
    cont_spectrumObj['id'] = cont_spectrum.id
    cont_spectrumObj['cont_model'] = cont_spectrum.cont_model
    all_specArray.append(cont_spectrumObj)
  print('All_spec are:', all_specArray)
  #np.savetxt('Request_continuum.txt', all_specArray)
  return jsonify({'all_spec_cont' : all_specArray})

@app.route('/delete_item/', methods=['GET', 'POST'])
def delete_item():
    import glob
    import shutil
    DIR = os.getcwd() + '/'
    filename = DIR+'Test_append.txt'
    filename2 = DIR+'Requested_continuum.txt'
    filename3 = (DIR+'Cont_test/')
    filename4 = DIR+'outputs.zip'
    os.remove(filename)
    os.remove(filename2)
    try:
      shutil.rmtree(filename3)
      os.remove(filename4)
    except FileNotFoundError:
      pass
    return redirect(url_for('synthetic'))




@app.route('/download')
def download_file():
  try:
    DIR = os.getcwd() + '/'
    p = DIR+'outputs.zip'
    return send_file(p,as_attachment=True)
  except FileNotFoundError:
    flash(u'The outputs were not created yet.','error')
    return redirect(url_for('synthetic'))


##############################################
##############################################
##############################################
##############################################
##############################################
#### REFRACTIVE INDEX EXTENTION -- 23/04/2021
##############################################
##############################################
##############################################
@app.route('/refrac_index', defaults={'page': 1})
@app.route('/page/<int:page>')
def refrac_index(page):
  #Remove files created in Kramers-Kroning tool if they exist
  DIR = os.getcwd() + '/'
  import shutil
  if os.path.isdir(DIR + 'application/uploads/') == True:
    shutil.rmtree(DIR + 'application/uploads/')
  else:
    pass
  
  if os.path.isdir(DIR + 'Cont_test/') == True:
    shutil.rmtree(DIR + 'Cont_test/')
  else:
    pass
  
  try:
    os.remove('Test_continuum.txt')
  except FileNotFoundError:
    pass
  
  try:
    os.remove('Test_append.txt')
  except FileNotFoundError:
    pass
  
  try:
    os.remove('Requested_continuum.txt')
  except FileNotFoundError:
    pass

  ###########################################################

  searchword = request.args.get('q')
  if searchword:
    n_analogues = N_Analogue.query.filter(
      and_(N_Analogue.name.like('%' + word + '%') for word in searchword.split()))
    #analogues = Analogue.query.filter(Analogue.name.like('%' + searchword + '%'))
  else:
    n_analogues = N_Analogue.query
  n_analogues = n_analogues.paginate(page, app.config['ANALOGUES_PER_PAGE'], True)

  n_stats = {
    'n_analogues_count': N_Analogue.query.count(),
    'n_spectra_count': N_optc.query.count()
  }
  return render_template('refrac_index.jade', n_analogues=n_analogues, n_stats=n_stats, q=searchword)


@app.route('/data_opt_const/<int:n_analogue_id>', methods=['GET'])
def n_analogue_show(n_analogue_id):
  #print('Doing n_analogue_show', n_analogue_id)
  n_analogue = N_Analogue.query.get(n_analogue_id)
  temperatures = sorted([s.temperature for s in n_analogue.n_val])
  t = [str(t) for t in temperatures]
  n_val = db.session.query(N_optc).filter_by(n_analogue_id=n_analogue.id).order_by(N_optc.temperature)

  """print('==============================================')
  print('TMP:', temperatures)
  print('---------------------------------------------')
  print('t is:', t)
  print('---------------------------------------------')
  print('n_analogue:', n_analogue)
  print('---------------------------------------------')
  print('n_val is:', n_val)
  print('==============================================')"""


  DIR = os.getcwd() + '/'

  con = sqlite3.connect(DIR+'application/db/dbn.db')
  cur = con.cursor()
  all_analogues = []
  all_spectrum = []
  for row in cur.execute('SELECT * FROM n_val'):
    #print('reading dbn database...')
    #print(row[0], row[1])
    all_analogues.append(row[1])
    all_spectrum.append(row[0])
    #print("--------------------------------------")
  
  #print('All_analogues are:', all_analogues)
  #print('All_spectrum are:', all_spectrum)
  
  from bokeh.palettes import Spectral3
  spec_idx_list = []
  for i,j in zip(range(len(all_analogues)), range(len(all_analogues))):
    if all_analogues[i] == n_analogue_id:
      spec_idx_list.append(all_spectrum[j])


  def temperatureRGB(minimum, maximum, value):
    x = (value - minimum) / (maximum - minimum)
    return int(255*x),int(0), int(255*(1-x))
  
  colours = []
  for t_ind in range(len(temperatures)):
    if len(temperatures) == 1:
      color = RGB(r = 255, g = 0, b = 0)
      colours.append(color)
    elif len(temperatures) == 2:
      color = RGB(r = 255, g = 0, b = 0)
      colours.append(color)
    else:
      cc = temperatureRGB(min(temperatures),max(temperatures),temperatures[t_ind])
      color = RGB(r = cc[0], g = cc[1], b = cc[2])
      colours.append(color)
  
  p = figure(plot_height=300, sizing_mode='scale_width')
  
  miny = []
  maxy = []
  for idx, temp, color in zip(range(len(spec_idx_list)), t, colours):
    #print('reading idx:', idx)
    val = n_spectrum_show_json(spec_idx_list[idx])
    miny.append(min(val[1]))
    maxy.append(max(val[1]))
    source = ColumnDataSource(data=dict(x=val[0], y=val[1]))
    p.line('x', 'y', source = source, line_width=2, color=color, line_alpha=1.0, hover_color=color, hover_alpha=1.0, hover_width=5,
           muted_color=color, muted_alpha=0.2, legend_label=temp+'K')
      
    
  TOOLTIPS = """
  <div>
      <div>
          <span style="font-size: 18px;">Location</span>
          <span style="font-size: 18px; color: #696;">($x, $y)</span>
      </div>
  </div>"""
  
  
  p.add_tools(HoverTool(show_arrow=True, line_policy='interp', tooltips=TOOLTIPS))
  p.add_tools(CrosshairTool(line_color='grey', line_width=0.5))
  
  p.legend.location = "top_right"
  p.legend.label_text_font_size="16px"
  p.legend.click_policy="mute"
  p.x_scale = LogScale()
  p.xaxis.axis_label = 'Wavenumber (cm⁻¹)'
  p.xaxis.axis_label_text_font_style = "normal"
  p.xaxis.axis_label_text_font_size = '20px'
  p.yaxis.axis_label = 'Refractive index'
  p.yaxis.axis_label_text_font_style = "normal"
  p.yaxis.axis_label_text_font_size = '20px'
  p.y_range=Range1d(start = min(miny) - 0.1*min(miny), end = max(maxy)+0.1*max(maxy))
  p.x_range=Range1d(start = max(val[0]), end = min(val[0]))
  p.yaxis.major_label_text_font_size = '16px'
  p.xaxis.major_label_text_font_size = '16px'
  p.add_layout(LinearAxis(major_label_text_font_size = '1px'), 'right')
  #p.xaxis.ticker = [400, 500, 600, 700, 800, 1000, 1400, 1800, 2000, 3000, 4000, 5000]
  

  #p.x_scale = LinearScale()
  p.extra_x_ranges = {"x_mic": Range1d(1e4/max(val[0]), 1e4/min(val[0]))}
  top_axis = LogAxis(x_range_name = "x_mic", axis_label="Wavelength (μm)", axis_label_text_font_style='normal', axis_label_text_font_size='20px', major_label_text_font_size = '16px')
  p.add_layout(top_axis, 'above')


  
  script, div = components(p)

  return render_template(
          'N_showbkjs.jade',
          n_analogue=n_analogue,
          n_val=n_val,
          plot_script=script,
          plot_div=div,
          js_resources=INLINE.render_js(),
          css_resources=INLINE.render_css(),
      ).encode(encoding='UTF-8')


def split(arr, cond):
  return [arr[cond], arr[~cond]]


@app.route('/spectrum_nval/<int:spectrum_id>.json', methods=['GET'])
def n_spectrum_show_json(spectrum_id):
  print('Doing n_spectrum_show_json', spectrum_id)
  spectrum_nval = N_optc.query.get(spectrum_id)
  #n_val = db.session.query(N_optc).filter_by(n_analogue_id=n_analogue.id).order_by(N_optc.temperature)
  # Slice data to fewer samples to increase performance
  data = spectrum_nval.n_read_h5()
  
  
  data = data[::round(len(data)/1000)]
  #print('data here II is:', data)

  # Signal often starts with instrument noise (wavenumber < 500), cut that out
  parts = split(data, data[:,0] < 500)
  noise = parts[0]
  average = numpy.average(parts[1][:,1])
  maximum_distance = abs(average * 1.5)
  parts[0] = noise[abs(noise[:,1]-average) < maximum_distance]
  data = numpy.concatenate(parts)

  dataX = data[:,0]
  dataY = data[:,1]
  
  
  """print('==============================================')
  print('spectrum_nval:', spectrum_nval)
  print('---------------------------------------------')
  print('data after:', data)
  print('---------------------------------------------')
  #print('parts:', parts)
  print('---------------------------------------------')
  #print('noise:', noise)
  print('---------------------------------------------')
  #print('average:', average)
  print('==============================================')"""

  return dataX, dataY
  #data=data.tolist()
  #return data
  #return jsonify(temperature=spectrum_nval.temperature, data=data.tolist())

@app.route('/spectrum_nval/download/<int:spectrum_id>/<string:n_download_filename>.txt.gz', methods=['GET'])
def n_spectrum_download_gz(spectrum_id, n_download_filename):
  spectrum_nval = N_optc.query.get(spectrum_id)
  return send_file(spectrum_nval.n_gz_file_path(), mimetype='application/x-gzip')


@app.route('/spectrum_nval/download/<int:spectrum_id>/<string:n_download_filename>.txt', methods=['GET'])
def n_spectrum_download_txt(spectrum_id, n_download_filename):
  spectrum_nval = N_optc.query.get(spectrum_id)
  with gzip.open(spectrum_nval.n_gz_file_path(), 'r') as f:
    data = f.read()
  mimetype = 'text/plain'
  rv = app.response_class(data, mimetype=mimetype, direct_passthrough=True)
  return rv


@app.route('/spectrum_nval/download/<int:n_analogue_id>.tar.gz', methods=['GET'])
def n_analogue_download_all_txt(analogue_id):
  n_val = N_Analogue.query.get(n_analogue_id).n_val
  stream = io.BytesIO()
  with tarfile.open(mode='w:gz', fileobj=stream) as tar:
    for spectrum_nval in n_val:
      with gzip.open(spectrum_nval.n_gz_file_path(), 'r') as f:
        buff = f.read()
        tarinfo = tarfile.TarInfo(name=str(spectrum_nval.temperature)+'K.txt')
        tarinfo.size = len(buff)
        tar.addfile(tarinfo=tarinfo, fileobj=io.BytesIO(buff))
  data = stream.getvalue()
  mimetype = 'application/x-tar'
  rv = app.response_class(data, mimetype=mimetype, direct_passthrough=True)
  return rv



@app.route('/n_analogue/<int:n_analogue_id>.json', methods=['GET'])
def n_analogue_show_json(n_analogue_id):
  n_analogue = N_Analogue.query.get(n_analogue_id)

  # Annotate important wavenumbers
  n_annotations = {}



  #if '{H2O}' in analogue.name:
  #  annotations['H2O stretch'] =   3250 # cm-1
  #  annotations['H2O bending'] =   1700
  #  annotations['H2O libration'] = 770

  #if '{HCOOH}' in analogue.name:
  #  annotations['C=O stretch'] =   1714

  return jsonify(
    n_val=sorted([s.id for s in n_analogue.n_val]),
    n_annotations=n_annotations)




@app.route('/admin/Statistics', methods=['GET'])
def stats():
  from bokeh.io import output_file, show
  from bokeh.plotting import figure
  from bokeh.models.tools import SaveTool

  import glob

  DIR = os.getcwd() + '/'
  files = sorted(glob.glob(DIR+'Statistics/*.txt'))
  #downloads = '/Users/willrocha/T0/ice-database/Statistics/counter_download_tar_gz.dat'

  months = []
  counter = []
  years = []
  for m in range(len(files)):
    print(files[m])
    month = files[m].split('_')[1]
    year = files[m].split('_')[2].split('.')[0]
    print(month,year)
    months.append(month+'_'+year)
    n = np.loadtxt(files[m], dtype=str, usecols=(0)).T
    counter.append(len(n.tolist()))
    years.append(year)


  import pandas as pd

  df = pd.DataFrame({
  'col1': months,
  'col2': years,
  'col3': counter
  })

  from natsort import index_natsorted
  df2 = df.sort_values(
     by="col1",
     key=lambda x: np.argsort(index_natsorted(df["col1"]))
  )

  output_file("bars.html")
  months = df2['col1']
  counts = df2['col3']

  p = figure(plot_height=300, plot_width = 1100, sizing_mode='fixed', x_range=months, title="LID accesses per month",
             toolbar_location="right", tools="")

  p.vbar(x=months, top=counts, width=0.2, color='blue')

  p.xgrid.grid_line_color = None
  p.y_range.start = 0
  p.add_tools(HoverTool(tooltips=[("Nr accesses:", "@top")]))
  save = SaveTool()
  tools = save
  p.add_tools(tools)
  p.title.text_font_size = '20pt'
  p.xaxis.major_label_text_font_size = '20px'
  p.yaxis.major_label_text_font_size = '20px'


  
  
  df_sum = df2.groupby(['col2'])['col3'].agg('sum')
  y = df_sum.reset_index()["col2"]
  tot_y = df_sum

  p2 = figure(plot_height=300, plot_width = 1100, x_range=y, title="LID accesses per year",
             toolbar_location="right", tools="")

  p2.vbar(x=y, top=tot_y, width=0.2, color='green')

  p2.xgrid.grid_line_color = None
  p2.y_range.start = 0
  p2.add_tools(HoverTool(tooltips=[("Nr accesses:", "@top")]))
  save = SaveTool()
  tools = save
  p2.add_tools(tools)
  p2.title.text_font_size = '20pt'
  p2.xaxis.major_label_text_font_size = '20px'
  p2.yaxis.major_label_text_font_size = '20px'

  downloads = DIR+'Statistics/counter_download_tar_gz.dat'
  down = np.loadtxt(downloads, dtype=str, usecols=(0)).T
  down_n = np.loadtxt(downloads, dtype=int, usecols=(1)).T


  df_down = pd.DataFrame({
  'col1': down,
  'col2': down_n
  })

  df_down_sum = df_down.groupby(['col1'])['col2'].agg('sum')
  yval = df_down_sum.reset_index()["col1"]
  tot_yval = df_down_sum

  p3 = figure(plot_height=300, plot_width = 1100, x_range=yval, title="Number of downloads per analogue",
             toolbar_location="right", tools="")

  p3.vbar(x=yval, top=tot_yval, width=0.2, color='purple')

  p3.xgrid.grid_line_color = None
  p3.y_range.start = 0
  p3.add_tools(HoverTool(tooltips=[("Nr downloads:", "@top")]))
  s3ve = SaveTool()
  t3ols = save
  p3.add_tools(tools)
  p3.title.text_font_size = '20pt'
  p3.xaxis.major_label_text_font_size = '20px'
  p3.yaxis.major_label_text_font_size = '20px'


  #show(p)
  content = column(layout([p,p2,p3]), height=650)
  script, div = components(content)

  #inp_column = column(toggle)
  #layout_row = row([inp_column, p])

  return render_template(
          '/admin/index_stats.jade',
          plot_script=script,
          plot_div=div,
          js_resources=INLINE.render_js(),
          css_resources=INLINE.render_css(),
      ).encode(encoding='UTF-8')


