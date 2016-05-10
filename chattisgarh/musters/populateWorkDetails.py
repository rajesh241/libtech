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
from libtechFunctions import singleRowQuery,getjcNumber
from globalSettings import datadir,nregaDataDir

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
  regex=re.compile(r'</td></font></td>',re.DOTALL)
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  
  limitSetting=''
  additionalFilter=''
  if args['district']:
    districtName=args['district'].lower()
  if args['finyear']:
    infinyear=args['finyear'].lower()
  
  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString=" limit 10000 "
  if args['additionalFilters']:
    additionalFilter=" and "+args['additionalFilters']
  query="select state,stateShortCode,districtCode from crawlDistricts where name='%s'" % districtName.lower()
  cur.execute(query)
  if cur.rowcount == 0:
    logger.info("INVALID DISTRICT ENTERED")
  else:
    row=cur.fetchone()
    stateName=row[0]
    stateShortCode=row[1]
    districtCode=row[2]
   # stateName=singleRowQuery(cur,query)
    reMatchString="%s-%s-" % (stateShortCode,districtCode)
    musterfilepath=nregaDataDir.replace("stateName",stateName.title())+"/"+districtName.upper()+"/"
    query="use %s " % districtName.lower()
    cur.execute(query)
   
    query=" select m.id,m.finyear,m.musterNo,p.name,b.name,m.workCode,m.blockCode,p.panchayatCode,m.workName,m.dateFrom,m.dateTo from musters m,blocks b,panchayats p where m.isDownloaded=1 and m.wdProcessed=0  and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isRequired=1 %s and finyear='%s' %s" %(additionalFilter,infinyear,limitString)
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
        finyear=row[1]
        workCode=row[5]
        blockCode=row[6]
        panchayatCode=row[7]
        workName=row[8]
        dateFrom=str(row[9])
        dateTo=str(row[10])
        fullfinyear="20"+str(int(finyear) -1)+"-20"+str(finyear)
        logger.info(fullfinyear) 
        logger.info("muster ID : %s   musterNo:%s  blockName:%s  panchayatName:%s " % (str(musterID),str(musterNo),blockName,panchayatName))
        musterfilename=musterfilepath+blockName+"/"+panchayatName+"/MUSTERS/"+fullfinyear+"/"+musterNo+".html"
        print logger.info("Muster FileName:"+musterfilename)
        if (os.path.isfile(musterfilename)): 
          musterhtml1=open(musterfilename,'r').read()
          musterhtml=re.sub(regex,"</font></td>",musterhtml1)
        else:
          musterhtml="Timeout expired"

        if "Timeout expired" in musterhtml:
          logger.info("This is time out expired file")
          errorflag=1
          query="update musters set wdError=1 where id="+str(musterID)
          cur.execute(query)
        else:
          htmlsoup=BeautifulSoup(musterhtml)
          try:
            table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
            rows = table.findAll('tr')
            errorflag=0
          except:
            errorflag=1
            query="update musters set wdError=1 where id="+str(musterID)
            cur.execute(query)
          #The Below Loop will find Status Index
          for tr in rows:
            cols = tr.findAll('th')
            if len(cols) > 7:
              i=0
              while i < len(cols):
                value="".join(cols[i].text.split())
                if "Status" in value:
                  statusindex=i
                i=i+1
          isComplete=1

          #Now we need to extract the details from the table
          for tr in rows:
            #print "Looking at rows will look for td now"
            cols = tr.findAll('td')
            #print "the length of columns is "+str(len(cols))
            if len(cols) > 7:
              musterIndex="".join(cols[0].text.split())
              nameandjobcard="".join(cols[1].text.split())
              if nameandjobcard!='':
                totalWage="".join(cols[statusindex-6].text.split())
                dayWage="".join(cols[statusindex-10].text.split())
                status="".join(cols[statusindex].text.split())
                accountNo="".join(cols[statusindex-5].text.split())
                daysWorked="".join(cols[statusindex-11].text.split())
                bankNameOrPOName="".join(cols[statusindex-4].text.split())
                branchNameOrPOAddress="".join(cols[statusindex-3].text.split())
                branchCodeOrPOCode="".join(cols[statusindex-2].text.split())
                wagelistNo="".join(cols[statusindex-1].text.split())
                paymentDateString="".join(cols[statusindex+1].text.split())
                creditedDatestring="".join(cols[statusindex+3].text.split())
                nameandjobcardarray=re.match(r'(.*)'+reMatchString+'(.*)',nameandjobcard)
                name=nameandjobcardarray.groups()[0]
                jobcard=reMatchString+nameandjobcardarray.groups()[1]
                jcNumber=getjcNumber(jobcard)
                #print str(musterIndex)+"  "+name+"  "+jobcard
                logger.info(str(musterIndex)+" "+jobcard)
                if status != 'Credited':
                  isComplete=0
                if creditedDatestring != '':
                  creditedDate = time.strptime(creditedDatestring, '%d/%m/%Y')
                  creditedDate = time.strftime('%Y-%m-%d %H:%M:%S', creditedDate)
                  creditedDateQueryString="creditedDate='%s'" %creditedDate
                else:
                  creditedDateQueryString="creditedDate=NULL"


                query="insert into workDetails (musterNo,musterIndex,finyear,blockCode,createDate) values (%s,%s,'%s','%s',NOW()) " % (musterNo,musterIndex,finyear,blockCode)
                logger.info(query)
                try:
                  cur.execute(query)
                except:
                  logger.info('This Record ALready Exists' + query)
                query="update workDetails set updateDate=NOW(),blockName='%s',panchayatCode='%s',panchayatName='%s',name='%s',jobcard='%s',jcNumber='%s',workCode='%s',workName='%s',dateFrom='%s',dateTo='%s',daysWorked=%s,dayWage=%s,totalWage=%s,accountNo='%s',wagelistNo='%s',bankNameOrPOName='%s',branchNameOrPOAddress='%s',branchCodeOrPOCode='%s',status='%s' where musterNo=%s and musterIndex=%s and finyear='%s' and blockCode='%s' " % (blockName,panchayatCode,panchayatNameRaw,name,jobcard,jcNumber,workCode,workName.decode('UTF-8'),dateFrom,dateTo,str(daysWorked),str(dayWage),str(totalWage),str(accountNo),wagelistNo,bankNameOrPOName,branchNameOrPOAddress,branchCodeOrPOCode,status,musterNo,musterIndex,finyear,blockCode) 
                logger.info(query)
                cur.execute(query)

                if paymentDateString != '':
                  paymentDate = time.strptime(paymentDateString, '%d/%m/%Y')
                  paymentDate = time.strftime('%Y-%m-%d %H:%M:%S', paymentDate)
                  query="update workDetails set paymentDate='%s' where musterNo=%s and musterIndex=%s and finyear='%s' and blockCode='%s'" % (paymentDate,musterNo,musterIndex,finyear,blockCode)
                  cur.execute(query)
                else:
                  query="update workDetails set paymentDate=NULL where musterNo=%s and musterIndex=%s and finyear='%s' and blockCode='%s'" % (musterNo,musterIndex,finyear,blockCode)
                  cur.execute(query)


                if creditedDatestring != '':
                  creditedDate = time.strptime(creditedDatestring, '%d/%m/%Y')
                  creditedDate = time.strftime('%Y-%m-%d %H:%M:%S', creditedDate)
                  query="update workDetails set creditedDate='%s' where musterNo=%s and musterIndex=%s and finyear='%s' and blockCode='%s'" % (creditedDate,musterNo,musterIndex,finyear,blockCode)
                  cur.execute(query)
                else:
                  query="update workDetails set creditedDate=NULL where musterNo=%s and musterIndex=%s and finyear='%s' and blockCode='%s'" % (musterNo,musterIndex,finyear,blockCode)
                  cur.execute(query)

          query="update musters set wdProcessed=1,wdComplete=%s where id=%s" %(str(isComplete),str(musterID))
          logger.info(query)
          cur.execute(query)
  
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
