from flask.ext import admin, login
from flask.ext.admin.form import FileUploadField
from flask.ext.admin.form.rules import Macro
from flask.ext.admin.form import rules

from application import app, db, data_path
from application.auth import AuthModelView, AdminHomeView
from application.models import *
from application.worker import *
import time


class MixtureAdmin(AuthModelView):
  form_rules = [Macro('m.tex_expl'), 'name', Macro('m.tex_preview'),
    'description', 'author', 'author_email', 'spectra']
  column_exclude_list = ['user', 'description']
  form_excluded_columns = ('user', 'pub_date')

  def on_model_change(self, form, model):
    model.user_id = login.current_user.get_id()
    return model

class SpectrumAdmin(AuthModelView):
  column_exclude_list = ['description']
  column_labels = dict(temperature='Temperature (K)')
  form_rules = ['mixture', 'temperature', Macro('m.tex_expl'), 'description', 
    Macro('m.data_instr'), 'path']

  def spectrum_filename(obj, file_data):
    return secure_filename('%s.txt' % int(time.time()))

  form_extra_fields= {
    'path': FileUploadField('Data file', namegen=spectrum_filename,
      base_path=data_path, allowed_extensions=['asc', 'dat', ''])
  }


admin = admin.Admin(app,
  base_template='admin/layout.jade', template_mode='bootstrap3',
  index_view=AdminHomeView(
    name='Laboratory Ice Database',
    template='admin/index.jade'
  )
)

admin.add_view(MixtureAdmin(Mixture, db.session))
admin.add_view(SpectrumAdmin(Spectrum, db.session))
