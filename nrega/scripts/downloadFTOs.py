import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import sys
import importlib
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
from nregaSettings import nregaRawDataDir
from libtechFunctions import writeFile,getFullFinYear,singleRowQuery
#Connect to MySQL Database
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from crawlFunctions import alterFTOHTML
from crawlFunctions import getDistrictParams
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
  finyear=args['finyear']
  
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  logger.info("finyear "+finyear)
  fullFinyear=getFullFinYear(finyear) 
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
#Query to get all the blocks



  ftorawfilepath=nregaRawDataDir.replace("districtName",districtName.lower())

  #ftorawfilepath=htmlRawDir+"/"+districtName.upper()+"/"
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
    tableHTML=''
    classAtt='id = "basic" class = " table table-striped"' 
    tableHTML+='<table %s">' % classAtt
    tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("District Name",districtName.upper())
    tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Block Name",blockName.upper())
    tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("FTO NO",ftono)
    logger.info(stateCode+districtCode+blockCode+blockName)
    fullfinyear=getFullFinYear(finyear)
    url="http://"+crawlIP+"/netnrega/FTO/fto_trasction_dtl.aspx?page=p&rptblk=t&state_code="+stateCode+"&state_name="+stateName.upper()+"&district_code="+fullDistrictCode+"&district_name="+districtName.upper()+"&block_code="+fullBlockCode+"&block_name="+blockName+"&flg=W&fin_year="+fullfinyear+"&fto_no="+ftono
    logger.info(str(ftoid)+"   "+fullfinyear+"  "+ftono)
    logger.info(url)
    #ftofilename=ftofilepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftono+".html"
    #logger.info(ftofilename)
    r=requests.get(url)
    inhtml=r.text
    ftorawfilename=ftorawfilepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftono+".html"
    writeFile(ftorawfilename,inhtml)
    query="update ftoDetails set isDownloaded=1 where id="+str(ftoid)
    cur.execute(query)
#   errorflag,outhtml=alterFTOHTML(inhtml)
#   if errorflag==0:
#     logger.info("FTO Download Success Updating the Status")
#     ftohtml=''
#     ftohtml+=tableHTML
#     ftohtml+=outhtml
#     ftohtml=htmlWrapperLocal(title="FTO Details", head='<h1 aling="center">'+ftono+'</h1>', body=ftohtml)
#     writeFile(ftofilename,ftohtml)
#     query="update ftoDetails set isDownloaded=1 where id="+str(ftoid)
#     cur.execute(query)


  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
