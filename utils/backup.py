#! /usr/bin/env python

import datetime
from time import strftime,strptime
from MySQLdb import IntegrityError

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from includes.settings import dbhost,dbuser,dbpasswd,sid,token


#######################
# Global Declarations
#######################

#DB_NAMES = ['libtechdbOD', ]
DB_NAMES = ['amritmahal', 'bombatbengaluru', 'dhruvrungta', 'homestay', 'innohub', 'innovationhub', 'iycn', 'jhatkaa', 'khulamanch', 'mtsequipment', 'nuvepro', 'paradigmshift', 'proto', 'protovillage', 'rajeev', 'rajeev_nuvepro', 'spokesandlenses', 'tactsys', 'twb', 'vidsmeco_iycn1', 'wakeupcleanup', 'wellnessunlimited', ]
DB_NAMES = ['libtech', 'mahabubnagar' ]


#############
# Functions
#############  

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for taking backup daily, weekly and monthly')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--type', help='Type of backup sql/archive/wordpress', required=False)
  parser.add_argument('-f', '--frequency', help='Frequncy of backup daily/weekly/monthly', required=False)
  parser.add_argument('-d', '--directory', help='Specify BACKUPs directory', required=False)
  parser.add_argument('-a', '--archive-directory', help='Specify directory to be archived', required=False)

  args = vars(parser.parse_args())
  return args

def sqlDump(logger, db, filename, compress=False):
  '''
  Create a compressed MySQL dump of the specified database
  '''
  filepath = os.path.dirname(filename)
  logger.info('filepath[%s]' % filepath)
  if not os.path.exists(filepath):
    os.makedirs(filepath)
    
  if compress:
    filename += '.gz'
    dumpcmd = "mysqldump -u " + dbuser + " -p" + dbpasswd + " " + db + " | gzip -c | cat > " + filename
  else:
    dumpcmd = "mysqldump -u " + dbuser + " -p" + dbpasswd + " " + db + " > " + filename
    
  logger.info("Executing [%s]" % dumpcmd)
  os.system(dumpcmd)

def fetchSuffix(frequency=None):
  '''
  Create a suffix based on the frequency
  '''
  if not frequency:
    #frequency = "weekly"
    return "$( date '+%Y-%m-%d_%H-%M-%S' )"

  if(frequency == "daily"):
    suffix=(strftime("%a")) # Day of week (Mon, Tue, etc)
  elif(frequency =="weekly"):
    day_of_month = datetime.datetime.now().day
    suffix = (day_of_month - 1) // 7 + 1 # Week of month (1-4 or 5)
  elif(frequency =="monthly"):
    suffix=(strftime("%b"))   # To get Jan, Feb, etc.

  return suffix

def archiveFolder(logger, archive_dir, filename, with_db_dump=False):
  '''
  Create a suffix based on the frequency
  '''
  parent_dir = os.path.dirname(archive_dir)
  logger.info('Current Directory[%s]' % os.getcwd())
  dirname = os.path.basename(archive_dir)
  logger.info("dirname[%s]" % dirname)

  if with_db_dump:
    db = dirname[:dirname.index('.')]
    logger.info('db[%s]' % db)
    dump_filename = archive_dir + '/DB_BACKUPs/' + db + '.sql'
    sqlDump(logger, db, dump_filename)

  dest_dir = os.path.dirname(filename)
  if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
    
  archive_cmd = 'cd ' + parent_dir + ' && ' + 'tar hcjf ' + filename + '.bz2 ' + dirname
  logger.info('archive_cmd[%s]' % archive_cmd)
  os.system(archive_cmd)

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")

  backup_type = args['type']
  backup_frequency = args['frequency']
  directory = args['directory']
  archive_directory = args['archive_directory']
  
  if not directory:
    directory = "./BACKUPs"

  filepath = os.path.abspath(directory) # Absolute Path needed for cd
  if backup_frequency:
    filepath += '/' + backup_frequency

  suffix = fetchSuffix(backup_frequency)
  logger.info("suffix[%s]" % suffix)

  if not archive_directory:
    for db in DB_NAMES:
      filename = db + '_' + str(suffix)

      sqlDump(logger, db, filepath + '/' + filename + '.sql', compress=True)
  else:
    dirname = os.path.basename(archive_directory)
    filename = filepath + '/' + dirname + '_' + str(suffix)
    if backup_type == 'archive':
      archiveFolder(logger, archive_directory, filename)
    else:
      archiveFolder(logger, archive_directory, filename, with_db_dump=True)
      
  logger.info("...END PROCESSING")
      
if __name__ == '__main__':
  main()
