from application import app
import logging
from logging import Formatter
from logging.handlers import SMTPHandler

ADMINS = ['olsthoorn@strw.leidenuniv.nl']
if not app.debug:
  mail_handler = SMTPHandler('127.0.0.1',
                             'server-error@strw.leidenuniv.nl',
                             ADMINS, 'Ice Database Server Failed')
  mail_handler.setFormatter(Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
    '''))
  mail_handler.setLevel(logging.ERROR)
  app.logger.addHandler(mail_handler)
