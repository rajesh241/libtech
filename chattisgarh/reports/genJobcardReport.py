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
from libtechFunctions import singleRowQuery
from globalSettings import datadir,nregaDataDir,reportsDir,nregaStaticReportsDir
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQuery2HTML


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='HouseKeeping Script for SurGUJA Database')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)

  args = vars(parser.parse_args())
  return args

def main():
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
  if args['district']:
    districtName=args['district'].lower()

  query="select state from crawlDistricts where name='%s'" % districtName.lower()
  cur.execute(query)
  if cur.rowcount == 0:
    logger.info("INVALID DISTRICT ENTERED")
  else:
    stateName=singleRowQuery(cur,query)
    query="use %s " % districtName.lower()
    cur.execute(query)
    jcReportFilePath=reportsDir.replace("stateName",stateName.title())+"/"+districtName.upper()+"/"
    jcReportFilePath=nregaStaticReportsDir.replace("districtName",districtName.lower())+districtName.upper()+"/"
  
    blockCode='003'
    panchayatCode='007'
    query="select b.blockCode,b.name,p.panchayatCode,p.name from blocks b, panchayats p where b.blockCode=p.blockCode and p.isRequired=1 and b.blockCode='003' and p.panchayatCode='041'"
    query="select b.blockCode,b.name,p.panchayatCode,p.name from blocks b, panchayats p where b.blockCode=p.blockCode and p.isRequired=1"
    #query="select b.blockCode,b.name,p.panchayatCode,p.name from blocks b, panchayats p where b.blockCode=p.blockCode and p.isRequired=1 and b.blockCode='003' "
    cur.execute(query)
    panchResults=cur.fetchall()
    for panchRow in panchResults:
      blockCode=panchRow[0]
      blockName=panchRow[1]
      panchayatCode=panchRow[2]
      panchayatName=panchRow[3]
      logger.info("Processing blockCode: %s blockName: %s panchayatCode: %s PanchayatName: %s " %(blockCode,blockName,panchayatCode,panchayatName))
      
      query="select jobcard from jobcardRegister where blockCode='"+blockCode+"' and panchayatCode='"+panchayatCode+"' "
 #     query="select jobcard from jobcardRegister where blockCode='"+blockCode+"' and panchayatCode='"+panchayatCode+"' and jobcard='CH-05-003-007-001/92-A'  limit 10"
      cur.execute(query)
      results=cur.fetchall()
      for row in results:
        jobcard=row[0]
        logger.info(jobcard)
        jcReportFileName=jcReportFilePath+blockName.upper()+"/"+panchayatName.upper()+"/jobcardRegister/"+jobcard.replace("/","_")+".html"
        logger.info(jcReportFileName)
        myhtml='<h1>Jobcard Register</h1>' 
        myhtml=""
        myhtml+=  getCenterAligned('<h2 style="color:blue"> %s-%s</h2>' % (blockName.upper(),panchayatName.upper()))
        myhtml+=  getCenterAligned('<h2 style="color:green"> %s</h2>' % (jobcard))

        query="select headOfFamily,fatherHusbandName,issueDate,caste,village,isBPL,phone from jobcardRegister where jobcard='%s' " % (jobcard)
        query_table = "<br />"
        query_table += bsQuery2HtmlV2(cur, query, query_caption="JobcardInfo")
        query_table=query_table.replace("query_text","Jobcard Information")
       # myhtml+=  getCenterAligned('<h2 style="color:green">Jobcard Details</h2>' )
        myhtml+=query_table
         
        query="select applicantNo,applicantName,age,gender,accountNo,primaryAccountHolder,bankNameOrPOName,branchNameOrPOAddress from jobcardDetails where jobcard='%s'" % jobcard
        query_table = "<br />"
        query_table += bsQuery2HtmlV2(cur, query)
#        myhtml+=  getCenterAligned('<h2 style="color:green">Family Details</h2>' )
        query_table=query_table.replace("query_text","Family Details")
        myhtml+=query_table
        
        query="select sum(daysWorked) TotalDaysWorked,sum(totalWage) TotalWage from workDetails where jobcard='"+jobcard+"' "
        query_table = "<br />"
       
        query_table += bsQuery2HtmlV2(cur, query, query_caption="JddobcardInfo")
        query_table=query_table.replace("query_text","Work Stats")
        #myhtml+=  getCenterAligned('<h2 style="color:green">Work Stastics</h2>' )
        myhtml+=query_table

        query="select name,workName,musterNo,DATE_FORMAT(dateFrom,'%d-%M-%Y') FromDate,DATE_FORMAT(dateTo,'%d-%M-%Y') ToDate,daysWorked,totalWage,accountNo,status,DATE_FORMAT(creditedDate,'%d-%M-%Y') creditedDate,rejectionReason from workDetails where jobcard='"+jobcard+"' order by dateFrom DESC" 
        query_table = "<br />"
        linkIndex=['2']
        linkType=['muster']
        #query_table += bsQuery2HtmlV2(cur, query, query_caption="JddobcardInfo")
        query_table=tabletUIQuery2HTML(cur,query,hiddenValues=linkIndex,hiddenNames=linkType,districtName=districtName,blockName=blockName,panchayatName=panchayatName)
        #myhtml+=  getCenterAligned('<h2 style="color:green">Work Details</h2>' )
        query_table=query_table.replace("query_text","Work Details")
        myhtml+=query_table
        
        query="select ftoNo,applicantName,primaryAccountHolder,accountNo,wagelistNo,processedDate,creditedAmount,status,rejectionReason from ftoTransactionDetails where jobcard='%s' order by processedDate DESC" %(jobcard)
      #  logger.info(query)
        query_table = "<br />"
        linkIndex=['0']
        linkType=['fto']
        #query_table += bsQuery2HtmlV2(cur, query, query_caption="JddobcardInfo")
        query_table=tabletUIQuery2HTML(cur,query,hiddenValues=linkIndex,hiddenNames=linkType,districtName=districtName,blockName=blockName,panchayatName=panchayatName)
        #myhtml+=  getCenterAligned('<h2 style="color:green">Work Details</h2>' )
        query_table=query_table.replace("query_text","FTO Details")
        myhtml+=query_table
        


        myhtml=htmlWrapper(title=jobcard, head='<h1 aling="center">Jobcard Register</h1>', body=myhtml)
        if not os.path.exists(os.path.dirname(jcReportFileName)):
          os.makedirs(os.path.dirname(jcReportFileName))
        f = open(jcReportFileName, 'w')
        f.write(myhtml.encode("UTF-8"))

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
