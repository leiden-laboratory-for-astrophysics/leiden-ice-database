class Configuration(object):
  SQLALCHEMY_DATABASE_URI = 'sqlite:////vagrant/application/db/development.db'
  DEBUG = True
  SECRET_KEY = 'shhhh'
  MIXTURES_PER_PAGE = 20
