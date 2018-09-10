import logging




def libtechLoggerFetch(level=None,filename=None):
  defaultLogLevel="info"
  logFormat = '%(asctime)s:[%(name)s|%(module)s|%(funcName)s|%(lineno)s|%(levelname)s]: %(message)s' #  %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s"
  logger = logging.getLogger(__name__)

  if not level:
    level = defaultLogLevel
  
  if level:
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
      raise ValueError('Invalid log level: %s' % level)
    else:
      logger.setLevel(numeric_level)
  ch = logging.StreamHandler()
  formatter = logging.Formatter(logFormat)
  ch.setFormatter(formatter)
  logger.addHandler(ch)

# logging.basicConfig(
#    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
#    handlers=[
#    logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
#    logging.StreamHandler()
#   ])
  # create console handler and set level to debug

  # create formatter e.g - FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'

  # add formatter to ch

  # add ch to logger

  return logger


