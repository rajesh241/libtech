from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
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

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,PanchayatReport,LibtechTag,PanchayatStat

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
  parser.add_argument('-f', '--finyear', help='Financial year for which data needs to be crawld', required=True)
  parser.add_argument('-g', '--gather', help='Gather all the Reports', required=True)
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
  stateCodes=['33','34','27','24','15','18','16','31','05','17']
  stateCodes=['15']
  myLibtechTag=LibtechTag.objects.filter(name="August 2017 Hearing")
  tagArray=[]
  for eachTag in myLibtechTag:
    print(eachTag.id)
    tagArray.append(eachTag)

#  myPanchayats=Panchayat.objects.filter(block__district__state__code='34',crawlRequirement="FULL",libtechTag__in=tagArray)
 # stateCodes=[args['stateCode']]
  stateCodes=['33','34','27','24','15','18','16','31','05','17','32']
  consolidatedcsv=''
  consolidatedcsv="srno,state,district,block,panchayat,nicWorkDays,libtechWorkDays,accuracy\n"
  for stateCode in stateCodes:
    myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',block__district__state__code=stateCode,libtechTag__in=tagArray)[:limit]
    myState=State.objects.filter(code=stateCode).first()
    stateName=myState.slug
    i=0
    j=0
    outcsv=''  
    outcsv="srno,district,block,panchayat,nicWorkDays,libtechWorkDays,accuracy\n"
    for eachPanchayat in myPanchayats:
      i=i+1
      myMusters=Muster.objects.filter(panchayat=eachPanchayat,isDownloaded=0,finyear='17')
      undownloadedMusters=len(myMusters)
      myMusters=Muster.objects.filter(panchayat=eachPanchayat,isDownloaded=1,finyear='17')
      totalMusters=len(myMusters)
      logger.info("**********************************************************************************")
      logger.info("Createing work Payment report for panchayat: %s panchayatCode: %s ID: %s" % (eachPanchayat.name,eachPanchayat.code,str(eachPanchayat.id)))
      dcReport=PanchayatReport.objects.filter(panchayat=eachPanchayat,finyear='18',reportType="delayCompensationCSV").first()
      wpReport=PanchayatReport.objects.filter(panchayat=eachPanchayat,finyear='18',reportType="workPaymentDelayAnalysis").first()
      if (dcReport is not None) and (wpReport is not None):
        myPanchayatStat=PanchayatStat.objects.filter(panchayat=eachPanchayat,finyear='18').first()
        if myPanchayatStat is not None:
          nicWorkDays=myPanchayatStat.nicWorkDays
          libtechWorkDays=myPanchayatStat.libtechWorkDays
          try:
            accuracy=int(libtechWorkDays*100/nicWorkDays)
          except:
            accuracy=0
        else:
          nicWorkDays=''
          libtechWorkDays=''
          accuracy=0
          
        outcsv+="%s,%s,%s,%s,%s,%s,%s,%s,%s" %(str(i),eachPanchayat.block.district.slug,eachPanchayat.block.slug,eachPanchayat.slug,str(nicWorkDays),str(libtechWorkDays),str(accuracy),str(totalMusters),str(undownloadedMusters))
        consolidatedcsv+="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %(str(i),stateName,eachPanchayat.block.district.slug,eachPanchayat.block.slug,eachPanchayat.slug,str(nicWorkDays),str(libtechWorkDays),str(accuracy),str(totalMusters),str(undownloadedMusters))
        outcsv+="\n"
        consolidatedcsv+="\n"
        logger.info("Accurace is %s " % str(accuracy))
        if ( int(accuracy) >= 90 ) and ( int(accuracy) <= 110 ):
          eachPanchayat.isDataAccurate=True
          eachPanchayat.save()
          j=j+1
          if args['download']:
            dcReportURL=dcReport.reportFile.url
            wpReportURL=wpReport.reportFile.url
            filename="%s_p%s_%s.csv" % ('dc',str(j),finyear)
            filepath="/tmp/final/%s/" % (eachPanchayat.block.district.state.slug)
            cmd="mkdir -p %s && cd %s && wget -O %s %s " %(filepath,filepath,filename,dcReportURL) 
            logger.info(cmd)
            os.system(cmd)
            filename="%s_p%s_%s.csv" % ('wp',str(j),finyear)
            filepath="/tmp/final/%s/" % (eachPanchayat.block.district.state.slug)
            cmd="mkdir -p %s && cd %s && wget -O %s %s " %(filepath,filepath,filename,wpReportURL) 
            logger.info(cmd)
            os.system(cmd)
    with open("/tmp/%s.csv" % stateName,"w") as f:
      f.write(outcsv)
  with open("/tmp/%s.csv" % "consolidated","w") as f:
    f.write(consolidatedcsv)

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
