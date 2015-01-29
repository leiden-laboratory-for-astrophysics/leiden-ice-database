from flask.ext import admin, login
from flask.ext.admin.form import FileUploadField
from flask.ext.admin.form.rules import Macro
from flask.ext.admin.form import rules
from wtforms.fields import SelectField
from jinja2 import Markup

from application import app, db, data_path
from application.auth import AuthModelView, AdminHomeView
from application.models import *
from application.worker import *


class AnalogueAdmin(AuthModelView):
  form_rules = [Macro('m.tex_expl'), 'name', Macro('m.tex_preview'),
    'description', 'author', 'DOI']
  column_exclude_list = ['user', 'description']
  column_labels = dict(DOI='Paper DOI', author='First author')
  column_formatters = dict(DOI= lambda v, c, m, p:
      Markup('<a href="'+m.DOI_url()+'" target="_blank">'+m.DOI+'</a>'))
  form_excluded_columns = ('user', 'pub_date')

  def on_model_change(self, form, model):
    model.user_id = login.current_user.get_id()
    return model


class SpectrumAdmin(AuthModelView):
  column_exclude_list = ['description']
  column_labels = dict(temperature='Temperature (K)')
  column_formatters = dict(
      temperature= lambda v, c, m, p:
        int(m.temperature) if m.temperature.is_integer() else m.temperature,
      resolution=  lambda v, c, m, p: "%.2f" % m.resolution)
  form_rules = ['analogue', 'temperature', Macro('m.category'), 'category',
    Macro('m.tex_expl'), 'description', Macro('m.data_instr'), 'path']

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
  category=dict(
    choices=[(0, 'Warm-up'), (1, 'Exposure time'), (2, 'Other')]
  ))



admin = admin.Admin(app,
  base_template='admin/layout.jade', template_mode='bootstrap3',
  index_view=AdminHomeView(
    name='Laboratory Ice Database',
    template='admin/index.jade'
  )
)

admin.add_view(AnalogueAdmin(Analogue, db.session))
admin.add_view(SpectrumAdmin(Spectrum, db.session))
