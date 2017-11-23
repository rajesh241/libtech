from bs4 import BeautifulSoup
from queue import Queue
import json
from pprint import pprint
from threading import Thread
import threading
from datetime import datetime,date,timedelta
import requests
import os
import sys
import re
import time
import re
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
regex1=re.compile(r'</td></font></td>',re.DOTALL)
from customSettings import repoDir,djangoDir,djangoSettings
from customSettings import musterTimeThreshold
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getFullFinYear,getCenterAlignedHeading,getTelanganaDate,getjcNumber
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils import timezone


os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,LibtechTag,PanchayatStat,Muster

maxMusterDownloadQueue=200
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for created PRD Document')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-cr', '--crawlRequirement', help='Kindly put the tag of crawlRequiremtn that panchayats are tagged with, by default it will do it for panchayats which are tagged with crawlRequirement of FULL', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-p', '--panchayatCode', help='StateCode for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args

def getTableData(logger,tableTitle,eachPanchayat):
  myData=[]
  curfinyear=getCurrentFinYear()
  finyears=["16","17","18"]
  if tableTitle == "jobcardInfo":
    myPanchayatStat=PanchayatStat.objects.filter(panchayat=eachPanchayat,finyear=curfinyear).first()
    if myPanchayatStat is not None:
      jobcardsTotal=myPanchayatStat.jobcardsTotal
      workersTotal=myPanchayatStat.workersTotal
    else:
      jobcardsTotal=0
      workersTotal=0
    
#  matrix=[][]
    rowData=[]
    rowData.append(jobcardsTotal)
    rowData.append(workersTotal)
    myData.append(rowData)
   
  if tableTitle == "paymentInfoSummary":
   
    for finyear in finyears:
      logger.info(finyear)
      rowData=[]
      myPanchayatStat=PanchayatStat.objects.filter(panchayat=eachPanchayat,finyear=finyear).first()
      if myPanchayatStat is not None:
        libtechWorkDays=myPanchayatStat.libtechWorkDays
      else:
        libtechWorkDays=0
      totalWages=0
      totalWorkers=0
      myMusters=Muster.objects.filter(panchayat=eachPanchayat,finyear=finyear)
      rowData.append(finyear)
      rowData.append(libtechWorkDays)
      rowData.append(totalWages)
      rowData.append(totalWorkers)
      rowData.append(len(myMusters))
      myData.append(rowData) 

  if tableTitle == "unpaidMusters":
    myMusters=Muster.objects.filter(panchayat=eachPanchayat,isComplete=False).order_by("finyear")
    for eachMuster in myMusters:
      rowData=[]
      if eachMuster.dateTo is not None:
        dateTo=str(eachMuster.dateTo.strftime("%d/%m/%Y"))
      else:
        dateTo=""
      rowData.append(eachMuster.musterNo)
      rowData.append(eachMuster.finyear)
      rowData.append(eachMuster.workName)
      rowData.append(dateTo)
      rowData.append("")
      myData.append(rowData) 
      
          
  return myData
 
def getTableHTML(logger,eachTable,myLan,eachPanchayat):
  tableHTML=''
  tableHeader=eachTable["heading"]["hindi"]
  tableCols=eachTable["columns"]
  tableTitle=eachTable["title"]
  classAtt='id = "%s" border=1 class = " table table-striped"' % tableTitle
  tableHTML+="<h3>%s</h3>" % (tableHeader)
  tableHTML+='<table %s>' % classAtt
  tableHTML+='<thead><tr>'

  for col in tableCols:
    logger.info(col["hindi"])
    tableHTML+='<th>%s</th>' % str(col[myLan])
  tableHTML+='</tr></thead>'
  logger.info(tableTitle)
  dataMatrix=getTableData(logger,tableTitle,eachPanchayat)  
  tableHTML+="<tbody>"
  i=0
  for row in dataMatrix:
    i=i+1
    tableHTML+="<tr>"
    j=0
    for col in row:
      tableHTML+="<td>%s</td>" % (str(col))
      j=j+1
    tableHTML+="</tr>"

  tableHTML+="</tbody>"
  tableHTML+="</table>"
  return tableHTML

def getPanchayatStats(logger,jsonDict,eachPanchayat):
  myLan="hindi"
  outhtml=''
#  matrix[0][0] = "जलब कतरर सपखयत:"
  logger.info(jsonDict)
  allTables=jsonDict["reports"]["tables"]
  for eachTable in allTables:
    outhtml+=getTableHTML(logger,eachTable,myLan,eachPanchayat)

# tableHTML=''
# tableID="JobcardStat"
# classAtt='id = "%s" border=1 class = " table table-striped"' % tableID
# tableHTML+='<table %s>' % classAtt
# tableHTML+='<tr>'
# tableHTML+='<td>%s</td>' % str(jobcardsTotal)
# tableHTML+='</tr>'

#  tableHTML+='</table>'

#  outhtml+=tableHTML
  return outhtml

def main():
  args = argsFetch()
  with open('report.json') as data_file:    
    jsonDict = json.load(data_file)
  reportType="PRDHTML"
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  stateCode=args['stateCode']
  panchayatCode=args['panchayatCode']
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  if args['crawlRequirement']:
    crawlRequirement=args['crawlRequirement']
  else:
    crawlRequirement="FULL"

  stateCode=args['stateCode']
  panchayatCode=args['panchayatCode']
  if panchayatCode is not None:
    myPanchayats=Panchayat.objects.filter(block__district__state__isNIC=True,code=panchayatCode)[:limit]
  else: 
    if stateCode is None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement=crawlRequirement,block__district__state__isNIC=True)[:limit]
    else:
      myPanchayats=Panchayat.objects.filter(crawlRequirement=crawlRequirement,block__district__state__code=stateCode,block__district__state__isNIC=True)[:limit]
  for eachPanchayat in myPanchayats:
    
    outhtml=''
    title="%s-%s-%s-%s"   % (eachPanchayat.block.district.state.name,eachPanchayat.block.district.name,eachPanchayat.block.name,eachPanchayat.name)
    
    statTables=getPanchayatStats(logger,jsonDict,eachPanchayat)
    outhtml+=statTables

    outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
    try:
      outhtml=outhtml.encode("UTF-8")
    except:
      outhtml=outhtml
    finyear=getCurrentFinYear()
    filename="PRD_%s.html" % (eachPanchayat.slug)
    savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,outhtml)
    
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
