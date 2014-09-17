from flask import request, redirect, url_for
from flask.ext import login
from flask.ext.admin import helpers, expose, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from wtforms import form, fields, validators

from application import app, db
from application.models import User

class AuthModelView(ModelView):
  create_template = 'admin/create.html'
  edit_template = 'admin/edit.jade'

  def is_accessible(self):
    return login.current_user.is_authenticated()


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
  login = fields.TextField(validators=[validators.required()])
  password = fields.PasswordField(validators=[validators.required()])

  def validate_login(self, field):
    user = self.get_user()

    if user is None:
      raise validators.ValidationError('Invalid user')

    # we're comparing the plaintext pw with the the hash from the db
    if not user.check_password(self.password.data):
      raise validators.ValidationError('Invalid password')

  def get_user(self):
    return db.session.query(User).filter_by(username=self.login.data).first()


# Flask Admin integration
class AdminHomeView(AdminIndexView):
  @expose('/')
  def index(self):
    if not login.current_user.is_authenticated():
      return redirect(url_for('.login_view'))
    return super(AdminHomeView, self).index()

  @expose('/login/', methods=('GET', 'POST'))
  def login_view(self):
    # handle user login
    form = LoginForm(request.form)
    if helpers.validate_form_on_submit(form):
      user = form.get_user()
      login.login_user(user)

    if login.current_user.is_authenticated():
      return redirect(url_for('.index'))

    self._template_args['form'] = form
    return super(AdminHomeView, self).index()

  @expose('/logout/')
  def logout_view(self):
    login.logout_user()
    return redirect(url_for('.index'))
 

# Initialize flask-login
def init_login():
  login_manager = login.LoginManager()
  login_manager.init_app(app)

  # Create user loader function
  @login_manager.user_loader
  def load_user(user_id):
    return db.session.query(User).get(user_id)

init_login()
