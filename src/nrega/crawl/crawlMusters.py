import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
from libtechFunctions import singleRowQuery,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from crawlSettings import nregaDB 


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-fpc', '--fullPanchayatCode', help='Full PanchayatCode', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  args = argsFetch()
  finyear=args['finyear']
  additionalFilters=''
  fullfinyear=getFullFinYear(finyear)
  if args['fullPanchayatCode']:
    additionalFilters= " and fullPanchayatCode='%s' " % args['fullPanchayatCode']
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")


  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)


  query="select id,districtCode,crawlIP,stateCode from districts where isRequired=1 and stateName='JHARKHAND'"
#  query="select id,districtCode,crawlIP,stateCode from districts where isRequired=1 "
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    districtCode=row[1]
    crawlIP=row[2]
    stateCode=row[3]
    musterType='10'
    logger.info("DistrictCode: %s Crawl IP %s " % (districtCode,crawlIP))
    query="select stateName,blockCode,rawDistrictName,rawBlockName,rawPanchayatName,fullPanchayatCode,panchayatCode from panchayats where isRequired=1 and stateCode='%s' and districtCode='%s' %s order by id desc" % (stateCode,districtCode,additionalFilters)
    cur.execute(query)
    results1=cur.fetchall()
    for row1 in results1:
      stateName=row1[0]
      blockCode=row1[1]
      rawDistrictName=row1[2]
      rawBlockName=row1[3]
      rawPanchayatName=row1[4]
      fullPanchayatCode=row1[5]
      panchayatCode=row1[6]
      fullBlockCode=stateCode+districtCode+blockCode
      url="http://"+crawlIP+"/netnrega/state_html/emuster_wage_rep1.aspx?type="+str(musterType)+"&lflag=eng&state_name="+stateName+"&district_name="+rawDistrictName+"&block_name="+rawBlockName+"&panchayat_name="+rawPanchayatName+"&panchayat_code="+fullPanchayatCode+"&fin_year="+fullfinyear
      logger.info(url)
      try:
        r  = requests.get(url)
        error=0
      except requests.exceptions.RequestException as e:  # This is the correct syntax
        logger.info(e) 
        error=1
      if error==0:
        curtime = time.strftime('%Y-%m-%d %H:%M:%S')
        htmlsource=r.text
        htmlsource1=re.sub(regex,"",htmlsource)
        htmlsoup=BeautifulSoup(htmlsource1)
        try:
          table=htmlsoup.find('table',bordercolor="green")
          rows = table.findAll('tr')
          errorflag=0
        except:
          status=0
          errorflag=1
        if errorflag==0:
          for tr in rows:
            cols = tr.findAll('td')
            tdtext=''
            district= cols[1].string.strip()
            block= cols[2].string.strip()
            panchayat= cols[3].string.strip()
            worknameworkcode=cols[5].text
            if district!="District":
              emusterno="".join(cols[6].text.split())
              print emusterno
              datefromdateto="".join(cols[7].text.split())
              datefromstring=datefromdateto[0:datefromdateto.index("-")]
              datetostring=datefromdateto[datefromdateto.index("-") +2:len(datefromdateto)]
              if datefromstring != '':
                datefrom = time.strptime(datefromstring, '%d/%m/%Y')
                datefrom = time.strftime('%Y-%m-%d %H:%M:%S', datefrom)
              else:
                datefrom=''
              if datetostring != '':
                dateto = time.strptime(datetostring, '%d/%m/%Y')
                dateto = time.strftime('%Y-%m-%d %H:%M:%S', dateto)
              else:
                dateto=''
              #worknameworkcodearray=re.match(r'(.*)\(330(.*)\)',worknameworkcode)
              worknameworkcodearray=re.match(r'(.*)\('+stateCode+r'(.*)\)',worknameworkcode)
              if worknameworkcodearray is not None:
                workName=worknameworkcodearray.groups()[0]
                workCode=stateCode+worknameworkcodearray.groups()[1]
                logger.info(emusterno+" "+datefromstring+"  "+datetostring+"  "+workCode)
                query="select * from musters where finyear='%s' and fullBlockCode='%s' and musterNo='%s'" % (finyear,fullBlockCode,emusterno)
                cur.execute(query)
                if cur.rowcount == 0:
                  query="insert into musters (fullBlockCode,musterNo,stateCode,districtCode,blockCode,panchayatCode,musterType,finyear,workCode,workName,dateFrom,dateTo,crawlDate) values ('"+fullBlockCode+"','"+emusterno+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"','"+musterType+"','"+finyear+"','"+workCode+"','"+workName+"','"+datefrom+"','"+dateto+"',NOW())"
                  cur.execute(query)
          query="update panchayatStatus set musterCrawlDate=NOW() where fullPanchayatCode='%s' " % fullPanchayatCode
          cur.execute(query)
#   
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
               
