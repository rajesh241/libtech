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
from libtechFunctions import singleRowQuery,getjcNumber,getFullFinYear,writeFile
from nregaSettings import nregaWebDir,nregaRawDataDir 
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable

from crawlFunctions import getDistrictParams
from crawlFunctions import alterMusterHTML,getMusterPaymentDate
from crawlFunctions import alterFTOHTML,genHTMLHeader,NICToSQLDate
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script to Populate workDetail Table')
  parser.add_argument('-t', '--testMode', help='Script will run in TestMode', required=False,action='store_const', const=1)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)
  parser.add_argument('-af', '--additionalFilters', help='please enter additional filters', required=False)
  parser.add_argument('-f', '--finyear', help='Please enter the finyear', required=True)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)
  args = vars(parser.parse_args())
  return args
  
 
def main():
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  regex1=re.compile(r'</td></font></td>',re.DOTALL)
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  
  limitSetting=''
  additionalFilter=''
  if args['district']:
    districtName=args['district'].lower()
  if args['finyear']:
    infinyear=args['finyear'].lower()
  
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
  musterfilepath=nregaRawDataDir.replace("districtName",districtName.lower())
  modifiedMusterFilePath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString="  "
  if args['additionalFilters']:
    additionalFilter=" and "+args['additionalFilters']
   # stateName=singleRowQuery(cur,query)
  reMatchString="%s-%s-" % (stateShortCode,districtCode)
 
  query=" select m.id,m.finyear,m.musterNo,p.name,b.name,m.workCode,m.blockCode,p.panchayatCode,m.workName,m.dateFrom,m.dateTo,p.rawName from musters m,blocks b,panchayats p where m.wdError=0 and m.isDownloaded=1 and m.wdProcessed=0  and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isRequired=1 %s and finyear='%s' %s" %(additionalFilter,infinyear,limitString)
  logger.info(query)
  cur.execute(query)
  if cur.rowcount:
    logger.info("NUMBER OF RECORDS TO BE PROCESSED  " +str(cur.rowcount))
    results = cur.fetchall()
    for row in results:
      musterID=str(row[0])
      musterNo=row[2]
      blockName=row[4]
      panchayatNameRaw=row[3]
      panchayatName=row[3].upper()
      panchayatNameOnlyLetters=re.sub(r"[^A-Za-z]+", '', panchayatName)
      finyear=row[1]
      workCode=row[5]
      blockCode=row[6]
      panchayatCode=row[7]
      workName=row[8].replace(","," ")
      dateFrom=str(row[9])
      dateTo=str(row[10])
      panchayatRawName=str(row[11])
      fullfinyear=getFullFinYear(finyear)
      logger.info(fullfinyear) 
      logger.info("muster ID : %s   musterNo:%s  blockName:%s  panchayatName:%s " % (str(musterID),str(musterNo),blockName,panchayatName))
      musterfilename=musterfilepath+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/MUSTERS/"+fullfinyear+"/"+musterNo+".html"
      modifiedMusterFileName=modifiedMusterFilePath+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/MUSTERS/"+fullfinyear+"/"+musterNo+".html"
      print logger.info("Muster FileName:"+musterfilename)
      print logger.info("Muster FileName:"+modifiedMusterFileName)
      if (os.path.isfile(musterfilename)): 
        musterhtml=open(musterfilename,'r').read()
        #musterhtml=re.sub(regex,"</font></td>",musterhtml1)
      else:
        musterhtml="Timeout expired"

      if ("Timeout expired" in musterhtml) or ("Due to the heavy network traffic" in musterhtml) or ("The Values specified are wrong" in musterhtml) or ("The service is unavailable" in musterhtml):
        errorflag=1
      else:
        myhtml1=re.sub(regex,"",musterhtml)
        myhtml2=re.sub(regex1,"</font></td>",myhtml1)
        paymentDateString,sanctionNo,sanctionDate=getMusterPaymentDate(myhtml2)
        errorflag,outhtml=alterMusterHTML(myhtml2)

      if errorflag==1:
        logger.info("This is a invalid Muste rFile")
        query="update musters set wdError=1 where id="+str(musterID)
        cur.execute(query)
      else:
        logger.info("Muster HTML Looks good, now we shall process it")
        htmlHeaderLabels=["District Name","Block Name","PanchayatName","Muster No","Work Code","Work Name","sanctionNo","Sanction Date","Date From","Date To","Payment Date"]
        htmlHeaderValues=[districtName,blockName,panchayatName.upper(),musterNo,workCode,workName,sanctionNo,sanctionDate,dateFrom,dateTo,paymentDateString]
        htmlHeader=genHTMLHeader(htmlHeaderLabels,htmlHeaderValues)

        modifiedHTML=htmlHeader+outhtml
        modifiedHTML=htmlWrapperLocal(title="Muster Details", head='<h1 aling="center">'+musterNo+'</h1>', body=modifiedHTML)
        logger.info(modifiedMusterFileName)
        writeFile(modifiedMusterFileName,modifiedHTML)


        htmlsoup=BeautifulSoup(modifiedHTML,"html.parser")
        table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
        rows = table.findAll('tr')

        for tr in rows: #This loop is to find staus Index
          cols = tr.findAll('th')
          if len(cols) > 7:
            i=0
            while i < len(cols):
              value="".join(cols[i].text.split())
              if "Status" in value:
                statusindex=i
              i=i+1
        isComplete=1

        for tr in rows:
          cols = tr.findAll('td')
          if len(cols) > 7:
            musterIndex="".join(cols[0].text.split())
            aadharNo=cols[2].text.strip().lstrip().rstrip()
            nameandjobcard="".join(cols[1].text.split())
            logger.info("Name + Jocbcard %s" % nameandjobcard)
            nameandjobcard=cols[1].text.replace('\n',' ')
            nameandjobcard=nameandjobcard.replace("\\","")
            logger.info("Name + Jocbcard %s" % nameandjobcard)
            if stateShortCode in nameandjobcard:
              totalWage="".join(cols[statusindex-6].text.split())
              dayWage="".join(cols[statusindex-10].text.split())
              status="".join(cols[statusindex].text.split())
              accountNo="".join(cols[statusindex-5].text.split())
              daysWorked="".join(cols[statusindex-11].text.split())
              bankNameOrPOName="".join(cols[statusindex-4].text.split())
              bankNameOrPOName=cols[statusindex-4].text
              bankNameOrPOName=''
              branchNameOrPOAddress="".join(cols[statusindex-3].text.split())
              branchNameOrPOAddress=cols[statusindex-3].text
              branchCodeOrPOCode=cols[statusindex-2].text.replace("\n"," ")
              branchCodeOrPOCode=''
              wagelistNo="".join(cols[statusindex-1].text.split())
              creditedDateString="".join(cols[statusindex+1].text.split())
              nameandjobcardarray=re.match(r'(.*)'+reMatchString+'(.*)',nameandjobcard)
              name=nameandjobcardarray.groups()[0]
              jobcard=reMatchString+nameandjobcardarray.groups()[1]
              jcNumber=getjcNumber(jobcard)
              logger.info(str(musterIndex)+" "+jobcard)
              if status != 'Credited':
                isComplete=0      
              paymentDate=NICToSQLDate(paymentDateString)
              creditedDate=NICToSQLDate(creditedDateString)
              #We also need to create entry in WageList Table
              query="select * from wagelists where wagelistNo='%s' " % (wagelistNo)
              logger.info(query)
              cur.execute(query)
              if cur.rowcount == 0:
                query="insert into wagelists (blockCode,finyear,wagelistNo) values ('%s','%s','%s') " % (blockCode,finyear,wagelistNo)
                logger.info(query)
                cur.execute(query)
              #Here first we need to find out if the record already exists
              logger.info(" muster No: %s  musterIndex : %s  finyear: %s  blockCode: %s " % (musterNo, musterIndex, finyear, blockCode))
              query="select id from workDetails where musterNo=%s and musterIndex=%s and finyear='%s' and blockCode='%s'" % (musterNo,musterIndex,finyear,blockCode)
              cur.execute(query)
              if cur.rowcount == 0:
                logger.info("This record does not exist")
                query="insert into workDetails (musterNo,musterIndex,finyear,blockCode,createDate) values (%s,%s,'%s','%s',NOW()) " % (musterNo,musterIndex,finyear,blockCode)
                logger.info(query)
                cur.execute(query)
                mtID=str(cur.lastrowid)
              else:
                row1=cur.fetchone() 
                mtID=str(row1[0])
  
              logger.info("The musterTransaction ID: %s " % mtID)
              query="update workDetails set aadharNo='%s',creditedDate=%s,paymentDate=%s,updateDate=NOW(),blockName='%s',panchayatCode='%s',panchayatName='%s',name='%s',jobcard='%s',jcNumber='%s',workCode='%s',workName='%s',dateFrom='%s',dateTo='%s',daysWorked=%s,dayWage=%s,totalWage=%s,accountNo='%s',wagelistNo='%s',bankNameOrPOName='%s',branchNameOrPOAddress='%s',branchCodeOrPOCode='%s',musterStatus='%s' where id=%s" % (aadharNo,creditedDate,paymentDate,blockName,panchayatCode,panchayatNameRaw.upper(),name,jobcard,jcNumber,workCode,workName,dateFrom,dateTo,str(daysWorked),str(dayWage),str(totalWage),str(accountNo),wagelistNo,bankNameOrPOName,branchNameOrPOAddress,branchCodeOrPOCode,status,mtID) 
              logger.info(query)
              cur.execute(query)


        query="update musters set wdProcessed=1,wdComplete=%s where id=%s" %(str(isComplete),str(musterID))
        logger.info(query)
        cur.execute(query)
#
#             query="update workDetails set %s,%s,updateDate=NOW(),blockName='%s',panchayatCode='%s',panchayatName='%s',name='%s',jobcard='%s',jcNumber='%s',workCode='%s',workName='%s',dateFrom='%s',dateTo='%s',daysWorked=%s,dayWage=%s,totalWage=%s,accountNo='%s',wagelistNo='%s',bankNameOrPOName='%s',branchNameOrPOAddress='%s',branchCodeOrPOCode='%s',status='%s' where id=%s" % (creditedDateQueryString,paymentDateQueryString,blockName,panchayatCode,panchayatNameRaw,name,jobcard,jcNumber,workCode,workName,dateFrom,dateTo,str(daysWorked),str(dayWage),str(totalWage),str(accountNo),wagelistNo,bankNameOrPOName,branchNameOrPOAddress,branchCodeOrPOCode,status,mtID) 
#             logger.info(query)
#             cur.execute(query)

#       query="update musters set wdError=1 where id="+str(musterID)
#       cur.execute(query)
#     else:
#       htmlsoup=BeautifulSoup(musterhtml,"html.parser")
#       try:
#         table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
#         rows = table.findAll('tr')
#         errorflag=0
#       except:
#         errorflag=1
#         query="update musters set wdError=1 where id="+str(musterID)
#         cur.execute(query)
#       #The Below Loop will find Status Index
#       for tr in rows:
#         cols = tr.findAll('th')
#         if len(cols) > 7:
#           i=0
#           while i < len(cols):
#             value="".join(cols[i].text.split())
#             if "Status" in value:
#               statusindex=i
#             i=i+1
#       isComplete=1
#       #Extracting Paymetn Date
#       paymentTD=htmlsoup.find('td',id="paymentDateTD")
#       paymentDateString=paymentTD.text.replace(" ","")
#
#       #Now we need to extract the details from the table

#             if creditedDatestring != '':
#               creditedDate = time.strptime(creditedDatestring, '%d/%m/%Y')
#               creditedDate = time.strftime('%Y-%m-%d %H:%M:%S', creditedDate)
#               creditedDateQueryString="creditedDate='%s'" %creditedDate
#             else:
#               creditedDateQueryString="creditedDate=NULL"
#
#             if paymentDateString != '':
#               paymentDate = time.strptime(paymentDateString, '%d/%m/%Y')
#               paymentDate = time.strftime('%Y-%m-%d %H:%M:%S', paymentDate)
#               paymentDateQueryString = " paymentDate='%s' " % paymentDate
#             else:
#               paymentDateQueryString=" paymentDate=NULL "
#
#             #Here first we need to find out if the record already exists
#             logger.info(" muster No: %s  musterIndex : %s  finyear: %s  blockCode: %s " % (musterNo, musterIndex, finyear, blockCode))
#             query="select id from workDetails where musterNo=%s and musterIndex=%s and finyear='%s' and blockCode='%s'" % (musterNo,musterIndex,finyear,blockCode)
#             cur.execute(query)
#             if cur.rowcount == 0:
#               logger.info("This record does not exist")
#               query="insert into workDetails (musterNo,musterIndex,finyear,blockCode,createDate) values (%s,%s,'%s','%s',NOW()) " % (musterNo,musterIndex,finyear,blockCode)
#               logger.info(query)
#               cur.execute(query)
#               mtID=str(cur.lastrowid)
#             else:
#               row1=cur.fetchone() 
#               mtID=str(row1[0])
#
#             logger.info("The musterTransaction ID: %s " % mtID)
#
#             query="update workDetails set %s,%s,updateDate=NOW(),blockName='%s',panchayatCode='%s',panchayatName='%s',name='%s',jobcard='%s',jcNumber='%s',workCode='%s',workName='%s',dateFrom='%s',dateTo='%s',daysWorked=%s,dayWage=%s,totalWage=%s,accountNo='%s',wagelistNo='%s',bankNameOrPOName='%s',branchNameOrPOAddress='%s',branchCodeOrPOCode='%s',status='%s' where id=%s" % (creditedDateQueryString,paymentDateQueryString,blockName,panchayatCode,panchayatNameRaw,name,jobcard,jcNumber,workCode,workName,dateFrom,dateTo,str(daysWorked),str(dayWage),str(totalWage),str(accountNo),wagelistNo,bankNameOrPOName,branchNameOrPOAddress,branchCodeOrPOCode,status,mtID) 
#             logger.info(query)
#             cur.execute(query)
#
#       query="update musters set wdProcessed=1,wdComplete=%s where id=%s" %(str(isComplete),str(musterID))
#       logger.info(query)
#       cur.execute(query)
  
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
