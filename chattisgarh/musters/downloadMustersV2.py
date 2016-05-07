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
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery,getFullFinYear
from globalSettings import datadir,nregaDataDir

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  #This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)

  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)

  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString=" limit 10000 "
  infinyear=args['finyear']
  districtName=args['district']
 
  logger.info("DistrictName "+districtName)
  logger.info("Fin year "+infinyear)

#Query to get all the blocks
  query="use libtech"
  cur.execute(query)
  query="select crawlIP from crawlDistricts where name='%s'" % districtName.lower()
  crawlIP=singleRowQuery(cur,query)
  query="select state from crawlDistricts where name='%s'" % districtName.lower()
  stateName=singleRowQuery(cur,query)
  logger.info("crawlIP "+crawlIP)
  logger.info("State Name "+stateName)
  query="use %s" % districtName.lower()
  cur.execute(query)
 
  musterfilepath=datadir+districtName.upper()+"/"
  musterfilepath=nregaDataDir.replace("stateName",stateName.title())+"/"+districtName.upper()+"/"
#Change the districtName to input district
  query="use %s " % (districtName.lower())
  cur.execute(query)

#Main Muster Query

  query="select b.name,p.name,m.musterNo,m.stateCode,m.districtCode,m.blockCode,m.panchayatCode,m.finyear,m.musterType,m.workCode,m.workName,DATE_FORMAT(m.dateFrom,'%d/%m/%Y'),DATE_FORMAT(m.dateTo,'%d/%m/%Y'),m.id from musters m,blocks b, panchayats p where b.isRequired=1 and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isRequired=1 and m.finyear='"+infinyear+"' and m.isError=0 and m.musterType='10' and (m.isDownloaded=0 or (m.isComplete=0 and TIMESTAMPDIFF(HOUR, m.downloadAttemptDate, now()) > 48 ) )  order by TIMESTAMPDIFF(DAY, m.downloadAttemptDate, now()) desc %s;" % (limitString)
#  query="select b.name,p.name,m.musterNo,m.stateCode,m.districtCode,m.blockCode,m.panchayatCode,m.finyear,m.musterType,m.workCode,m.workName,DATE_FORMAT(m.dateFrom,'%d/%m/%Y'),DATE_FORMAT(m.dateTo,'%d/%m/%Y'),m.id from musters m,blocks b, panchayats p where b.isActive=1 and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isActive=1 and m.id=1"
  logger.info("Query: "+query)
  #cur.execute(query)
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    blockName=row[0]
    panchayatName=row[1]
    panchayatNameOnlyLetters=re.sub(r"[^A-Za-z]+", '', panchayatName)
    musterNo=row[2]
    stateCode=row[3]
    districtCode=row[4]
    blockCode=row[5]
    panchayatCode=row[6]
    finyear=row[7]
    musterType=row[8]
    workCode=row[9]
    workName=row[10].decode("UTF-8")
    dateTo=row[12]
    dateFrom=row[11]
    musterid=row[13]
    fullPanchayatCode=stateCode+districtCode+blockCode+panchayatCode
    fullBlockCode=stateCode+districtCode+blockCode
    fullDistrictCode=stateCode+districtCode
    worknameplus=workName.replace(" ","+")
    datetostring = str(dateTo)
    datefromstring = str(dateFrom)
   
    fullfinyear=getFullFinYear(finyear)

    musterURL="http://%s/netnrega/citizen_html/musternew.aspx?state_name=%s&district_name=%s&block_name=%s&panchayat_name=%s&workcode=%s&panchayat_code=%s&msrno=%s&finyear=%s&dtfrm=%s&dtto=%s&wn=%s&id=1" % (crawlIP,stateName.upper(),districtName.upper(),blockName.upper(),panchayatName,workCode,fullPanchayatCode,musterNo,fullfinyear,datefromstring,datetostring,worknameplus)
    logger.info("%s   %s   %s   %s   %s" %(districtName,blockName,panchayatName,fullfinyear,musterNo))
    logger.info("MusterURL "+musterURL)
    r=requests.get(musterURL)
    #Irrespective of result of download lets set downloadAttemptDate
    query="update musters set downloadAttemptDate=NOW() where id="+str(musterid)
    cur.execute(query)


    mustersource=r.text
    myhtml=mustersource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    myhtml1=re.sub(regex,"",myhtml)
    htmlsoup=BeautifulSoup(myhtml1)
  #  table=htmlsoup.find('table',bordercolor="#458CC0")
    try:
      table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
      rows = table.findAll('tr')
      errorflag=0
      #print "There is not ERROR here"
    except:
      errorflag=1
      logger.info("MusterDownloadError Could not fin table")
      #print "Cannot find the table"
    if errorflag==0:
      logger.info("MusterDownloadSuccess Updating the Status")
     # print "error is zero"
      musterfilename=musterfilepath+blockName+"/"+panchayatNameOnlyLetters.upper()+"/MUSTERS/"+fullfinyear+"/"+musterNo+".html"
      logger.info("MusterFileName" +musterfilename)
      if not os.path.exists(os.path.dirname(musterfilename)):
        os.makedirs(os.path.dirname(musterfilename))
      f = open(musterfilename, 'w')
      f.write(myhtml1.encode("UTF-8"))
      try:
        query="update musters set isProcessed=0,isDownloaded=1,downloadDate=NOW() where id="+str(musterid)
        logger.info("Update Query : "+ query)
       # print query
        #cur.execute(query)
        cur.execute(query)
      except MySQLdb.IntegrityError,e:
        errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
      #  errorfile.write(errormessage)
    logger.info("***************")
    logger.info("***************")
 



 
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
