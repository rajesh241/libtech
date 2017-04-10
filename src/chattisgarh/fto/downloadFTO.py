import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
from settings import dbhost,dbuser,dbpasswd,sid,token
from globalSettings import datadir,nregaDataDir
from libtechFunctions import getFullFinYear,singleRowQuery
#Connect to MySQL Database
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from crawlSettings import crawlIP,stateName,stateShortCode,districtCode
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for Downloading FTOs')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of ftos to be downloaded', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")

  limitString=''
  if args['limit']:
    limitString=' limit '+args['limit']
  if args['district']:
    districtName=args['district']
 
  logger.info("DistrictName "+districtName)
  if args['finyear']:
    finyear=args['finyear']
  else:
    finyear='16'
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  logger.info("finyear "+finyear)
  fullFinyear=getFullFinYear(finyear) 
#Query to get all the blocks



  ftofilepath=nregaDataDir.replace("stateName",stateName.title())+"/"+districtName.upper()+"/"
#ftofilepath="/home/libtech/libtechdata/CHATTISGARH/"+districtName+"/"
  query="select b.name,f.ftoNo,f.stateCode,f.districtCode,f.blockCode,f.finyear,f.id from ftoDetails f,blocks b where f.isDownloaded=0 and f.finyear='%s' and f.blockCode=b.blockCode and f.stateCode=b.stateCode and f.districtCode=b.districtCode  %s;" % (finyear,limitString)
  logger.info(query)
#query="select b.name,f.ftoNo,f.stateCode,f.districtCode,f.blockCode,f.finyear,f.id from ftoDetails f,blocks b where f.isDownloaded=0 and f.blockCode=b.blockCode and f.stateCode=b.stateCode and f.districtCode=b.districtCode and b.blockCode='003';"
  cur.execute(query)
  logger.info("Number of ftos to be downloaded is "+str(cur.rowcount))
  results = cur.fetchall()
  for row in results:
    blockName=row[0]
    ftono=row[1]
    stateCode=row[2]
    districtCode=row[3]
    blockCode=row[4]
    finyear=row[5]
    ftoid=row[6]
    fullBlockCode=stateCode+districtCode+blockCode
    fullDistrictCode=stateCode+districtCode
    logger.info(stateCode+districtCode+blockCode+blockName)
    fullfinyear=getFullFinYear(finyear)
    url="http://"+crawlIP+"/netnrega/FTO/fto_trasction_dtl.aspx?page=p&rptblk=t&state_code="+stateCode+"&state_name="+stateName.upper()+"&district_code="+fullDistrictCode+"&district_name="+districtName.upper()+"&block_code="+fullBlockCode+"&block_name="+blockName+"&flg=W&fin_year="+fullfinyear+"&fto_no="+ftono
    logger.info(str(ftoid)+"   "+fullfinyear+"  "+ftono)
    logger.info(url)
    ftofilename=ftofilepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftono+".html"
    logger.info(ftofilename)
    if not os.path.exists(os.path.dirname(ftofilename)):
      os.makedirs(os.path.dirname(ftofilename))
    r=requests.get(url)
    f = open(ftofilename, 'w')
    f.write(r.text)
    query="update ftoDetails set isDownloaded=1 where id="+str(ftoid)
    cur.execute(query)


  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
