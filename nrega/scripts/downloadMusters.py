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
from libtechFunctions import singleRowQuery,getFullFinYear,writeFile
from nregaSettings import nregaRawDataDir
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from crawlFunctions import alterMusterHTML,getMusterPaymentDate
from crawlFunctions import getDistrictParams
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)
  parser.add_argument('-b', '--blockCode', help='BlockCode for  which you need to Download', required=False)
  parser.add_argument('-p', '--panchayatCode', help='panchayatCode for  which you need to Download', required=False)
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
  regex1=re.compile(r'</td></font></td>',re.DOTALL)
  districtName=args['district']

  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)

  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString=" limit 10000 "
  additionalFilters = ''
  if args['blockCode']:
    additionalFilters=" and m.blockCode='%s' " % args['blockCode']
  if args['panchayatCode']:
    additionalFilters+=" and m.panchayatCode like '%"+args['panchayatCode']+"%' " 
  infinyear=args['finyear']
 
  logger.info("DistrictName "+districtName)
  logger.info("Fin year "+infinyear)

#Query to get all the blocks
  logger.info("crawlIP "+crawlIP)
  logger.info("State Name "+stateName)
  query="use %s" % districtName.lower()
  cur.execute(query)
 
 # musterfilepath=nregaDataDir.replace("stateName",stateName.title())+"/"+districtName.upper()+"/"
  musterrawfilepath=nregaRawDataDir.replace("districtName",districtName.lower())
  #musterrawfilepath=htmlRawDir+"/"+districtName.upper()+"/"
#Change the districtName to input district
  query="use %s " % (districtName.lower())
  cur.execute(query)

#Main Muster Query

  query="select count(*) from musters m,blocks b, panchayats p where b.isRequired=1 and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isRequired=1  and m.musterType='10' and (m.isDownloaded=0 or m.wdError=1 or (m.wdComplete=0 and TIMESTAMPDIFF(HOUR, m.downloadAttemptDate, now()) > 48 ) )  order by TIMESTAMPDIFF(DAY, m.downloadAttemptDate, now()) desc %s;" % (limitString)
  query="select b.name,p.name,m.musterNo,m.stateCode,m.districtCode,m.blockCode,m.panchayatCode,m.finyear,m.musterType,m.workCode,m.workName,DATE_FORMAT(m.dateFrom,'%d/%m/%Y'),DATE_FORMAT(m.dateTo,'%d/%m/%Y'),m.id,p.rawName from musters m,blocks b, panchayats p where b.isRequired=1 and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isRequired=1 and m.finyear='"+infinyear+"'  and m.musterType='10' and (m.isDownloaded=0 or m.wdError=1 or (m.wdComplete=0 and TIMESTAMPDIFF(HOUR, m.downloadAttemptDate, now()) > 48 ) ) %s order by TIMESTAMPDIFF(DAY, m.downloadAttemptDate, now()) desc %s;" % (additionalFilters,limitString)
#  query="select b.name,p.name,m.musterNo,m.stateCode,m.districtCode,m.blockCode,m.panchayatCode,m.finyear,m.musterType,m.workCode,m.workName,DATE_FORMAT(m.dateFrom,'%d/%m/%Y'),DATE_FORMAT(m.dateTo,'%d/%m/%Y'),m.id from musters m,blocks b, panchayats p where b.isActive=1 and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isActive=1 and m.id=1"
  logger.info("Query: "+query)
  #cur.execute(query)
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    blockName=row[0]
    panchayatName=row[14]
    musterNo=row[2]
    #stateCode=row[3]
    #districtCode=row[2]
    blockCode=row[5]
    panchayatCode=row[6]
    finyear=row[7]
    musterType=row[8]
    workCode=row[9]
    workName=row[10]
    dateTo=row[12]
    dateFrom=row[11]
    musterid=row[13]
    panchayatNameOnlyLetters=row[1]
    #re.sub(r"[^A-Za-z]+", '', panchayatName)
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
    htmlsoup=BeautifulSoup(myhtml1,"lxml")
  #  table=htmlsoup.find('table',bordercolor="#458CC0")
    try:
      table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
      rows = table.findAll('tr')
      errorflag=0
      #print "There is not ERROR here"
    except:
      errorflag=1
      logger.info("MusterDownloadError Could not find table")
      #print "Cannot find the table"
    if errorflag==0:
      musterrawfilename=musterrawfilepath+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/MUSTERS/"+fullfinyear+"/"+musterNo+".html"
      writeFile(musterrawfilename,myhtml)
      try:
        query="update musters set wdProcessed=0,wdError=0,isDownloaded=1,downloadDate=NOW() where id="+str(musterid)
        logger.info("Update Query : "+ query)
       # print query
        cur.execute(query)
        #cur.execute(query)
      except MySQLdb.IntegrityError,e:
        errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
        #  errorfile.write(errormessage)
      logger.info("***************")
      logger.info("***************")
 
#   myhtml1=re.sub(regex,"",myhtml)
#   myhtml2=re.sub(regex1,"</font></td>",myhtml1)
#   errorflag,outhtml=alterMusterHTML(myhtml2)
#   
#   if errorflag==0:
#     logger.info("MusterDownloadSuccess Updating the Status")
#     paymentDate,sanctionNo,sanctionDate=getMusterPaymentDate(myhtml2)
#     logger.info("Payment Date is %s " % paymentDate)
#     logger.info("Sanction No is %s " % sanctionNo)
#     logger.info("Sanction Date is %s " % sanctionDate)
#
#
#     tableHTML=''
#     classAtt='id = "basic" class = " table table-striped"' 
#     tableHTML+='<table %s">' % classAtt
#     tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("District Name",districtName.upper())
#     tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Block Name",blockName.upper())
#     tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Panchayat Name",panchayatName.upper())
#     tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Muster No",musterNo)
#     tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Work Code",workCode)
#     tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Work name",workName)
#     tableHTML+="<tr><th> %s </th><td id='sacntionNoTD'> %s </td></tr>" %("Sacntion No",sanctionNo)
#     tableHTML+="<tr><th> %s </th><td id='sactionDateTD'>%s </td></tr>" %("Sanction Date",sanctionDate)
#     tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Date From",datefromstring)
#     tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Date To",datetostring)
#     tableHTML+="<tr><th> %s </th><td id='paymentDateTD'> %s </td></tr>" %("Payment Date",paymentDate)
#     tableHTML+='</table>'
#
#
#     musterhtml=''
#     musterhtml+=tableHTML
#     musterhtml+=outhtml
#     musterhtml=htmlWrapperLocal(title="Muster Details", head='<h1 aling="center">'+musterNo+'</h1>', body=musterhtml)
#    # print "error is zero"
#     musterfilename=musterfilepath+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/MUSTERS/"+fullfinyear+"/"+musterNo+".html"
#     musterrawfilename=musterrawfilepath+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/MUSTERS/"+fullfinyear+"/"+musterNo+".html"
#     #logger.info(musterfilename)
#     #musterfilename="/tmp/"+musterNo+".html"
#     logger.info("MusterFileName" +musterfilename)
#     writeFile(musterfilename,musterhtml)
     # writeFile(musterrawfilename,myhtml)




 
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
