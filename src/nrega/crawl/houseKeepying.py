import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
from datetime import datetime,date
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
from libtechFunctions import singleRowQuery,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from crawlSettings import nregaDB 
from crawlSettings import nregaWebDir,nregaRawDataDir,tempDir
from crawlFunctions import formatName,writeFile,writeFileGCS
from crawlFunctions import alterHTMLTables,writeFile,getjcNumber,NICToSQLDate,getFullFinYear,htmlWrapperLocal,getCenterAligned



def rewriteRejectedTable(inhtml,tableID):
  tableHTML=''
  classAtt='id = "%s" border=1 class = " table table-striped"' % tableID
  tableHTML+='<table %s>' % classAtt
  rows=inhtml.findAll('tr')
  for eachRow in rows:
    if "Green" in str(eachRow):
       className="success"
    elif "Yellow" in str(eachRow):
       className="warning"
    elif "Blue" in str(eachRow):
       className="blue"
    else:
       className="danger"
    thCols=eachRow.findAll('th')
    if len(thCols) > 1:
     tableHTML+='<tr class="info">'
     for eachTD in thCols:
       tableHTML+='<th>%s</th>' % eachTD.text
     tableHTML+='</tr>'

    tdCols=eachRow.findAll('td')
    if len(tdCols) > 1:
      tableHTML+='<tr class="%s">' %(className)
      for eachTD in tdCols:
        tableHTML+='<td>%s</td>' % eachTD.text
      tableHTML+='</tr>'

  tableHTML+='</table>'
  return tableHTML


def downloadRejectedPaymentReport(cur,logger,finyear):
  logger.info("Downloading Rejected Payment Info")
  fullfinyear=getFullFinYear(finyear)
  limitString=' limit 100 '
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  query="select d.crawlIP,b.fullBlockCode,b.stateCode,b.stateName,b.districtCode,b.rawBlockName,b.districtName,b.blockName from blocks b,blockStatus bs,districts d where b.stateCode=d.stateCode and b.districtCode=d.districtCode and b.fullBlockCode=bs.fullBlockCode and (b.jRequired=1 or b.isRequired=1) and (bs.rejectedCrawlDate is NULL or TIMESTAMPDIFF(DAY, bs.rejectedCrawlDate, now()) > 1 ) order by bs.rejectedCrawlDate limit 50"
  cur.execute(query)
  results=cur.fetchall()
  reportTypes=['R','I']
  for row in results:
    error=0
    [crawlIP,fullBlockCode,stateCode,stateName,districtCode,rawBlockName,districtName,blockName] = row
    logger.info("State: %s, District : %s, Block : %s " % (stateName,districtName,blockName))
    fullDistrictCode=stateCode+districtCode
    filepath=nregaRawDataDir.replace("stateName",formatName(stateName).upper()).replace("districtName",formatName(districtName).upper())
    modifiedFilePath=nregaWebDir.replace("stateName",formatName(stateName).upper()).replace("districtName",formatName(districtName).upper())
    for reportType in reportTypes:
      dateString= datetime.strftime(date.today(), "%d%b%Y")
      myurl="http://%s/netnrega/FTO/rejection.aspx?lflag=eng&state_code=%s&state_name=%s&district_code=%s&page=d&Block_code=%s&Block_name=%s&district_name=%s&fin_year=%s&typ=%s&linkr=X&"   %(crawlIP,stateCode,stateName.upper(),fullDistrictCode,fullBlockCode,rawBlockName.upper(),districtName,fullfinyear,reportType)
      logger.info(myurl)
      if reportType=='R':
        varname="rejectedDownloaded"
        fname="Rejected_%s.html" % dateString
        cmpString='No Rejection Found'
      else:
        varname="invalidDownloaded"
        fname="Invalid_%s.html" % dateString
        cmpString='No Invalid Account Found'
      filename=filepath+blockName.upper()+"/REJECTEDPAYMENTREPORT/"+fullfinyear+"/"+fname
      r=requests.get(myurl)
      myhtml=r.text
      if ("Narration" in myhtml) or (cmpString in myhtml):
        curerror=writeFileGCS(filename,myhtml)
        error=error+curerror
        if curerror == 0:
          outhtml=''
          htmlsoup=BeautifulSoup(myhtml,"lxml")
          if "Narration" in myhtml:
            table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_gridData2")
            title="%s-%s-%s Rejected Payments" % (stateName,districtName,fullfinyear)
            outhtml+=rewriteRejectedTable(table,"rejectedTable")
          else:
            outhtml+=getCenterAligned('<h3 style="color:green"> %s</h3>' %cmpString )
          outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
          filename=modifiedFilePath+blockName.upper()+"/REJECTEDPAYMENTREPORT/"+fullfinyear+"/rejected.html"
          logger.info(filename)
          writeFile(filename,outhtml)
          query="update blockStatus set %s=1 where fullBlockCode='%s'" % (varname,fullBlockCode)
          logger.info(query)
          cur.execute(query)
      else:
        error=error+1
    if error==0:
      logger.info("File Written SuccessFully")
    logger.info("Total Value of Error is %s" % str(error))
    query="update blockStatus set rejectedCrawlDate=NOW() where fullBlockCode='%s' " % fullBlockCode
    logger.info(query)
    cur.execute(query)


def updatePanchayatStats(cur,logger):
  logger.info("Update Panchayat Status")
  query="select fullPanchayatCode,fullBlockCode,panchayatCode from panchayats where isRequired=1 and fullBlockCode='3406004'"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [fullPanchayatCode,fullBlockCode,panchayatCode]=row
    query="select count(*) from jobcards where fullPanchayatCode='%s' " % fullPanchayatCode
    logger.info(query)
    cur.execute(query)
    row1=cur.fetchone()
    totalJobcards=row1[0]
    query="update panchayatStatus set totalJobcards=%s where fullPanchayatCode='%s' " % (str(totalJobcards),fullPanchayatCode)
    logger.info(query)
    cur.execute(query)
    query="select count(*) from workDetails where isArchive=0 and fullBlockCode='%s' and panchayatCode='%s' and finyear='17'" %(fullBlockCode,panchayatCode)
    cur.execute(query)
    row1=cur.fetchone()
    totalTransactions=row1[0]
    query="select count(*) from workDetails where isArchive=0 and fullBlockCode='%s' and panchayatCode='%s' and finyear='17' and musterStatus=''"  %(fullBlockCode,panchayatCode)

    cur.execute(query)
    row1=cur.fetchone()
    totalPending=row1[0]
    query="select count(*) from workDetails where isArchive=0 and fullBlockCode='%s' and panchayatCode='%s' and finyear='17' and musterStatus='credited'"  %(fullBlockCode,panchayatCode)

    cur.execute(query)
    row1=cur.fetchone()
    totalCredited=row1[0]
    query="select count(*) from workDetails where isArchive=0 and fullBlockCode='%s' and panchayatCode='%s' and finyear='17' and (musterStatus='Invalid Account' or musterStatus='Rejected' )" %(fullBlockCode,panchayatCode)

    cur.execute(query)
    row1=cur.fetchone()
    totalRejected=row1[0]
    query="update panchayatStatus set totalTransactions='%s',totalCredited='%s',totalPending='%s',totalRejected='%s' where fullPanchayatCode='%s'" % (str(totalTransactions),str(totalCredited),str(totalPending),str(totalRejected),fullPanchayatCode)
    logger.info(query)
    cur.execute(query)
def selectRandomDistricts(cur,logger):
  logger.info("Selecting Random Districts")
  query="select count(*),stateName from districts group by stateName"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [count,stateName]=row
    if count <=5 :
      query="update districts set jRequired=1 where stateName='%s' " % (stateName)
      cur.execute(query)
    else:
      query="select id from districts where stateName='%s' order by RAND() limit 5" % (stateName)
      cur.execute(query)
      results1=cur.fetchall()
      for row1 in results1:
        rowid=str(row1[0])
        query="update districts set jRequired=1 where id=%s " %str(rowid)
        cur.execute(query)
def genMusterURLs(cur,logger,mid):
  logger.info("Generating Muster URLs")
  whereClause=''
  if mid is not None:
    whereClause=" where id=%s " % str(mid)
  query="select fullBlockCode,panchayatCode,musterNo,workName,DATE_FORMAT(dateFrom,'%d/%m/%Y'),DATE_FORMAT(dateTo,'%d/%m/%Y'),workCode,finyear,id from musters " + whereClause
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=row[8]
    #[fullBlockCode,panchayatCode,musterNo,workName,
    fullBlockCode=row[0]
    logger.info("Processing ID: %s, fullBlockCode:%s " % (str(rowid),fullBlockCode))
    panchayatCode=row[1]
    musterNo=str(row[2])
    workName=row[3].replace(" ","+")
    #workName=row[3]
    #workName=quote_plus(workName)
    dateFrom=str(row[4])
    dateTo=str(row[5])
    workCode=row[6]
    fullFinYear=getFullFinYear(row[7]) 
    query="select fullPanchayatCode from panchayats where fullBlockCode='%s' and panchayatCode='%s'" % (fullBlockCode,panchayatCode)
    cur.execute(query)
    panchRow=cur.fetchone()
    fullPanchayatCode=panchRow[0]
    query="select crawlIP,stateName,rawDistrictName,rawBlockName,rawPanchayatName,stateShortCode,stateCode,districtCode,blockCode,panchayatName from panchayats where fullPanchayatCode='%s'" % (fullPanchayatCode)
    cur.execute(query)
    row=cur.fetchone()
    crawlIP=row[0]
    stateName=row[1]
    districtName=row[2]
    blockName=row[3]
    panchayatName=row[4] 
    stateShortCode=row[5]
    stateCode=row[6]
    districtCode=row[7]
    blockCode=row[8]
    panchayatNameAltered=row[9]
    jobcardPrefix="%s-%s" % (stateShortCode,districtCode)
    musterURL="http://%s/netnrega/citizen_html/musternew.aspx?state_name=%s&district_name=%s&block_name=%s&panchayat_name=%s&workcode=%s&panchayat_code=%s&msrno=%s&finyear=%s&dtfrm=%s&dtto=%s&wn=%s&id=1" % (crawlIP,stateName.upper(),districtName.upper(),blockName.upper(),panchayatName,workCode,fullPanchayatCode,musterNo,fullFinYear,dateFrom,dateTo,workName)
    #logger.info(musterURL)
    query="update musters set url='%s' where id=%s " % (musterURL,str(rowid))
    cur.execute(query)
def updateMusterStats(cur,logger):
  logger.info("Updating Muster Statistics")
  query="select id,fullBlockCode,musterNo,finyear from musters where wdProcessed=1 "
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [rowid,fullBlockCode,musterNo,finyear] = row
    query="select count(*) from workDetails where finyear='%s' and fullBlockCode='%s' and musterNo='%s' " % (finyear,fullBlockCode,musterNo)
    cur.execute(query)
    row1=cur.fetchone()
    totalCount=row1[0] 
    query="select count(*) from workDetails where musterStatus!='Credited' and finyear='%s' and fullBlockCode='%s' and musterNo='%s' " % (finyear,fullBlockCode,musterNo)
    cur.execute(query) 
    row1=cur.fetchone()
    totalPending=row1[0] 
    totalSuccess=totalCount-totalPending
    logger.info("musterid : %s totalSuccess:%s totalCount:%s totalPending:%s " % (str(rowid),str(totalSuccess),str(totalCount),str(totalPending)))
    query="update musters set totalCount=%s,totalSuccess=%s,totalPending=%s where id=%s " % (str(totalCount),str(totalSuccess),str(totalPending),str(rowid))
    cur.execute(query)
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-mid', '--musterID', help='Muster ID', required=False)
  parser.add_argument('-ums', '--updateMusterStats', help='update Statistics in Muster Table', required=False,action='store_const', const=1)
  parser.add_argument('-srd', '--selectRandomDistricts', help='Select Random Districts', required=False,action='store_const', const=1)
  parser.add_argument('-ups', '--updatePanchayatStats', help='update Panchayat Status', required=False,action='store_const', const=1)
  parser.add_argument('-gmu', '--genMusterURL', help='Generate Muster URl', required=False,action='store_const', const=1)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=False)
  parser.add_argument('-drp', '--downloadRejectedPaymentReport', help='Download Rejected Payment Info', required=False,action='store_const', const=1)
  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  
  if args['updateMusterStats']:
    updateMusterStats(cur,logger) 
  if args['selectRandomDistricts']:
    selectRandomDistricts(cur,logger)
  if args['updatePanchayatStats']:
    updatePanchayatStats(cur,logger)
  if args['genMusterURL']:
    genMusterURLs(cur,logger,args['musterID'])
  if args['downloadRejectedPaymentReport']:
    if args['finyear']:
      finyear=args['finyear']
    else:
      finyear='17'
    downloadRejectedPaymentReport(cur,logger,finyear)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
