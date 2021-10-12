class Configuration(object):
  SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/willrocha/T0/ice-database/application/db/development.db'
  SQLALCHEMY_BINDS = {'n' : 'sqlite:////Users/willrocha/T0/ice-database/application/db/dbn.db',
                     'sc' : 'sqlite:////Users/willrocha/T0/ice-database/application/db/dbsc.db'}
  DEBUG = True
  SECRET_KEY = 'shhhh'
  ANALOGUES_PER_PAGE = 20
