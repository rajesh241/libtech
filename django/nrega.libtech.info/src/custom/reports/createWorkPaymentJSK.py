from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
sys.path.insert(0, "./../scripts")
from customSettings import repoDir,djangoDir,djangoSettings

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,savePanchayatReport
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,PanchayatReport

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-f', '--finyear', help='Financial year for which data needs to be crawld', required=True)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-cr', '--crawlRequirement', help='Kindly put the tag of crawlRequiremtn that panchayats are tagged with, by default it will do it for panchayats which are tagged with crawlRequirement of FULL', required=False)
  parser.add_argument('-p', '--panchayatCode', help='panchaytCode for which the numbster needs to be downloaded', required=False)

  args = vars(parser.parse_args())
  return args


def main():
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
  finyear=args['finyear']

  stateCodes=['33','34','16','27','24','15','18','35']
  stateCodes=['33','34','27','24','15','18',]
  stateCodes=['16','31','05','17']
  stateCodes=['15']
  stateCodes=[args['stateCode']]
  stateCode=args['stateCode']
  panchayatCode=args['panchayatCode']
  logger.info(panchayatCode)
  if panchayatCode is not None:
    myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',code=panchayatCode)
  elif stateCode is not None:
    myPanchayats=Panchayat.objects.filter(crawlRequirement=crawlRequirement,block__district__state__code=stateCode)
  else:
    myPanchayats=Panchayat.objects.filter(crawlRequirement=crawlRequirement)[:limit]
#  else:
#    myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL')[:limit]
  for eachPanchayat in myPanchayats:
    logger.info("**********************************************************************************")
    logger.info("Createing work Payment report for panchayat: %s panchayatCode: %s ID: %s" % (eachPanchayat.name,eachPanchayat.code,str(eachPanchayat.id)))
    outcsv=''
    rejectedcsv=''
    invalidcsv=''
    outcsv+="vilCode,hhdCode,zname,work,workCode,wagelist,totalWage_musterStatus,dateTo_ftoSign_creditedDate,sNo"
    rejectedcsv+="vilCode,hhdCode,zname,work,workCode,wagelist,totalWage_musterStatus,dateTo_ftoSign_creditedDate,sNo\n"
    invalidcsv+="vilCode,hhdCode,zname,work,workCode,wagelist,totalWage_musterStatus,dateTo_ftoSign_creditedDate,sNo\n"
    outcsv+="\n"
    workRecords=WorkDetail.objects.filter(muster__block__panchayat__id=eachPanchayat.id,muster__finyear=finyear)
    workRecords=WorkDetail.objects.filter(muster__panchayat=eachPanchayat,muster__finyear=finyear).order_by('zvilCode','zjcNo','creditedDate')
    logger.info("Total Work Records: %s " %str(len(workRecords)))
    for wd in workRecords:
      workName=wd.muster.workName.replace(","," ")
      workCode=wd.muster.workCode
      wagelistArray=wd.wagelist.all()
      if len(wagelistArray) > 0:
        wagelist=wagelistArray[len(wagelistArray) -1 ]
      else:
        wagelist=''
      
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
      outcsv+="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (wd.zvilCode,str(wd.zjcNo),applicantName,work,workCode,wagelist,wageStatus,dateString,srNo,wd.zjobcard)
      outcsv+="\n"

      if wd.musterStatus == 'Rejected':
        rejectedcsv+="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (wd.zvilCode,str(wd.zjcNo),applicantName,work,workCode,wagelist,wageStatus,dateString,srNo,wd.zjobcard)
      if wd.musterStatus == 'Invalid Account':
        invalidcsv+="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (wd.zvilCode,str(wd.zjcNo),applicantName,work,workCode,wagelist,wageStatus,dateString,srNo,wd.zjobcard)
  
    try:
      outcsv=outcsv.encode("UTF-8")
    except:
      outcsv=outcsv
    try:
      rejectedcsv=rejectedcsv.encode("UTF-8")
    except:
      rejectedcsv=rejectedcsv
    try:
      invalidcsv=invalidcsv.encode("UTF-8")
    except:
      invalidcsv=invalidcsv

    filename="/tmp/%s_%s.csv" % (eachPanchayat.slug,finyear)
    with open(filename,"wb") as f:
      f.write(outcsv)
    filename="/tmp/%s_rejected_%s.csv" % (eachPanchayat.slug,finyear)
    with open(filename,"wb") as f:
      f.write(rejectedcsv)
    filename="/tmp/%s_invalid_%s.csv" % (eachPanchayat.slug,finyear)
    with open(filename,"wb") as f:
      f.write(invalidcsv)
   #  csvfilename=eachPanchayat.slug+"_"+finyear+"_wp.csv"
   #  reportType="workPayment"
   #  savePanchayatReport(logger,eachPanchayat,finyear,reportType,csvfilename,outcsv)

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
 
