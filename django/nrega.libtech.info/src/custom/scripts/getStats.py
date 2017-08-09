from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
from customSettings import repoDir,djangoDir,djangoSettings,jobCardRegisterTimeThreshold
import requests
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getCurrentFinYear
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q,Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,PanchayatReport,PanchayatStat,WorkDetail,Muster,Applicant

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-d', '--download', help='Download the Status', required=False,action='store_const', const=1)
  parser.add_argument('-p', '--process', help='Process the Status', required=False,action='store_const', const=1)
  parser.add_argument('-c', '--calculate', help='Calculate the Stats', required=False,action='store_const', const=1)

  args = vars(parser.parse_args())
  return args
def validateStatsHTML(myhtml):
  error=None
  statsTable=None
  htmlsoup=BeautifulSoup(myhtml,"html.parser")
  tables=htmlsoup.findAll('table')
  for table in tables:
    if "Persondays Generated so far" in str(table):
      statsTable=table
  if statsTable is None:
    error="Stats Table not found"
  return error,statsTable



def main():
  reportType="nicStatsHTML"
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  url = "http://164.100.129.6/netnrega/dynamic_account_details.aspx"
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  stateCode=[args['stateCode']]

  #stateCode=['34','33','17','18','05','27','15','24','16','31','32']
  if args['download']:
    if stateCode is not None:
      #myPanchayats=Panchayat.objects.filter(Q (crawlRequirement="FULL")  &  (Q (statsCrawlDate__lt = jobCardRegisterTimeThreshold) | Q(statsCrawlDate__isnull = True ) ) & Q (block__district__state__code__in=stateCode)).order_by('statsCrawlDate')[:limit]
      myPanchayats=Panchayat.objects.filter(Q (crawlRequirement="FULL")  &  (Q(statsCrawlDate__isnull = True ) ) & Q (block__district__state__code__in=stateCode)).order_by('-block__district__state__code')[:limit]
    else:
      myPanchayats=Panchayat.objects.filter(Q (crawlRequirement="FULL")  &  (Q (statsCrawlDate__lt = jobCardRegisterTimeThreshold) | Q(statsCrawlDate__isnull = True ) ) ).order_by('statsCrawlDate')[:limit]
   
    finyear=getCurrentFinYear()
    logger.info("Total Panchayats  %s " % str(len(myPanchayats)))
    i=0
    for eachPanchayat in myPanchayats:
      i=i+1
      logger.info("%s of Total %s  Panchayat: %s, PanchayatCode: %s " % (str(i),str(len(myPanchayats)),eachPanchayat.name, eachPanchayat.code)) 
      statsURL="http://mnregaweb4.nic.in/netnrega/all_lvl_details_new.aspx"
      statusURL="%s?panchayat_code=%s&panchayat_name=%s&block_code=%s&block_name=%s&district_code=%s&district_name=%s&state_code=%s&state_name=%s&page=p&fin_year=2014-2015" % (statsURL,eachPanchayat.code,eachPanchayat.name,eachPanchayat.block.code,eachPanchayat.block.name,eachPanchayat.block.district.code,eachPanchayat.block.district.name,eachPanchayat.block.district.state.code,eachPanchayat.block.district.state.name)
      logger.info(statusURL) 
   
      try:
        r  = requests.get(statusURL)
        error=0
      except requests.exceptions.RequestException as e:  # This is the correct syntax
        logger.info(e) 
        error=1
      if error==0:
        myhtml=r.text
        error,statsTable=validateStatsHTML(myhtml)
        if error is None:
          logger.info("Successfully Downloaded")
          outhtml=''
          outhtml+=stripTableAttributes(statsTable,"statsTable")
          title="NIC Panchayat Statistics state:%s District:%s block:%s panchayat: %s  " % (eachPanchayat.block.district.state.name,eachPanchayat.block.district.name,eachPanchayat.block.name,eachPanchayat.name)
          outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
          try:
            outhtml=outhtml.encode("UTF-8")
          except:
            outhtml=outhtml
          filename="nicStats_%s_%s_%s.html" % (eachPanchayat.slug,eachPanchayat.code,finyear)
          savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,outhtml)
      eachPanchayat.statsCrawlDate=timezone.now()
      eachPanchayat.save()
   
  if args['process']:
    logger.info("Procesing Panchayat Stats")
    curfinyear=getCurrentFinYear()
     
    myPanchayats=Panchayat.objects.filter( Q(statsCrawlDate__isnull=False)   )[:limit]
    for eachPanchayat in myPanchayats:
      logger.info(eachPanchayat.name+","+eachPanchayat.code)
      panchayatReport=PanchayatReport.objects.filter(reportType=reportType,finyear=curfinyear,panchayat=eachPanchayat).first()
      statFound=0
      if panchayatReport is not None:
        logger.info("Panchayat Report Exists")
        myhtml=panchayatReport.reportFile.read()  
        #myhtml=eachPanchayat.jobcardRegisterFile.read()
        htmlsoup=BeautifulSoup(myhtml,"html.parser")
        rows=htmlsoup.findAll("tr")
        nicTotalApplicants=None
        for row in rows:
          if "Total No. of Workers" in str(row):
            cols=row.findAll("td")
            wArray=[]
            for col in cols:
              wArray.append(col.text.lstrip().rstrip())
            logger.info(str(wArray))  
            nicTotalApplicants=wArray[1]
            
          if "II             Progress" in str(row):
            statFound=1
            logger.info(str(row)) 
            cols=row.findAll("td")
            fArray=[]
            for col in cols:
              fArray.append(col.text.lstrip().rstrip()[-2:])
            logger.info(str(fArray))  
          if "Persondays Generated so far" in str(row):
            logger.info(str(row)) 
            cols=row.findAll("td")
            fArrayData=[]
            for col in cols:
              fArrayData.append(col.text.lstrip().rstrip().replace(",",""))
            logger.info(str(fArrayData))

      if statFound == 1:
        for i,finyear in enumerate(fArray):
          if i != 0:
            workDays=fArrayData[i]
            libtechWorkDays=WorkDetail.objects.filter(muster__panchayat=eachPanchayat,muster__finyear=finyear).aggregate(Sum('daysWorked')).get('daysWorked__sum')
            libtechTotalMusters=Muster.objects.filter(panchayat=eachPanchayat,finyear=finyear).count()
            libtechTotalApplicants=Applicant.objects.filter(panchayat=eachPanchayat).count()
            logger.info("Finyear:%s   WorkDays: %s libtechWorkDays: %s " %(finyear,str(workDays),str(libtechWorkDays)))
            mypanchayatStat=PanchayatStat.objects.filter(finyear=finyear,panchayat=eachPanchayat).first()
            if mypanchayatStat is None:
              PanchayatStat.objects.create(finyear=finyear,panchayat=eachPanchayat)
            myStat=PanchayatStat.objects.filter(finyear=finyear,panchayat=eachPanchayat).first()
            myStat.nicWorkDays=workDays
            myStat.libtechWorkDays=libtechWorkDays
            myStat.save()
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
