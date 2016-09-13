import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import sys
import time
import re
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
from settings import dbhost,dbuser,dbpasswd
sys.path.insert(0, fileDir+'/../crawlDistricts/')
#Error File Defination
errorfile = open('/tmp/crawlfto.log', 'w')

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

  parser = argparse.ArgumentParser(description='Script for crawling FTOS, you need to pass finyear and district as arguments')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-f', '--finyear', help='Fin Years for which FTOs need to be downloaded', required=True)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)

  args = vars(parser.parse_args())
  return args


def updateFtoTable(cur,logger,url,blockCode,finyear,fullBlockCode,signatoryType):
  logger.info(url)
  r  = requests.get(url)
  htmlsource=r.text
  htmlsoup=BeautifulSoup(htmlsource,"html.parser")
  tables=htmlsoup.findAll('table')
  dateFormat="%d/%m/%Y"
  for table in tables:
    if "Financial Institution" in str(table):
      logger.info("Found the FTO Table")
      rows=table.findAll('tr')
      for row in rows:
        if "Financial Institution" in str(row):
          logger.info("This is a header Row")
        else:
          cols=row.findAll('td')
          ftoNo=cols[1].text.strip().replace(" ","")
          dateString=cols[3].text.strip().lstrip().rstrip()
          if fullBlockCode in ftoNo:#This will ensure only valid FTO get in to the database 
            query="select * from ftoDetails where ftoNo='%s' " % ftoNo
            cur.execute(query)
            logger.info(query)
            if cur.rowcount == 0:
              query="insert into ftoDetails (ftoNo,blockCode,finyear) values ('%s','%s','%s')" % (ftoNo,blockCode,finyear)
              cur.execute(query)
              logger.info(query)
            if "/" in dateString:#This will ensure that blank dates dont go intoour database
              query="update ftoDetails set %s=STR_TO_DATE('%s', '%s') where ftoNo='%s'" % (signatoryType,dateString,dateFormat,ftoNo)
              logger.info(query)
              cur.execute(query)


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  #This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)


  if args['district']:
    districtName=args['district']
 
  logger.info("DistrictName "+districtName)
  if args['finyear']:
    finyear=args['finyear']


  logger.info("finyear "+finyear)
  fullFinyear=getFullFinYear(finyear) 
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
#Query to get all the blocks

  query="select blockCode,name from blocks where isRequired=1"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    blockCode=row[0]
    blockName=row[1]
    fullBlockCode=stateCode+districtCode+blockCode
    fullDistrictCode=stateCode+districtCode
    logger.info(stateCode+districtCode+blockCode+blockName)
    url="http://"+crawlIP+"/netnrega/FTO/fto_reprt_detail.aspx?lflag=local&flg=W&page=b&state_name="+stateName.upper()+"&state_code="+stateCode+"&district_name="+districtName.upper()+"&district_code="+stateCode+districtCode+"&block_name="+blockName+"&block_code="+stateCode+districtCode+blockCode+"&fin_year="+fullFinyear+"&typ=pb&mode=b"
    url="http://%s/netnrega/FTO/fto_sign_detail.aspx?lflag=eng&flg=W&page=b&state_name=%s&state_code=%s&district_name=%s&district_code=%s&block_name=%s&block_code=%s&fin_year=%s&typ=fst_sig&mode=b" % (crawlIP,stateName.upper(),stateCode,districtName.upper(),fullDistrictCode,blockName.upper(),fullBlockCode,fullFinyear)
    updateFtoTable(cur,logger,url,blockCode,finyear,fullBlockCode,"firstSignatoryDate")
    #Following Code will update second Signatory Date     
    url="http://%s/netnrega/FTO/fto_sign_detail.aspx?lflag=eng&flg=W&page=b&state_name=%s&state_code=%s&district_name=%s&district_code=%s&block_name=%s&block_code=%s&fin_year=%s&typ=sec_sig&mode=b" % (crawlIP,stateName.upper(),stateCode,districtName.upper(),fullDistrictCode,blockName.upper(),fullBlockCode,fullFinyear)
    updateFtoTable(cur,logger,url,blockCode,finyear,fullBlockCode,"secondSignatoryDate")
#   for fto in htmlsoup.find_all('a'):
#     ftoNo=fto.contents[0]
#     #ftoURL="http://164.100.112.66/netnrega/FTO/"+fto.get('href')
#     if fullBlockCode in ftoNo:
#       query="insert into ftoDetails (ftoNo,stateCode,districtCode,blockCode,finyear) values ('"+ftoNo+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+finyear+"');"
#       try:
#         logger.info(query)
#         cur.execute(query)
#       except MySQLdb.IntegrityError,e:
#         errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
#         errorfile.write(errormessage)
#       continue
#  


if __name__ == '__main__':
  main()
