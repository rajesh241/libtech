from bs4 import BeautifulSoup
import datetime
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
  parser.add_argument('-cb', '--createBroadcast', help='Create Broadcast', required=False, action='store_const', const=1)
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
  query="select f.districtName,f.blockName,f.fpsName,f.village,fs.year,fs.month,DATE_FORMAT(fs.deliveryDate,'%d/%m/%Y') deliveryDate,f.totalNumbers,fs.fpsCode,fs.audioPresent from fpsShops f, fpsStatus fs where f.cRequired=1 and f.fpsCode=fs.fpsCode order by fs.deliveryDate DESC limit 100"
  queryTable=bsQuery2Html(cur,query)
  myhtml+="<h2><a href='./fps.csv'> Download CSV </a></h2>"
  myhtml+=queryTable
  myhtml=htmlWrapperLocal(title="PDS Report", head='<h1 aling="center">Panchayats Reports</h1>', body=myhtml)
  writeFile(filename,myhtml)
  logger.info("CSV FILE Name: %s " % csvname)
  query="select f.districtName,f.blockName,f.fpsName,f.village,fs.year,fs.month,DATE_FORMAT(fs.deliveryDate,'%d/%m/%Y') deliveryDate,fs.fpsCode from fpsShops f, fpsStatus fs where f.cRequired=1 and f.fpsCode=fs.fpsCode order by fs.deliveryDate DESC "
  writecsv(cur,query,csvname)

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors

def getPDSAudioList(fpsCode,month):
  db = dbInitialize(db=pdsDB,host=pdsDBHost, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  query="select districtName from fpsShops where fpsCode='%s' " % fpsCode
  cur.execute(query)
  districtName=''
  error=0
  if cur.rowcount == 1:
    row=cur.fetchone()
    districtName=row[0]
  else:
    error=1
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  db = dbInitialize(db='libtech', charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  if districtName=='Gaya':
    audioLanguage='gaya'
  elif districtName=='Munger':
    audioLanguage='maithili'
  elif districtName=='Saharsa':
    audioLanguage='maithili'
  elif districtName=='Sitamarhi':
    audioLanguage='sitamarhi'
  else:
    audioLanguage='maithili'
    error=1

  if month < 10:
    monthString='bihar0'+str(month)
  elif month > 12:
    error=1
    monthString='bihar'+str(month)
  else:
    monthString='bihar'+str(month)
  audioList=[audioLanguage+'_0',monthString,audioLanguage+'_1',str(fpsCode),audioLanguage+'_2',monthString,audioLanguage+'_3',str(fpsCode),audioLanguage+'_4']
  likeString='%biharPDS%'
  audioIDs=''
  for audioFile in audioList:
    query="select id from audioLibrary where name='%s' and filename like '%s' " % (audioFile,likeString)
    cur.execute(query)
    if cur.rowcount > 0:
      row=cur.fetchone()
      audioIDs+=str(row[0])
      audioIDs+=','
    else:
      error=1
  audioIDs=audioIDs.rstrip(',')
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  if error == 1:
    return None
  else:
    return audioIDs

def createPDSBroadcast(logger):
  logger.info("Creating PDS Broadcast")
  db = dbInitialize(host=pdsDBHost,db=pdsDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  monthLabels=['0','JAN','FEB','MAR','APR','MAY','JUNE','JULY','AUG','SEP','OCT','NOV','DEC']
  query="select fs.id,f.districtName,f.blockName,f.village,fs.fpsCode,fs.month,fs.year from fpsShops f, fpsStatus fs where f.fpsCode=fs.fpsCode and fs.initiateBroadcast=1"
  cur.execute(query)
  results=cur.fetchall()
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  db = dbInitialize(db='libtech', charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  for row in results:
    [rowid,districtName,blockName,village,fpsCode,month,year] = row
    monthName=monthLabels[month]
    broadcastName="%s_%s_%s_%s_%s_%s" % (str(rowid),districtName,blockName,village,monthName,year)
    logger.info("Broadcast Name: %s " % broadcastName)
    broadcastType='biharPDS'
    vendor='any'
    todayPlus3=datetime.date.fromordinal(datetime.date.today().toordinal()+3)
    endDate=todayPlus3.strftime("%Y-%m-%d")
    audioFiles=getPDSAudioList(fpsCode,month)
    region='adri'
    template='general'
    query="insert into broadcasts (name,type,vendor,startDate,endDate,fileid,region,template) values ('%s','%s','%s',NOW(),'%s','%s','%s','%s')" % (broadcastName,broadcastType,vendor,endDate,audioFiles,region,template) 
    logger.info(query)
    cur.execute(query)
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
  if args['createBroadcast']:
    createPDSBroadcast(logger)

  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
