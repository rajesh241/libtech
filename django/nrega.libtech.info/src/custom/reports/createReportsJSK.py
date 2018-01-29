from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
sys.path.insert(0, "./../scripts")
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,savePanchayatReport,getEncodedData
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,PanchayatReport,PanchayatStat

def savePanchayatReportWrapper(logger,finyear,eachPanchayat,tableCols,reportType,reportsuffix,myData,csvData):  

  myPanchayatStat=PanchayatStat.objects.filter(panchayat=eachPanchayat,finyear=finyear).first()
  if myPanchayatStat is not None:
    accuracyIndex=myPanchayatStat.workDaysAccuracyIndex
  else:
    accuracyIndex = 0
  title="%s Report for Block %s Panchayat %s FY %s " % (reportType,eachPanchayat.block.name,eachPanchayat.name,getFullFinYear(finyear))
  filename='%s_%s_%s.csv' % (eachPanchayat.slug,finyear,reportsuffix)
  savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,getEncodedData(csvData))
  myhtml="<h4>Accuracy Index %s </h4>" % str(accuracyIndex)
  myhtml+=getTableHTML(logger,tableCols,myData)
  myhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=myhtml)
  reportType="%sHTML" % reportType
  filename='%s_%s_%s.html' % (eachPanchayat.slug,finyear,reportsuffix)
  savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,getEncodedData(myhtml))

def getTableHTML(logger,tableCols,tableData):
  tableHTML=''
  tableTitle="libtechTable"
  classAtt='id = "%s" border=1 class = " table table-striped table-condensed"' % tableTitle
  tableHTML+='<table %s>' % classAtt
  tableHTML+='<thead><tr>'
  for col in tableCols:
    tableHTML+='<th>%s</th>' % str(col)
  tableHTML+='</tr></thead>'
  tableHTML+="<tbody>"
  i=0
  for row in tableData:
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


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-c', '--create', help='Create Reports', required=False,action='store_const', const=1)
  parser.add_argument('-d', '--download', help='Download Reports', required=False,action='store_const', const=1)
  parser.add_argument('-a', '--archive', help='Archive Reports', required=False,action='store_const', const=1)
  parser.add_argument('-g', '--gather', help='Archive Reports', required=False,action='store_const', const=1)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-b', '--blockCode', help='BlockCode for which the reports need to be archived', required=False)
  parser.add_argument('-cr', '--crawlRequirement', help='Kindly put the tag of crawlRequiremtn that panchayats are tagged with, by default it will do it for panchayats which are tagged with crawlRequirement of FULL', required=False)
  parser.add_argument('-p', '--panchayatCode', help='panchaytCode for which the numbster needs to be downloaded', required=False)

  args = vars(parser.parse_args())
  return args


def main():
  finyears=["16","17","18"]
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['crawlRequirement']:
    crawlRequirement=args['crawlRequirement']
  else:
    crawlRequirement="FULL"
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  stateCode=args['stateCode']
  panchayatCode=args['panchayatCode']
  logger.info(panchayatCode)
 #Telangana Block 3614005  
  if args['gather']:
    reports=['workPayment','rejectedPayment','pendingPayment','inValidPayment']
    finyears=["16","17","18"]
    inpanchayatCode=args['panchayatCode']
    eachPanchayat=Panchayat.objects.filter(code=inpanchayatCode).first()
    filepath="/tmp/%s/csv/" % (eachPanchayat.slug)
    for eachReport in reports:
      for finyear in finyears:
        logger.info(finyear+eachReport+str(eachPanchayat))
        myPanchayatReport=PanchayatReport.objects.filter(panchayat=eachPanchayat,reportType=eachReport,finyear=finyear).first()
        url=myPanchayatReport.reportFile.url
        logger.info(url)
        htmlReport=eachReport+"HTML"
        filename="%s_%s_%s.csv" % (eachPanchayat.slug,eachReport,finyear)
        cmd="mkdir -p %s && cd %s && wget -O %s %s " %(filepath,filepath,filename,url) 
        logger.info(cmd)
        os.system(cmd)
 
  if args['archive']:
    reports=['workPayment','rejectedPayment','pendingPayment','inValidPayment']
 #   reports=['paymentDetailsTelangana']
#    reports=['workPaymentDelayAnalysis']
    finyears=["16","17","18"]
    if args['blockCode']:
      inblockCode=args['blockCode']
    else:
      inblockCode='3406007'
    myBlocks=Block.objects.filter(code=inblockCode)
    for eachBlock in myBlocks:
      filepath="/tmp/%s/csv/" % (eachBlock.slug)
      myPanchayats=Panchayat.objects.filter(block=eachBlock)
      for eachPanchayat in myPanchayats:
        for eachReport in reports:
          for finyear in finyears:
            logger.info(finyear+eachReport+str(eachPanchayat))
            myPanchayatReport=PanchayatReport.objects.filter(panchayat=eachPanchayat,reportType=eachReport,finyear=finyear).first()
            url=myPanchayatReport.reportFile.url
            logger.info(url)
            htmlReport=eachReport+"HTML"
            filename="%s_%s_%s.csv" % (eachPanchayat.slug,eachReport,finyear)
            cmd="mkdir -p %s && cd %s && wget -O %s %s " %(filepath,filepath,filename,url) 
            logger.info(cmd)
            os.system(cmd)
       #    myPanchayatReport=PanchayatReport.objects.filter(panchayat=eachPanchayat,reportType=htmlReport,finyear=finyear).first()
       #    url=myPanchayatReport.reportFile.url
       #    logger.info(url)
       #    filename="%s_%s_%s.html" % (eachPanchayat.slug,eachReport,finyear)
       #    cmd="mkdir -p %s && cd %s && wget -O %s %s " %(filepath,filepath,filename,url) 
       #    logger.info(cmd)
       #    os.system(cmd)
  if args['create']:
    if panchayatCode is not None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',code=panchayatCode)
    elif stateCode is not None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement=crawlRequirement,block__district__state__code=stateCode)
    else:
      myPanchayats=Panchayat.objects.filter(crawlRequirement=crawlRequirement,block__district__state__isNIC=True)[:limit]
#    else:
#      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL')[:limit]
    for eachPanchayat in myPanchayats:
      logger.info("**********************************************************************************")
      logger.info("Createing work Payment report for panchayat: %s panchayatCode: %s ID: %s" % (eachPanchayat.name,eachPanchayat.code,str(eachPanchayat.id)))
      for finyear in finyears:
        wpcsv=''
        wphtml=''
        rejectedhtml=''
        invalidhtml=''
        pendinghtml=''
        rejectedcsv=''
        invalidcsv=''
        pendingcsv=''
        wpcsv+="vilCode,hhdCode,zname,work,workCode,totalWage_musterStatus,dateTo_ftoSign_creditedDate,sNo\n"
        rejectedcsv+="vilCode,hhdCode,zname,work,workCode,totalWage_musterStatus,dateTo_ftoSign_creditedDate,sNo\n"
        invalidcsv+="vilCode,hhdCode,zname,work,workCode,totalWage_musterStatus,dateTo_ftoSign_creditedDate,sNo\n"
        pendingcsv+="vilCode,hhdCode,zname,work,workCode,totalWage_musterStatus,dateTo_ftoSign_creditedDate,sNo\n"
        tableCols=["vil","hhd","name","Name of work","workCode","wage_status","dateTo_ftoSign_credited","sNo"]

        workRecords=WorkDetail.objects.filter(muster__panchayat=eachPanchayat,muster__finyear=finyear).order_by('zvilCode','zjcNo','creditedDate')
        wpdata=[]
        rejecteddata=[]
        invaliddata=[]
        pendingdata=[]
        for wd in workRecords:
          wprow=[]
          workName=wd.muster.workName.replace(","," ")
          workCode=wd.muster.workCode
          wagelistArray=wd.wagelist.all()
          if len(wagelistArray) > 0:
            wagelist=wagelistArray[len(wagelistArray) -1 ]
          else:
            wagelist=''
          if wd.worker is not None:
            applicantName=wd.worker.name.replace(",","")
          else:
            applicantName=wd.zname.replace(",","")
          work=workName+"/"+str(wd.muster.musterNo)
          wageStatus=str(wd.totalWage).split(".")[0]+"/"+wd.musterStatus
          srNo=str(wd.id)
          if wd.muster.dateTo is not None:
            dateTo=str(wd.muster.dateTo.strftime("%d/%m/%Y"))
          else:
            dateTo="FTOnotgenerated"
          if wd.creditedDate is not None:
            creditedDate=str(wd.creditedDate.strftime("%d/%m/%y"))
          else:
            creditedDate="NotCred"
          if wd.muster.paymentDate is not None:
            paymentDate=str(wd.muster.paymentDate.strftime("%d/%m/%y"))
          else:
            paymentDate=""
          dateString="%s / %s / %s" %(dateTo,paymentDate,creditedDate)
          wpcsv+="%s,%s,%s,%s,%s,%s,%s,%s" % (wd.zvilCode,str(wd.zjcNo),applicantName,work,workCode,wageStatus,dateString,srNo)
          wpcsv+="\n"
          wprow.extend([wd.zvilCode,str(wd.zjcNo),applicantName,work,workCode,wageStatus,dateString,srNo])
          wpdata.append(wprow)
          if wd.musterStatus == 'Rejected':
            rejectedcsv+="%s,%s,%s,%s,%s,%s,%s,%s\n" % (wd.zvilCode,str(wd.zjcNo),applicantName,work,workCode,wageStatus,dateString,srNo)
            rejecteddata.append(wprow)
          if wd.musterStatus == 'Invalid Account':
            invalidcsv+="%s,%s,%s,%s,%s,%s,%s,%s\n" % (wd.zvilCode,str(wd.zjcNo),applicantName,work,workCode,wageStatus,dateString,srNo)
            invaliddata.append(wprow)
          if wd.musterStatus == '':
            pendingcsv+="%s,%s,%s,%s,%s,%s,%s,%s\n" % (wd.zvilCode,str(wd.zjcNo),applicantName,work,workCode,wageStatus,dateString,srNo)
            pendingdata.append(wprow)
    
        savePanchayatReportWrapper(logger,finyear,eachPanchayat,tableCols,"workPayment","wp",wpdata,wpcsv)
        savePanchayatReportWrapper(logger,finyear,eachPanchayat,tableCols,"rejectedPayment","rp",rejecteddata,rejectedcsv)
        savePanchayatReportWrapper(logger,finyear,eachPanchayat,tableCols,"invalidPayment","ip",invaliddata,invalidcsv)
        savePanchayatReportWrapper(logger,finyear,eachPanchayat,tableCols,"pendingPayment","pp",pendingdata,pendingcsv)

      


  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
