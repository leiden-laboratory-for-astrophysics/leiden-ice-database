from flask_admin import Admin
from flask_login import LoginManager
from flask_login import login_user, logout_user, current_user
from flask_admin.form import FileUploadField
from flask_admin.form.rules import Macro
from flask_admin.form import rules
from wtforms.fields import SelectField
from jinja2 import Markup

from application import app, db, data_path, data_path_optc, data_path_annot, data_path_sc
from application.auth import AuthModelView, AdminHomeView
from application.models import *
from application.worker import *


class AnalogueAdmin(AuthModelView):
  form_rules = [Macro('m.tex_expl'), 'name', 'name2', 'name3', 'name4', 'name5', Macro('m.tex_preview'),
    'deposition_temperature', 'description', 'author', 'DOI', 'path_annot']
  column_exclude_list = ['user', 'description']
  column_labels = dict(name2='Second name', name3='Third name', name4='Fourth name', name5='Fifth name', DOI='Paper DOI', author='First author', path_annot='Annotation')
  column_formatters = dict(DOI= lambda v, c, m, p:
      Markup('<a href="'+m.DOI_url()+'" target="_blank">'+m.DOI+'</a>'))
  form_excluded_columns = ('user', 'pub_date')

  def on_model_change(self, form, model, is_created=True):
    model.user_id = current_user.get_id()
    return model

  form_extra_fields= {
    'path_annot': FileUploadField('Annotation file', base_path=data_path_annot,
    allowed_extensions=['csv'])
  }


class SpectrumAdmin(AuthModelView):
  column_exclude_list = ['description']
  column_labels = dict(temperature='Temperature (K)')
  column_formatters = dict(
      temperature= lambda v, c, m, p:
        int(m.temperature) if m.temperature.is_integer() else m.temperature)
      #resolution=  lambda v, c, m, p: "%.2f" % m.resolution)
  form_rules = ['analogue', 'temperature', Macro('m.category'), 'category',
    Macro('m.exposure_time'), 'exposure_time', Macro('m.resolution'), 'resolution', Macro('m.column_density'), 'column_density', Macro('m.ice_thickness'), 'ice_thickness', Macro('m.tex_expl'),
    'description', Macro('m.data_instr'), 'path']

#  This method would set the uploaded data file name to a timestamp
#  def spectrum_filename(obj, file_data):
#    return secure_filename('%s.txt' % int(time.time()))

  form_extra_fields= {
    'path': FileUploadField('Data file', base_path=data_path,
    allowed_extensions=['asc', 'dat', ''])
  }
  

  form_overrides = dict(category=SelectField)
  form_args = dict(
    # Pass the choices to the `SelectField`
    category=dict(choices=Spectrum.CATEGORIES)
  )




class N_AnalogueAdmin(AuthModelView):
  form_rules = [Macro('m.tex_expl'), 'name', Macro('m.tex_preview'),
    'description', 'author', 'DOI']
  column_exclude_list = ['n_user', 'description']
  column_labels = dict(DOI='Paper DOI', author='First author')
  column_formatters = dict(DOI= lambda v, c, m, p:
      Markup('<a href="'+m.DOI_url()+'" target="_blank">'+m.DOI+'</a>'))
  form_excluded_columns = ('n_user', 'pub_date')

  def on_model_change(self, form, model, is_created=True):
    model.n_user_id = current_user.get_id()
    return model


class N_SpectrumAdmin(AuthModelView):
  column_exclude_list = ['description']
  column_labels = dict(temperature='Temperature (K)')
  column_formatters = dict(
      temperature= lambda v, c, m, p:
        int(m.temperature) if m.temperature.is_integer() else m.temperature,
      resolution=  lambda v, c, m, p: "%.2f" % m.resolution)
  form_rules = ['n_analogue', 'temperature', Macro('m.category'), 'category',
    Macro('m.exposure_time'), 'exposure_time', Macro('m.tex_expl'),
    'description', Macro('m.data_instr'), 'path']

#  This method would set the uploaded data file name to a timestamp
#  def spectrum_filename(obj, file_data):
#    return secure_filename('%s.txt' % int(time.time()))

  form_extra_fields= {
    'path': FileUploadField('Data file', base_path=data_path_optc,
    allowed_extensions=['asc', 'dat', ''])
  }
  

  form_overrides = dict(category=SelectField)
  form_args = dict(
    # Pass the choices to the `SelectField`
    category=dict(choices=N_optc.N_CATEGORIES)
  )


###

class SC_AnalogueAdmin(AuthModelView):
  form_rules = [Macro('m.tex_expl'), 'name', Macro('m.tex_preview'),
    'description', 'author', 'DOI']
  column_exclude_list = ['sc_user', 'description']
  column_labels = dict(DOI='Paper DOI', author='First author')
  column_formatters = dict(DOI= lambda v, c, m, p:
      Markup('<a href="'+m.DOI_url()+'" target="_blank">'+m.DOI+'</a>'))
  form_excluded_columns = ('sc_user', 'pub_date')

  def on_model_change(self, form, model, is_created=True):
    model.sc_user_id = current_user.get_id()
    return model


class SC_SpectrumAdmin(AuthModelView):
  column_exclude_list = ['description']
  column_labels = dict(temperature='Temperature (K)')
  column_formatters = dict(
      temperature= lambda v, c, m, p:
        int(m.temperature) if m.temperature.is_integer() else m.temperature,
      resolution=  lambda v, c, m, p: "%.2f" % m.resolution)
  form_rules = ['sc_analogue', 'temperature', Macro('m.category'), 'category',
    Macro('m.cont_model'), 'cont_model', Macro('m.tex_expl'),
    'description', Macro('m.data_instr'), 'path']

#  This method would set the uploaded data file name to a timestamp
#  def spectrum_filename(obj, file_data):
#    return secure_filename('%s.txt' % int(time.time()))

  form_extra_fields= {
    'path': FileUploadField('Data file', base_path=data_path_sc,
    allowed_extensions=['asc', 'dat', ''])
  }
  

  form_overrides = dict(category=SelectField)
  form_args = dict(
    # Pass the choices to the `SelectField`
    category=dict(choices=SC_spec.SC_CATEGORIES)
  )

###


admin = Admin(app,
  base_template='admin/layout.jade', template_mode='bootstrap3',
  index_view=AdminHomeView(
    name='Laboratory Ice Database',
    template='admin/index.jade'
  )
)

admin.add_view(AnalogueAdmin(Analogue, db.session))
admin.add_view(SpectrumAdmin(Spectrum, db.session))
admin.add_view(N_AnalogueAdmin(N_Analogue, db.session))
admin.add_view(N_SpectrumAdmin(N_optc, db.session))
admin.add_view(SC_AnalogueAdmin(SC_Object, db.session))
admin.add_view(SC_SpectrumAdmin(SC_spec, db.session))
