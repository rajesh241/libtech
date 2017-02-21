from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../nrega/crawl/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
from bootstrap_utils import bsQuery2Html,htmlWrapperLocal
from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery,writecsv
from crawlFunctions import alterHTMLTables
from pdsFunctions import cleanFPSName,writeFile
from globalSettings import datadir,nregaDataDir
from pdsSettings import pdsDB,pdsDBHost,pdsRawDataDir,pdsWebDirRoot,pdsUIDir,pdsAudioDir
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Populate Pds SHop codes from csv File')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-m', '--month', help='Month for which PDS needs to be downloaded', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-wr', '--webReport', help='Generate Web Report', required=False, action='store_const', const=1)
  parser.add_argument('-cf', '--checkAudioFiles', help='Check if AudioFiles are present', required=False, action='store_const', const=1)
  parser.add_argument('-f', '--fpsCode', help='FPS shop for which data needs to be donwloaded', required=False)

  args = vars(parser.parse_args())
  return args

def checkAudioFiles(logger):
  logger.info("Checking if all AudioFiles are present or not")
  db = dbInitialize(host=pdsDBHost,db=pdsDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  query="select id,fpsCode from fpsShops where cRequired=1 order by id desc "
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    fpsCode=row[1]
    logger.info("row id: %s dpsCode: %s  " % (rowid,fpsCode))
    audioPresent=1
    fpsFileName="%s/fps/%s.wav" % (pdsAudioDir,fpsCode)
    if not os.path.isfile(fpsFileName):
      audioPresent=0
    logger.info("THe audioPresent : %s " % str(audioPresent))
    query="update fpsShops set audioPresent=%s where id=%s " % (str(audioPresent),rowid)
    cur.execute(query)
    query="update fpsStatus set audioPresent=%s where fpsCode=%s " % (str(audioPresent),fpsCode)
    cur.execute(query)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors

def genWebReport(logger):
  logger.info("Generating PDS Report")
  db = dbInitialize(host=pdsDBHost,db=pdsDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
 
  filename="%s/index.html" % (pdsUIDir)
  csvname="%s/fps.csv" % (pdsUIDir)
  myhtml=''
  query="select f.districtName,f.blockName,f.fpsName,f.village,fs.year,fs.month,DATE_FORMAT(fs.deliveryDate,'%d/%m/%Y') deliveryDate,f.totalNumbers,fs.fpsCode from fpsShops f, fpsStatus fs where f.cRequired=1 and f.fpsCode=fs.fpsCode order by fs.deliveryDate DESC limit 100"
  queryTable=bsQuery2Html(cur,query)
  myhtml+="<h2><a href='./fps.csv'> Download CSV </a></h2>"
  myhtml+=queryTable
  myhtml=htmlWrapperLocal(title="PDS Report", head='<h1 aling="center">Panchayats Reports</h1>', body=myhtml)
  writeFile(filename,myhtml)
  logger.info("CSV FILE Name: %s " % csvname)
  query="select f.districtName,f.blockName,f.fpsName,f.village,fs.year,fs.month,DATE_FORMAT(fs.deliveryDate,'%d/%m/%Y') deliveryDate,fs.fpsCode from fpsShops f, fpsStatus fs where f.cRequired=1 and f.fpsCode=fs.fpsCode order by fs.deliveryDate DESC "
  writecsv(cur,query,csvname)

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  if args['webReport']:
    genWebReport(logger)
  if args['checkAudioFiles']:
    checkAudioFiles(logger)

  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
