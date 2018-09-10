from bs4 import BeautifulSoup
import requests
import os
import sys
import re
import urllib.request
import django
from subprocess import call,Popen

from django.core.wsgi import get_wsgi_application
from django.db.models import Count,Sum
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,logDir
#from crawlFunctions import getAPJobcardData,computeWorkPaymentStatus,crawlWagelists,parseMuster,getAPJobcardData,processAPJobcardData,computeJobcardStat,getJobcardRegister1
from crawlFunctions import getJobcardRegister1,jobcardRegister,saveJobcardRegisterTelangana,processJobcardRegisterTelangana
from reportFunctions import createJobcardReport
from nregaFunctions import is_ascii
from libtechInit import libtechLoggerFetch
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
from wrappers.logger import loggerFetch
sys.path.append(djangoDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
# This is so Django knows where to find stuff.
# This is so my local_settings.py gets loaded.
django.setup()
from nrega.models import State,District,Block,Panchayat,PaymentInfo,LibtechTag,CrawlQueue,Jobcard,APWorkPayment,Wagelist
from django.contrib.auth.models import User


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-t', '--test', help='Test Function can be used to run any script', required=False, action='store_const', const=1)
  parser.add_argument('-s', '--subprocess', help='Run a Sub Process', required=False, action='store_const', const=1)
  parser.add_argument('-sp', '--selectPanchayats', help='Select Panchayats Randomly', required=False, action='store_const', const=1)
  parser.add_argument('-gh', '--getHindi', help='Select Panchayats Randomly', required=False, action='store_const', const=1)
  parser.add_argument('-ti', '--testInput', help='Log level defining verbosity', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logFileName="debug.log"
  logger = libtechLoggerFetch(args.get('log_level'),filename=logFileName)
  logger.debug("hey this is working")
  logger.info("THis is info message")
  logger.info('args: %s', str(args))
  s=''
  if args['getHindi']:
    myobjs=Block.objects.all()
    for obj in myobjs:
      if is_ascii(obj.name) is False:
        logger.info(obj.name)
        s+="%s,%s,%s,%s\n" % (str(obj.code),obj.district.state.name,obj.district.name,obj.name)
    with open("/tmp/hindiBlocks.csv","w") as f:
      f.write(s)
  if args['subprocess']:
    logger.info("Running Sub process command")
    proc = Popen(["sleep 50"], shell=True,stdin=None, stdout=None, stderr=None, close_fds=True)
    logger.info("Exiting Program")
    
  if args['selectPanchayats']:
    myLibtechTag=LibtechTag.objects.filter(name="demoTest").first()
    logger.info(myLibtechTag)
    states=State.objects.all()
    i=0
    for eachState in states:
      panchayats=Panchayat.objects.filter(block__district__state=eachState).order_by('?')[:3]
      for eachPanchayat in panchayats:
        i=i+1
        logger.info("%s-%s-%s-%s'%s" % (str(i),eachPanchayat.block.district.state.name,eachPanchayat.block.district.name,eachPanchayat.block.name,eachPanchayat.name))
    #    eachPanchayat.libtechTag.add(myLibtechTag)
        eachPanchayat.save()
    libtechTagArray=[myLibtechTag.id]
    panchayats=Panchayat.objects.filter(libtechTag__id__in=libtechTagArray)
    logger.info("Total Demo Panchayats %s " % str(len(panchayats)))
    for eachPanchayat in panchayats:
    #  eachPanchayat.libtechTag.remove(myLibtechTag)
      logger.info("%s-%s-%s'%s" % (eachPanchayat.block.district.state.name,eachPanchayat.block.district.name,eachPanchayat.block.name,eachPanchayat.name))
      CrawlQueue.objects.create(panchayat=eachPanchayat)
    logger.info("Total Demo Panchayats %s " % str(len(panchayats)))
      
  if args['test']:
    panchayatCode=args['testInput']
    eachPanchayat=Panchayat.objects.filter(code=panchayatCode).first()
    saveJobcardRegisterTelangana(logger,eachPanchayat)
    processJobcardRegisterTelangana(logger,eachPanchayat)
    exit(0)
    myobjs=Wagelist.objects.all()
    for obj in myobjs:
      dm=obj.downloadManager
      dm.isProcessed=False
      dm.save()
    exit()
    incode=args['testInput']
    logger.info("In tet")
    finyear='19'
    eachPanchayat=Panchayat.objects.filter(code=incode).first()
    logger.info(eachPanchayat.id)
    myhtml=jobcardRegister(logger,eachPanchayat=eachPanchayat) 
    with open("/tmp/b.html","wb") as f:
      f.write(myhtml)
    exit(0)
    s=''
    s+="panchayat,totalJobcards,activeJobcards,daysworked,totalWages\n"
    objs=APWorkPayment.objects.filter(jobcard__panchayat__block__code=blockCode,finyear=finyear).values("jobcard__panchayat__code").annotate(dcount=Sum('daysWorked'),pcount=Sum('payorderAmount'),jcount=Count('jobcard',distinct=True))
    for obj in objs:
      logger.info(obj)
      pcode=obj['jobcard__panchayat__code']
      activeJobcards=obj['jcount']
      totalWages=obj['pcount']
      daysWorked=obj['dcount']
      eachPanchayat=Panchayat.objects.filter(code=pcode).first()
      totalJobcards=len(Jobcard.objects.filter(panchayat=eachPanchayat))
      s+="%s,%s,%s,%s,%s\n" % (eachPanchayat.name,str(totalJobcards),str(activeJobcards),str(daysWorked),str(totalWages))
    with open('/tmp/stats.csv',"w") as f:
      f.write(s)
    exit(0)
    memberCode="jsk"
    password="jsk12345"
    email="libtech.stanford@gmail.com"
    myUser=User.objects.create_user(username=memberCode,email=email,password=password)
    exit(0)
    jobcard=args['testInput']
    myJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
    computeJobcardStat(logger,myJobcard.id,"16")
    exit(0)
    testID=args['testInput']
    myPanchayats=Panchayat.objects.filter(block__code="0203020")
    for eachPanchayat in myPanchayats:
      createJobcardReport(logger,eachPanchayat,"19")
    exit(0)
    myobjs=Jobcard.objects.filter(panchayat__block__code=testID,isVillageInfoMissing=True)
    for obj in myobjs:
      obj.isDownloaded=False
      obj.save()
    exit(0)
    getAPJobcardData(logger,testID)
    exit(0)
#   eachPanchayat=Panchayat.objects.filter(code=testID).first()
#   finyear='18'
#   crawlWagelists(logger,eachPanchayat,finyear)
#   exit(0)
    computeWorkPaymentStatus(logger,int(testID))
    exit(0)
    panchayatCodes=['3406004010','3406004002','3405008005']
    s="panchayatName,status,finyear,count\n"
    for eachCode in panchayatCodes:
      eachPanchayat=Panchayat.objects.filter(code=eachCode).first()
      finyears=['16','17','18','19']
      for finyear in finyears:
        wdArray=[]
        rejectedpinfos=PaymentInfo.objects.filter(workDetail__worker__jobcard__panchayat=eachPanchayat,status='Rejected',workDetail__muster__finyear=finyear).values('workDetail').annotate(dcount=Count('pk'))
        for pinfo in rejectedpinfos:
          wdArray.append(pinfo['workDetail'])
        totalRejectedTransactions=len(rejectedpinfos)
        rejectedpinfos=PaymentInfo.objects.filter(workDetail__worker__jobcard__panchayat=eachPanchayat,status='Invalid Account',workDetail__muster__finyear=finyear).values('workDetail').annotate(dcount=Count('pk'))
        for pinfo in rejectedpinfos:
          wdArray.append(pinfo['workDetail'])
        totalRejectedTransactions+=len(rejectedpinfos)
        logger.info(wdArray)
        pinfos=PaymentInfo.objects.filter(workDetail__worker__jobcard__panchayat=eachPanchayat,workDetail__in=wdArray).values('status').annotate(dcount=Count('pk'))
        noOfRejected=0
        for pinfo in pinfos:
          status=pinfo['status']
          if status!='Credited':
            noOfRejected+=pinfo['dcount']
        s+="%s,%s,%s,%s\n" % (eachPanchayat.name,finyear,str(totalRejectedTransactions),str(noOfRejected))
    with open('/tmp/stat1.csv','w') as f:
      f.write(s)
      
    logger.info("Running Test Function")
    
    exit(0)
    objID=110
    getAPJobcardData(logger,objID)
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
