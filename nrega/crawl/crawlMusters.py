import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
#This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
from libtechFunctions import singleRowQuery,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from crawlFunctions import getDistrictParams


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  #This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  districtName=args['district']
  districtList=[]
  if districtName=='all':
    logger.info("Need to run for all districts")
    db = dbInitialize(db="crawlDistricts", charset="utf8")  # The rest is updated automatically in the function
    cur=db.cursor()
    db.autocommit(True)
    query="select name from districts"
    cur.execute(query)
    results=cur.fetchall()
    for row in results:
      district=row[0]
      districtList.append(district)
    dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  else:
    districtList.append(districtName)

  for districtName in districtList:
    logger.info("Processing District %s " % districtName)
    db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
    cur=db.cursor()
    db.autocommit(True)
    #Query to set up Database to read Hindi Characters
    query="SET NAMES utf8"
    cur.execute(query)
    crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
   
   
    logger.info("DistrictName "+districtName)
    finyear=args['finyear']
    logger.info("finyear "+finyear)
   
    #Query to get all the blocks
    logger.info("crawlIP "+crawlIP)
    logger.info("State Name "+stateName)
   
    #Error File Defination
    errorfile = open('/tmp/crawlJobcards.log', 'w')
    #Connect to MySQL Database
    #muster Type list
    musterTypeList= ['10']
    fullfinyear=getFullFinYear(finyear)
    #Query to get all the blocks
    query="select stateCode,districtCode,blockCode,name from blocks where isRequired=1"
    #query="select stateCode,districtCode,blockCode,name from blocks where blockCode='002'"
    cur.execute(query)
    results = cur.fetchall()
    for row in results:
      stateCode=row[0]
      districtCode=row[1]
      blockCode=row[2]
      blockName=row[3]
      logger.info("Block Name "+blockName)
      query="select name,panchayatCode,id from panchayats where isChaupal=1 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
      query="select name,panchayatCode,id from panchayats where isRequired=1 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
      cur.execute(query)
      panchresults = cur.fetchall()
      for panchrow in panchresults:
        panchayatName=panchrow[0]
        panchayatCode=panchrow[1]
        fullPanchayatCode=stateCode+districtCode+blockCode+panchayatCode
        panchID=panchrow[2]
        print blockName+"  "+panchayatName
        logger.info("Block Name %s Panchayat %s" % (blockName,panchayatName))
        #We need to now run this for each musterType
        status=1 
        for musterType in musterTypeList:
          url="http://"+crawlIP+"/netnrega/state_html/emuster_wage_rep1.aspx?type="+str(musterType)+"&lflag=eng&state_name="+stateName+"&district_name="+districtName+"&block_name="+blockName+"&panchayat_name="+panchayatName+"&panchayat_code="+fullPanchayatCode+"&fin_year="+fullfinyear
          print url
          r  = requests.get(url)
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
                workName=worknameworkcodearray.groups()[0]
                workCode=stateCode+worknameworkcodearray.groups()[1]
                print emusterno+" "+datefromstring+"  "+datetostring+"  "+workCode
                query="insert into musters (musterNo,stateCode,districtCode,blockCode,panchayatCode,musterType,finyear,workCode,workName,dateFrom,dateTo,crawlDate) values ('"+emusterno+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"','"+musterType+"','"+finyear+"','"+workCode+"','"+workName+"','"+datefrom+"','"+dateto+"',NOW())"
                try:
                  cur.execute(query)
                except MySQLdb.IntegrityError,e:
                  errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
                  errorfile.write(errormessage)
                  continue
               
    dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
