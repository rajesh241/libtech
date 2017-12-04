from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
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

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,PanchayatReport,LibtechTag,PanchayatStat,PanchayatCrawlQueue

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-d', '--download', help='Download the Status', required=False,action='store_const', const=1)
  parser.add_argument('-g', '--gather', help='Download the Status', required=False,action='store_const', const=1)
  parser.add_argument('-f', '--finyear', help='Financial year for which data needs to be crawld', required=True)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)

  args = vars(parser.parse_args())
  return args


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  finyear=args['finyear']
  stateCodes=['05']
  stateCodes=[]
  stateCodes.append(args['stateCode'])
  outdir="/tmp/datafy18/"
  stateCodes=['18','24','31','33']
  stateCodes=['34','32']
  stateCodes=['27']
  stateCodes=['24','27','31','32','33','34','15','18','16','05','17']
  if args['gather']:
    for stateCode in stateCodes:
      logger.info(stateCode)
      i=0
      outcsv=''
      outcsv+="i,panchayatCode,state,district,block,panchayat,workDays,accuracy,musters\n"
      myState=State.objects.filter(code=stateCode).first()
      fileDir="%s/%s/" % (outdir,myState.slug)
      cmd="mkdir -p %s " % (fileDir) 
      os.system(cmd)
      myPanchayatCrawlQueues=PanchayatCrawlQueue.objects.filter(panchayat__block__district__state__code=stateCode,status='5').order_by("panchayat__accuracyIndex")
      myLibtechTag=LibtechTag.objects.filter(name="August 2017 Hearing")
      myPanchayats=Panchayat.objects.filter(block__district__state__code=stateCode,libtechTag__in=myLibtechTag)
      j=len(myPanchayats)
      for eachPanchayat in myPanchayats:
        logger.info("Processing : %s panchayat: %s " % (str(j),eachPanchayat.name))
        dcReport=PanchayatReport.objects.filter(panchayat=eachPanchayat,finyear=finyear,reportType="delayCompensationCSV").first()
        wpReport=PanchayatReport.objects.filter(panchayat=eachPanchayat,finyear=finyear,reportType="workPaymentDelayAnalysis").first()
        isDownload=False
        srNo=0
        accuracyIndex=eachPanchayat.accuracyIndex
        if (dcReport is not None) and (wpReport is not None):
          if ( int(accuracyIndex) >= 0 ) and ( int(accuracyIndex) <= 500 ):
            isDownload=True 
            i=i+1
            srNo=i
        logger.info("Data Accurate %s " % str(accuracyIndex))
        if isDownload== True:
          myPanchayatStat=PanchayatStat.objects.filter(panchayat=eachPanchayat,finyear=finyear).first()
          libtechWorkDays=myPanchayatStat.libtechWorkDays
          totalMusters=myPanchayatStat.mustersTotal
          outcsv+="%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %(str(srNo),eachPanchayat.code,eachPanchayat.block.district.state.slug,eachPanchayat.block.district.slug,eachPanchayat.block.slug,eachPanchayat.slug,str(libtechWorkDays),str(accuracyIndex),str(totalMusters))
          if args['download']:
            dcReportURL=dcReport.reportFile.url
            wpReportURL=wpReport.reportFile.url
            filename="%s_p%s_%s.csv" % ('dc',str(i),finyear)
            cmd="cd %s && wget -O %s %s " %(fileDir,filename,dcReportURL) 
            logger.info(cmd)
            os.system(cmd)
            filename="%s_p%s_%s.csv" % ('wp',str(i),finyear)
            filepath="/tmp/final/%s/" % (eachPanchayat.block.district.state.slug)
            cmd="cd %s && wget -O %s %s " %(fileDir,filename,wpReportURL) 
            logger.info(cmd)
            os.system(cmd)
        j=j-1  
      with open("%s/%s.csv" % (fileDir,myState.slug),"w") as f:
        f.write(outcsv)
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
