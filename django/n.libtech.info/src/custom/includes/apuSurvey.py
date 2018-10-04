
import re
import shutil
import unicodecsv as csv
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
#import csv
from io import BytesIO
from bs4 import BeautifulSoup
from customSettings import repoDir,djangoDir,djangoSettings,telanganaThresholdDate,telanganaJobcardTimeThreshold,searchIP,wagelistTimeThreshold,musterTimeThreshold,apStateCode
import sys
import time
import os
from queue import Queue
from threading import Thread
import threading
import requests
import time
import random
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from wrappers.logger import loggerFetch
import datetime
from os import listdir
import pandas as pd
from itertools import chain
import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import F,Q,Count,Sum
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,Village,Jobcard,Worker,Wagelist,PanchayatStat,FTO,PaymentInfo,APWorkPayment,LibtechTag,GenericReport
from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,getCurrentFinYear,saveBlockReport,savePanchayatReport,correctDateFormat,getjcNumber,getVilCode,getEncodedData,getCenterAlignedHeading,getTelanganaDate,table2csv,csv2Table,changeLanguage

musterregex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
statsURL="http://mnregaweb4.nic.in/netnrega/all_lvl_details_new.aspx"
transactionStartDate=datetime.datetime.strptime('15082017', "%d%m%Y").date()
transactionEndDate=datetime.datetime.strptime('15082018', "%d%m%Y").date()
isWorkCode = False

def saveGenericReport(logger,eachPanchayat,libtechTag,filecontent,filename=None):
  myTag=LibtechTag.objects.filter(name=libtechTag).first()
  if filename is None:
    filename="%s_%s.csv" % (eachPanchayat.slug,myTag.slug)
  if myTag is not None:
    myReport=GenericReport.objects.filter(panchayat=eachPanchayat,libtechTag=myTag).first()
  if myReport is None:
    myReport=GenericReport.objects.create(panchayat=eachPanchayat,libtechTag=myTag)   
  myReport.reportFile.save(filename, ContentFile(filecontent))
  myReport.save()

def apJobcardProcess1(logger,objID):
  eachJobcard=Jobcard.objects.filter(id=objID).first()
  try:
    myhtml=eachJobcard.jobcardFile.read()
    readError=None
  except:
    readError="No File Found"
  if readError is None: 
    stateShortCode=eachJobcard.panchayat.block.district.state.stateShortCode
    htmlsoup=BeautifulSoup(myhtml,"lxml")
    locationTag=htmlsoup.find('h2')
    if locationTag is not None:
      locationText=locationTag.text.lstrip().rstrip()
      if 'Habitation' in locationText:
        villageName=locationText.split("Habitation :")[1].lstrip().strip()
        logger.debug(villageName)
        myVillage=Village.objects.filter(panchayat=eachJobcard.panchayat,name=villageName).first()
        if myVillage is None:
          myVillage=Village.objects.create(panchayat=eachJobcard.panchayat,name=villageName)
        eachJobcard.village=myVillage
        logger.debug("Village found")
    workerTable=htmlsoup.find('table',id='workerTable')
    if workerTable is not None:
      rows=workerTable.findAll('tr')
      for row in rows:
        cols=row.findAll('td')
        if len(cols) > 0:
          applicantNo=cols[1].text.lstrip().rstrip()
          name=cols[2].text.lstrip().rstrip()
          age=cols[3].text.lstrip().rstrip()
          gender=cols[4].text.lstrip().rstrip()
          relationship=cols[5].text.lstrip().rstrip()
          myWorker=Worker.objects.filter(jobcard=eachJobcard,applicantNo=applicantNo,name=name).first()
          if myWorker is None:
            Worker.objects.create(jobcard=eachJobcard,name=name,applicantNo=applicantNo)
          myWorker=Worker.objects.filter(jobcard=eachJobcard,name=name,applicantNo=applicantNo).first()
          logger.debug(applicantNo)
          myWorker.applicantNo=applicantNo
          myWorker.gender=gender
          myWorker.age=age
          myWorker.relationship=relationship
          myWorker.save()

def updateAPWorkPayment(logger,eachPanchayat):
  myobjs=APWorkPayment.objects.filter(jobcard__panchayat=eachPanchayat)
  for obj in myobjs:
    applicantNo=obj.applicantNo
    eachJobcard=obj.jobcard
    myWorker=Worker.objects.filter(jobcard=eachJobcard,applicantNo=applicantNo).first()
    if myWorker is not None:
      obj.worker=myWorker
      obj.save()
    else:
      logger.debug("Worker not found %s-%s " % (str(obj.id),str(eachJobcard.id)))

def selectWorkersAPU(logger,eachPanchayat):
  limit=1
  return 0
  myobjs=APWorkPayment.objects.filter(worker__jobcard__panchayat=eachPanchayat,worker__is15Days=True,isDelayedPayment=True).values("worker__id").annotate(pcount=Count('pk'))
  logger.info("Total Length of Workers is %s " % (str(len(myobjs))))
  if len(myobjs) > 42:
    sampledObjs=random.sample(list(myobjs),42)
  else:
    sampledObjs = myobjs
  i=0
  for obj in sampledObjs:
    i=i+1
    workerID=obj['worker__id']
    if i <= 21:
      libtechTag=LibtechTag.objects.filter(name="apuSurvey2018MainSampleC30").first()
    else:
      libtechTag=LibtechTag.objects.filter(name="apuSurvey2018ReplacementSampleC30").first()
    eachWorker=Worker.objects.filter(id=workerID).first()
    eachWorker.libtechTag.add(libtechTag)
    eachWorker.isSample=True
    eachWorker.save()
    logger.info("Worker is %s-%s Tag ID %s" % (str(i),str(workerID),str(libtechTag.id)))
  myobjs=APWorkPayment.objects.filter(worker__jobcard__panchayat=eachPanchayat,worker__isSample=False,worker__is15Days=True,isDelayedPayment=False).values("worker__id").annotate(pcount=Count('pk'))
  logger.info("Total Length of Workers is %s " % (str(len(myobjs))))
  if len(myobjs) > 42:
    sampledObjs=random.sample(list(myobjs),42)
  else:
    sampledObjs = myobjs
  i=0
  for obj in sampledObjs:
    i=i+1
    workerID=obj['worker__id']
    if i <= 21:
      libtechTag=LibtechTag.objects.filter(name="apuSurvey2018MainSample").first()
    else:
      libtechTag=LibtechTag.objects.filter(name="apuSurvey2018ReplacementSample").first()
    eachWorker=Worker.objects.filter(id=workerID).first()
    eachWorker.libtechTag.add(libtechTag)
    eachWorker.isSample=True
    eachWorker.save()
    logger.info("Worker is %s-%s Tag ID %s" % (str(i),str(workerID),str(libtechTag.id)))
 
def sampleWorkersAP(logger,eachPanchayat):
  myobjs=APWorkPayment.objects.filter(jobcard__panchayat=eachPanchayat,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).values("jobcard","applicantNo").annotate(tcount=Count('pk'),dcount=Sum('daysWorked'))
  for obj in myobjs:
#    logger.info(obj)
    jobcardID=obj['jobcard']
    eachJobcard=Jobcard.objects.filter(id=jobcardID).first()
    jobcard="~%s" % (eachJobcard.tjobcard)
    if eachJobcard.village is not None:
      village=eachJobcard.village.name
    else:
      village=''
    applicantNo=obj['applicantNo']
    totalTransaction=str(obj['tcount'])
    daysWorked=int(obj['dcount'])
    if daysWorked >= 15:
      myWorker=Worker.objects.filter(jobcard=eachJobcard,applicantNo=applicantNo).first()
      if myWorker is None:
        logger.debug("Jobcard ID is %s-%s name is %s " % (str(eachJobcard.id),eachJobcard.jobcard,str(applicantNo)))
      else:
        myWorker.is15Days=True
        myWorker.save()

def createSampleWorkersReport(logger,eachBlock):
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  a=[]
  a.extend(["panchayat","village","jobcard","caste","tag","name"])
  w.writerow(a)
  myobjs=Worker.objects.filter(jobcard__panchayat__block=eachBlock,isSample=True).order_by("jobcard__panchayat__code")
  for eachWorker in myobjs:
    panchayatName=eachWorker.jobcard.panchayat.name
    libtechTag=eachWorker.libtechTag.first()
    jobcard="~"+eachWorker.jobcard.tjobcard
    applicantNo=eachWorker.applicantNo
    name=eachWorker.name
    caste=eachWorker.jobcard.caste
    headOfFamily=eachWorker.jobcard.headOfHousehold
    wd=APWorkPayment.objects.filter(worker=eachWorker).first()

    if eachWorker.jobcard.village is not None:
      village=eachWorker.jobcard.village.name
    else:
      village=''
    a=[]
    a.extend([panchayatName,village,jobcard,caste,libtechTag.name,wd.name])
    w.writerow(a)
  f.seek(0)
  outcsv=f.getvalue()
  with open("/tmp/apSamples.csv","wb") as f:
    f.write(outcsv)

def createWorkDaysReport(logger,eachPanchayat):
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  a=[]
  a.extend(["panchayat","village","jobcard","name","totalTransaction","daysWorked"])
  w.writerow(a)
  stateCode=eachPanchayat.block.district.state.code
  if stateCode==apStateCode:
    myTag="apuAPWorkDaysReport"
    myobjs=APWorkPayment.objects.filter(jobcard__panchayat=eachPanchayat,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).values("jobcard","name").annotate(tcount=Count('pk'),dcount=Sum('daysWorked'))
    for obj in myobjs:
      logger.info(obj)
      jobcardID=obj['jobcard']
      eachJobcard=Jobcard.objects.filter(id=jobcardID).first()
      jobcard="~%s" % (eachJobcard.tjobcard)
      if eachJobcard.village is not None:
        village=eachJobcard.village.name
      else:
        village=''
      name=obj['name']
      totalTransaction=str(obj['tcount'])
      daysWorked=str(obj['dcount'])
      a=[]
      a.extend([eachPanchayat.name,village,jobcard,name,totalTransaction,daysWorked])
      w.writerow(a)
  else:
    myTag="apuNICWorkDaysReport"
    wds=WorkDetail.objects.filter(worker__jobcard__panchayat=eachPanchayat,muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate).values('worker',"worker__jobcard__village__name","worker__jobcard__jcNo","worker__name").annotate(tcount=Count('pk'),dcount=Sum('daysWorked')).order_by("worker__jobcard__village__name","worker__jobcard__jcNo","worker__name")
    for wd in wds:
      eachWorker=Worker.objects.filter(id=wd['worker']).first()
      jobcard=eachWorker.jobcard
      applicantNo=eachWorker.applicantNo
      name=eachWorker.name
      caste=eachWorker.jobcard.caste
      headOfFamily=eachWorker.jobcard.headOfHousehold
      if eachWorker.jobcard.village is not None:
        village=eachWorker.jobcard.village.name
      else:
        village=''
      totalTransactions=str(wd['tcount'])
      daysWorked=str(wd['dcount'])
      logger.info(wd)
      a=[]
      a.extend([eachPanchayat.name,village,jobcard,name,totalTransactions,daysWorked])
      w.writerow(a)
   
  f.seek(0)
  f.seek(0)
  outcsv=f.getvalue()
  saveGenericReport(logger,eachPanchayat,myTag,outcsv)

def createTransactionReport(logger,eachWorker):
  myTag="surveyTransactionReport"
  s=''
  s1=''
  s+='"name","workName","startDate","endDate","daysWorked","wages","payorderNo","worked y/n","noOfDays","amount","code"\n'
  s1+='"name","workName","startDate","endDate","daysWorked","wages","payorderNo","worked y/n","noOfDays","amount","code"\n'
  tjobcard=eachWorker.jobcard.tjobcard
  logger.info(eachWorker.name)
  myTransactions=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).values("workName").annotate(tcount=Sum('daysWorked'),wcount=Sum('payorderAmount'))
  for eachTransaction in myTransactions:
    workName=eachTransaction['workName']
    totalWorkDays=str(eachTransaction['tcount'])
    totalWages=str(int((eachTransaction['wcount'])))
    logger.info("Work name is %s transaction count is %s " % (workName,totalWorkDays))
    wds=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate,workName=workName).order_by("dateTo")
    i=0
    for wd in wds:
      i=i+1
      name=wd.name
      daysWorked=wd.daysWorked
      wages=int(wd.payorderAmount)
      dateTo=wd.dateTo
      payorderNo=wd.payorderNo
      dateFrom=wd.dateTo-datetime.timedelta(days=wd.daysWorked-1)
      dateFromString=datetime.datetime.strftime(dateFrom,'%d-%m-%Y')
      dateToString=datetime.datetime.strftime(dateTo,'%d-%m-%Y')
      if i == 1:
        dateStartString=dateFromString
      logger.info("Transaction ID %s , dateTo %s dateFrom %s Days WOrked %s" % (str(wd.id),str(wd.dateTo),str(dateFrom),str(daysWorked)))
#      a.extend([name,workName,dateFromString,dateToString,str(daysWorked),str(wages),payorderNo])
      s1+="%s,%s,%s,%s,%s,%s,%s\n" %(name,workName,dateFromString,dateToString,str(daysWorked),str(wages),payorderNo)
    s+="%s,%s,%s,%s,%s,%s,%s\n" %(name,workName,dateStartString,dateToString,str(totalWorkDays),str(totalWages),payorderNo)
  out="~%s\n%s\n%s\n" % (tjobcard,s,s1)
  tjobcardName=slugify(tjobcard+"_"+name)
  panchayatName=eachWorker.jobcard.panchayat.slug
  filename="/tmp/survey/%s/%s.csv" % (panchayatName,tjobcardName)  
  if not os.path.exists(os.path.dirname(filename)):
    os.makedirs(os.path.dirname(filename))
  with open(filename,"w") as fb:
    fb.write(out)

def createAPUWorkPaymentAP(logger,eachPanchayat,finyear=None,eachBlock=None):
  myTag="apuAPWorkPayment"
  finyear=str(finyear)
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  #w = csv.writer(f, newline='',delimiter=',')
  reportType="workPaymentAP"
#  logger.info("Createing extended Rejected Payment ReportsPayment for panchayat: %s panchayatCode: %s ID: %s" % (eachPanchayat.name,eachPanchayat.code,str(eachPanchayat.id)))
  a=[]
#  workRecords=WorkDetail.objects.filter(id=16082209)
  if eachBlock is not None:
    a.extend(["panchayat","tjobcard","heafOfFamily","caste","applicantNo","applicantName","workCode","workName","musterNo","dateTo","daysWorked","accountNo","payorderNo","payorderDate","epayorderno","epayorderDate","payingAgencyDate","creditedDate","disbursedDate","paymentMode","payOrdeAmount","disbursedAmount","dateDiff"])
    w.writerow(a)
    workRecords=APWorkPayment.objects.filter(jobcard__panchayat__block=eachBlock,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).order_by("jobcard__tjobcard","name","epayorderDate")
  else:
    a.extend(["panchayat","tjobcard","heafOfFamily","caste","applicantNo","applicantName","workCode","workName","musterNo","dateTo","daysWorked","accountNo","payorderNo","payorderDate","epayorderno","epayorderDate","payingAgencyDate","creditedDate","disbursedDate","paymentMode","payOrdeAmount","disbursedAmount","dateDiff"])
    w.writerow(a)
    workRecords=APWorkPayment.objects.filter(jobcard__panchayat=eachPanchayat,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).order_by("jobcard__tjobcard","name","dateTo")
  logger.info("Total Work Records: %s " %str(len(workRecords)))

  myobjs=APWorkPayment.objects.filter(jobcard__panchayat=eachPanchayat,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).values("jobcard","name").annotate(tcount=Count('pk'),dcount=Sum('daysWorked'))
  for obj in myobjs:
    logger.info(obj)
    jobcardID=obj['jobcard']
    eachJobcard=Jobcard.objects.filter(id=jobcardID).first()
    name=obj['name']
    totalTransaction=str(obj['tcount'])
    daysWorked=int(obj['dcount'])
    if daysWorked > 10:
      workRecords=APWorkPayment.objects.filter(jobcard=eachJobcard,name=name,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).order_by("jobcard__tjobcard","name","dateTo")
      for wd in workRecords:
        if wd.jobcard is not None:
          panchayatName=wd.jobcard.panchayat.name
        tjobcard1="~%s" % (wd.jobcard.tjobcard)
        dateDiff='0'
        if (wd.creditedDate is not None) and (wd.dateTo is not None):
          dateDiff=str((wd.creditedDate-wd.dateTo).days)
        a=[]
        a.extend([panchayatName,tjobcard1,wd.jobcard.headOfHousehold,wd.jobcard.caste,str(wd.applicantNo),wd.name,wd.workCode,wd.workName,wd.musterNo,str(wd.dateTo),str(wd.daysWorked),wd.accountNo,wd.payorderNo,str(wd.payorderDate),wd.epayorderNo,str(wd.epayorderDate),str(wd.payingAgencyDate),str(wd.creditedDate),str(wd.disbursedDate),wd.modeOfPayment,str(wd.payorderAmount),str(wd.disbursedAmount),dateDiff])
        w.writerow(a)
  f.seek(0)
#  with open("/tmp/a.csv","wb") as f1:
#    shutil.copyfileobj(f, f1)
  outcsv=f.getvalue()
  saveGenericReport(logger,eachPanchayat,myTag,outcsv)
# workers=Worker.objects.filter(jobcard__panchayat=eachPanchayat).order_by("jobcard__jcNo","applicantNo")
# for eachWorker in workers:
#   if eachWorker.jobcard.tjobcard is not None:
#     jobcard="~%s" %(eachWorker.jobcard.tjobcard)
#   else:
#     jobcard=eachWorker.jobcard
#   applicantNo=eachWorker.applicantNo
#   name=eachWorker.name
#   caste=eachWorker.jobcard.caste
#   headOfFamily=eachWorker.jobcard.headOfHousehold
#   if eachWorker.jobcard.village is not None:
#     village=eachWorker.jobcard.village.name
#   else:
#     village=''
#
#   a=[]
#   a.extend([eachPanchayat.name,village,jobcard,applicantNo,name,caste])
#   w.writerow(a)
# 
# f.seek(0)
# outcsv=f.getvalue()
# with open("/tmp/a.csv","wb") as w:
#   w.write(outcsv)

def createJobcardReport(logger,eachPanchayat,finyear,eachBlock=None):
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  reportType="jobcardcsv"
  a=[]
  a.extend(["panchayat","village","jobcard","names","caste","daysWorked19",'payOrderAmount19','disbursedAmount19','pendingAmount19','daysWorked18','payOrderAmount18','disbursedAmount18','pendingAmount18'])
  w.writerow(a)
  if eachBlock is not None:
    jobcards=Jobcard.objects.filter(panchayat__block=eachBlock)
  else:
    jobcards=Jobcard.objects.filter(panchayat=eachPanchayat)
  logger.info("Total Jobcards %s" % str(len(jobcards)))
  for eachJobcard in jobcards:
    if eachJobcard.tjobcard is not None:
      jobcard="~"+eachJobcard.tjobcard
    else:
      jobcard=eachJobcard.jobcard
    workerString=''
    if eachJobcard.village is not None:
      village=eachJobcard.village.name
    else:
      village=''
    caste=eachJobcard.caste
    if eachJobcard.panchayat.block.district.state.code == apStateCode:
      myDaysWorked=APWorkPayment.objects.filter(jobcard=eachJobcard).values("finyear").annotate(dsum=Sum('daysWorked'),psum=Sum('payorderAmount'),csum=Sum('disbursedAmount'))
    else:
      myDaysWorked=WorkPayment.objects.filter(jobcard=eachJobcard).values("finyear").annotate(dsum=Sum('daysWorked'),psum=Sum('totalWage'),csum=Sum('disbursedAmount'))
    daysWorked19=0
    payOrderAmount19=0
    creditedAmount19=0
    pendingAmount19=0
    daysWorked18=0
    payOrderAmount18=0
    creditedAmount18=0
    pendingAmount18=0
    for obj in myDaysWorked:
      if obj['finyear'] == '19':
        daysWorked19=obj['dsum']
        payOrderAmount19=obj['psum']
        creditedAmount19=obj['csum']
        pendingAmount19=payOrderAmount19-creditedAmount19
      if obj['finyear'] == '18':
        daysWorked18=obj['dsum']
        payOrderAmount18=obj['psum']
        creditedAmount18=obj['csum']
        pendingAmount18=payOrderAmount18-creditedAmount18
#myWorkDetails=WorkDetail.objects.filter(worker__jobcard__panchayat__block__id=2639,musterStatus='Rejected').values("worker__jobcard__panchayat__block__id","muster__finyear").annotate(dcount=Count('pk'),tcount=Sum('totalWage'))
    workers=Worker.objects.filter(jobcard=eachJobcard)
    for eachWorker in workers:
      workerString+=eachWorker.name
      workerString+="|"
    a=[]
    a.extend([eachPanchayat.name,village,jobcard,workerString,caste,daysWorked19,payOrderAmount19,creditedAmount19,pendingAmount19,daysWorked18,payOrderAmount18,creditedAmount18,pendingAmount18])
    w.writerow(a)
  f.seek(0)
  outcsv=f.getvalue()
  if eachBlock is not None:
    csvfilename=eachBlock.slug+"_"+finyear+"_jobcards.csv"
    saveBlockReport(logger,eachBlock,finyear,reportType,csvfilename,outcsv)
  else:
    csvfilename=eachPanchayat.slug+"_"+finyear+"_jobcards.csv"
    savePanchayatReport(logger,eachPanchayat,finyear,reportType,csvfilename,outcsv)

def getDiffFTOMuster(logger,eachBlock):
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  a=[]
  a.extend(["panchayat","tjobcard","heafOfFamily","caste","applicantNo","applicantName","workCode","workName","musterNo","dateTo","daysWorked","accountNo","payorderNo","payorderDate","epayorderno","epayorderDate","payingAgencyDate","creditedDate","disbursedDate","paymentMode","payOrdeAmount","disbursedAmount","dateDiff"])
  w.writerow(a)
  logger.info("Generating stats for Block %s " % (eachBlock.name))
#  Booking.objects.annotate(days=DiffDays(CastDate(F('end'))-CastDate(F('start'))) + 1)[0].days
  myobjs=APWorkPayment.objects.filter(jobcard__panchayat__block=eachBlock,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).extra(select={'offset': 'epayorderDate - dateTo'}).order_by('-offset')[:50]
  for wd in myobjs:
    logger.info(wd.id)
    if (wd.dateTo is not None) and (wd.epayorderDate is not None):
      diffDays=(wd.epayorderDate-wd.dateTo).days
    else:
      diffDays=None
    if wd.jobcard is not None:
      panchayatName=wd.jobcard.panchayat.name
    tjobcard1="~%s" % (wd.jobcard.tjobcard)
    dateDiff='0'
    if (wd.creditedDate is not None) and (wd.dateTo is not None):
      dateDiff=str((wd.creditedDate-wd.dateTo).days)
    a=[]
    a.extend([panchayatName,tjobcard1,wd.jobcard.headOfHousehold,wd.jobcard.caste,str(wd.applicantNo),wd.name,wd.workCode,wd.workName,wd.musterNo,str(wd.dateTo),str(wd.daysWorked),wd.accountNo,wd.payorderNo,str(wd.payorderDate),wd.epayorderNo,str(wd.epayorderDate),str(wd.payingAgencyDate),str(wd.creditedDate),str(wd.disbursedDate),wd.modeOfPayment,str(wd.payorderAmount),str(wd.disbursedAmount),diffDays])
    w.writerow(a)
  f.seek(0)
#  with open("/tmp/a.csv","wb") as f1:
#    shutil.copyfileobj(f, f1)
  outcsv=f.getvalue()
  with  open("/tmp/max.csv","wb") as f1:
    f1.write(outcsv)


def justlikethat(logger,eachPanchayat):
  myTag="surveyTransactionReport"
  s=''
  s1=''
  myWorkers=Worker.objects.filter(jobcard__panchayat=eachPanchayat,isSample=True)[:1]
  wid=0
  for eachWorker in myWorkers:
    wid=wid+1
    tjobcard=eachWorker.jobcard.tjobcard
    myTransactions=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).values("workName").annotate(tcount=Sum('daysWorked'),wcount=Sum('payorderAmount'))
    for eachTransaction in myTransactions:
      workName=eachTransaction['workName'].replace(",","")
      totalWorkDays=str(eachTransaction['tcount'])
      totalWages=str(int((eachTransaction['wcount'])))
      logger.info("Work name is %s transaction count is %s " % (workName,totalWorkDays))
 
def createTransactionReportHTML(logger,eachPanchayat):
  myTag="surveyTransactionReport"
  outhtml=''
  myWorkers=Worker.objects.filter(jobcard__panchayat=eachPanchayat,isSample=True)
  wid=0
  for eachWorker in myWorkers:
    s=''
    s1=''
    s+="%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (changeLanguage(logger,"english","telugu","workName"),
                                 changeLanguage(logger,"english","telugu","startDate"),
                                 changeLanguage(logger,"english","telugu","endDate"),
                                 changeLanguage(logger,"english","telugu","daysWorked"),
                                 changeLanguage(logger,"english","telugu","wages"),
                                 changeLanguage(logger,"english","telugu","workedyn"),
                                 changeLanguage(logger,"english","telugu","noOfDays"),
                                 changeLanguage(logger,"english","telugu","amount"),
                                 "code")
    s1+="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (changeLanguage(logger,"english","telugu","workName"),
                                 changeLanguage(logger,"english","telugu","startDate"),
                                 changeLanguage(logger,"english","telugu","endDate"),
                                 changeLanguage(logger,"english","telugu","daysWorked"),
                                 changeLanguage(logger,"english","telugu","wages"),
                                 changeLanguage(logger,"english","telugu","payorderNo"),
                                 changeLanguage(logger,"english","telugu","workedyn"),
                                 changeLanguage(logger,"english","telugu","noOfDays"),
                                 changeLanguage(logger,"english","telugu","amount"),
                                 "code")

    wid=wid+1
    tjobcard=eachWorker.jobcard.tjobcard
    myTransactions=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).values("workName").annotate(tcount=Sum('daysWorked'),wcount=Sum('payorderAmount'))
    for eachTransaction in myTransactions:
      workNameRaw=eachTransaction['workName']
      workName=eachTransaction['workName'].replace(",","")
      totalWorkDays=str(eachTransaction['tcount'])
      totalWages=str(int((eachTransaction['wcount'])))
      logger.info("Work name is %s transaction count is %s " % (workName,totalWorkDays))
      wds=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate,workName=workNameRaw).order_by("dateTo")
      i=0
      for wd in wds:
        i=i+1
        name=wd.name
        daysWorked=wd.daysWorked
        wages=int(wd.payorderAmount)
        dateTo=wd.dateTo
        payorderNo=wd.payorderNo
        dateFrom=wd.dateTo-datetime.timedelta(days=wd.daysWorked-1)
        dateFromString=datetime.datetime.strftime(dateFrom,'%d-%m-%Y')
        dateToString=datetime.datetime.strftime(dateTo,'%d-%m-%Y')
        if i == 1:
          dateStartString=dateFromString
        logger.info("Transaction ID %s , dateTo %s dateFrom %s Days WOrked %s" % (str(wd.id),str(wd.dateTo),str(dateFrom),str(daysWorked)))
        s1+="%s,%s,%s,%s,%s,%s,,,,\n" %(workName,dateFromString,dateToString,str(daysWorked),str(wages),payorderNo)
      s+="%s,%s,%s,%s,%s,,,,\n" %(workName,dateStartString,dateToString,str(totalWorkDays),str(totalWages))
    #logger.info(s1)
    outhtml+=getCenterAlignedHeading('Panchayat: %s Jobcard: %s' % (eachPanchayat.name,tjobcard))
    outhtml+=getCenterAlignedHeading('%s Name: %s' % (str(wid),eachWorker.name))
    outhtml+="<h3>code:%s</h3>" % changeLanguage(logger,"english","telugu","code")
    outhtml+="<h3>AggregateTable</h3>"
    outhtml+=csv2Table(logger,s,"workerAggregate")
    outhtml+="<h3>DetailTable</h3>"
    outhtml+=csv2Table(logger,s1,"workerDetail")
    outhtml+='<div class="pagebreak"> </div>'
  title=eachPanchayat.name
  outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
  try:
    outhtml=outhtml.encode("UTF-8")
  except:
    outhtml=outhtml

  filename="/tmp/surveyHTML/%s.html" % (eachPanchayat.slug)
  filename="/tmp/a.html"
  with open(filename,"wb") as f1:
    f1.write(outhtml)
  filename="%s_surveyTransaction.html" % (eachPanchayat.slug)
  saveGenericReport(logger,eachPanchayat,"apSurveyTransaction",outhtml,filename=filename)

  s=''
  s1=''
  s+='"name","workName","startDate","endDate","daysWorked","wages","payorderNo","worked y/n","noOfDays","amount","code"\n'
  s1+='"name","workName","startDate","endDate","daysWorked","wages","payorderNo","worked y/n","noOfDays","amount","code"\n'
  tjobcard=eachWorker.jobcard.tjobcard
  logger.info(eachWorker.name)
  myTransactions=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).values("workName").annotate(tcount=Sum('daysWorked'),wcount=Sum('payorderAmount'))
  for eachTransaction in myTransactions:
    workName=eachTransaction['workName']
    totalWorkDays=str(eachTransaction['tcount'])
    totalWages=str(int((eachTransaction['wcount'])))
    logger.info("Work name is %s transaction count is %s " % (workName,totalWorkDays))
    wds=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate,workName=workName).order_by("dateTo")
    i=0
    for wd in wds:
      i=i+1
      name=wd.name
      daysWorked=wd.daysWorked
      wages=int(wd.payorderAmount)
      dateTo=wd.dateTo
      payorderNo=wd.payorderNo
      dateFrom=wd.dateTo-datetime.timedelta(days=wd.daysWorked-1)
      dateFromString=datetime.datetime.strftime(dateFrom,'%d-%m-%Y')
      dateToString=datetime.datetime.strftime(dateTo,'%d-%m-%Y')
      if i == 1:
        dateStartString=dateFromString
      logger.info("Transaction ID %s , dateTo %s dateFrom %s Days WOrked %s" % (str(wd.id),str(wd.dateTo),str(dateFrom),str(daysWorked)))
#      a.extend([name,workName,dateFromString,dateToString,str(daysWorked),str(wages),payorderNo])
      s1+="%s,%s,%s,%s,%s,%s,%s\n" %(name,workName,dateFromString,dateToString,str(daysWorked),str(wages),payorderNo)
    s+="%s,%s,%s,%s,%s,%s,%s\n" %(name,workName,dateStartString,dateToString,str(totalWorkDays),str(totalWages),payorderNo)
  out="~%s\n%s\n%s\n" % (tjobcard,s,s1)
  tjobcardName=slugify(tjobcard+"_"+name)
  panchayatName=eachWorker.jobcard.panchayat.slug
  filename="/tmp/survey/%s/%s.csv" % (panchayatName,tjobcardName)  
  if not os.path.exists(os.path.dirname(filename)):
    os.makedirs(os.path.dirname(filename))
  with open(filename,"w") as fb:
    fb.write(out)

def createAPUWorkPaymentAP(logger,eachPanchayat,finyear=None,eachBlock=None):
  myTag="apuAPWorkPayment"
  finyear=str(finyear)
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  #w = csv.writer(f, newline='',delimiter=',')
  reportType="workPaymentAP"
#  logger.info("Createing extended Rejected Payment ReportsPayment for panchayat: %s panchayatCode: %s ID: %s" % (eachPanchayat.name,eachPanchayat.code,str(eachPanchayat.id)))
  a=[]
#  workRecords=WorkDetail.objects.filter(id=16082209)
  if eachBlock is not None:
    a.extend(["panchayat","tjobcard","heafOfFamily","caste","applicantNo","applicantName","workCode","workName","musterNo","dateTo","daysWorked","accountNo","payorderNo","payorderDate","epayorderno","epayorderDate","payingAgencyDate","creditedDate","disbursedDate","paymentMode","payOrdeAmount","disbursedAmount","dateDiff"])
    w.writerow(a)
    workRecords=APWorkPayment.objects.filter(jobcard__panchayat__block=eachBlock,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).order_by("jobcard__tjobcard","name","epayorderDate")
  else:
    a.extend(["panchayat","tjobcard","heafOfFamily","caste","applicantNo","applicantName","workCode","workName","musterNo","dateTo","daysWorked","accountNo","payorderNo","payorderDate","epayorderno","epayorderDate","payingAgencyDate","creditedDate","disbursedDate","paymentMode","payOrdeAmount","disbursedAmount","dateDiff"])
    w.writerow(a)
    workRecords=APWorkPayment.objects.filter(jobcard__panchayat=eachPanchayat,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).order_by("jobcard__tjobcard","name","dateTo")
  logger.info("Total Work Records: %s " %str(len(workRecords)))

  myobjs=APWorkPayment.objects.filter(jobcard__panchayat=eachPanchayat,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).values("jobcard","name").annotate(tcount=Count('pk'),dcount=Sum('daysWorked'))
  for obj in myobjs:
    logger.info(obj)
    jobcardID=obj['jobcard']
    eachJobcard=Jobcard.objects.filter(id=jobcardID).first()
    name=obj['name']
    totalTransaction=str(obj['tcount'])
    daysWorked=int(obj['dcount'])
    if daysWorked > 10:
      workRecords=APWorkPayment.objects.filter(jobcard=eachJobcard,name=name,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).order_by("jobcard__tjobcard","name","dateTo")
      for wd in workRecords:
        if wd.jobcard is not None:
          panchayatName=wd.jobcard.panchayat.name
        tjobcard1="~%s" % (wd.jobcard.tjobcard)
        dateDiff='0'
        if (wd.creditedDate is not None) and (wd.dateTo is not None):
          dateDiff=str((wd.creditedDate-wd.dateTo).days)
        a=[]
        a.extend([panchayatName,tjobcard1,wd.jobcard.headOfHousehold,wd.jobcard.caste,str(wd.applicantNo),wd.name,wd.workCode,wd.workName,wd.musterNo,str(wd.dateTo),str(wd.daysWorked),wd.accountNo,wd.payorderNo,str(wd.payorderDate),wd.epayorderNo,str(wd.epayorderDate),str(wd.payingAgencyDate),str(wd.creditedDate),str(wd.disbursedDate),wd.modeOfPayment,str(wd.payorderAmount),str(wd.disbursedAmount),dateDiff])
        w.writerow(a)
  f.seek(0)
#  with open("/tmp/a.csv","wb") as f1:
#    shutil.copyfileobj(f, f1)
  outcsv=f.getvalue()
  saveGenericReport(logger,eachPanchayat,myTag,outcsv)
# workers=Worker.objects.filter(jobcard__panchayat=eachPanchayat).order_by("jobcard__jcNo","applicantNo")
# for eachWorker in workers:
#   if eachWorker.jobcard.tjobcard is not None:
#     jobcard="~%s" %(eachWorker.jobcard.tjobcard)
#   else:
#     jobcard=eachWorker.jobcard
#   applicantNo=eachWorker.applicantNo
#   name=eachWorker.name
#   caste=eachWorker.jobcard.caste
#   headOfFamily=eachWorker.jobcard.headOfHousehold
#   if eachWorker.jobcard.village is not None:
#     village=eachWorker.jobcard.village.name
#   else:
#     village=''
#
#   a=[]
#   a.extend([eachPanchayat.name,village,jobcard,applicantNo,name,caste])
#   w.writerow(a)
# 
# f.seek(0)
# outcsv=f.getvalue()
# with open("/tmp/a.csv","wb") as w:
#   w.write(outcsv)

def createJobcardReport(logger,eachPanchayat,finyear,eachBlock=None):
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  reportType="jobcardcsv"
  a=[]
  a.extend(["panchayat","village","jobcard","names","caste","daysWorked19",'payOrderAmount19','disbursedAmount19','pendingAmount19','daysWorked18','payOrderAmount18','disbursedAmount18','pendingAmount18'])
  w.writerow(a)
  if eachBlock is not None:
    jobcards=Jobcard.objects.filter(panchayat__block=eachBlock)
  else:
    jobcards=Jobcard.objects.filter(panchayat=eachPanchayat)
  logger.info("Total Jobcards %s" % str(len(jobcards)))
  for eachJobcard in jobcards:
    if eachJobcard.tjobcard is not None:
      jobcard="~"+eachJobcard.tjobcard
    else:
      jobcard=eachJobcard.jobcard
    workerString=''
    if eachJobcard.village is not None:
      village=eachJobcard.village.name
    else:
      village=''
    caste=eachJobcard.caste
    if eachJobcard.panchayat.block.district.state.code == apStateCode:
      myDaysWorked=APWorkPayment.objects.filter(jobcard=eachJobcard).values("finyear").annotate(dsum=Sum('daysWorked'),psum=Sum('payorderAmount'),csum=Sum('disbursedAmount'))
    else:
      myDaysWorked=WorkPayment.objects.filter(jobcard=eachJobcard).values("finyear").annotate(dsum=Sum('daysWorked'),psum=Sum('totalWage'),csum=Sum('disbursedAmount'))
    daysWorked19=0
    payOrderAmount19=0
    creditedAmount19=0
    pendingAmount19=0
    daysWorked18=0
    payOrderAmount18=0
    creditedAmount18=0
    pendingAmount18=0
    for obj in myDaysWorked:
      if obj['finyear'] == '19':
        daysWorked19=obj['dsum']
        payOrderAmount19=obj['psum']
        creditedAmount19=obj['csum']
        pendingAmount19=payOrderAmount19-creditedAmount19
      if obj['finyear'] == '18':
        daysWorked18=obj['dsum']
        payOrderAmount18=obj['psum']
        creditedAmount18=obj['csum']
        pendingAmount18=payOrderAmount18-creditedAmount18
#myWorkDetails=WorkDetail.objects.filter(worker__jobcard__panchayat__block__id=2639,musterStatus='Rejected').values("worker__jobcard__panchayat__block__id","muster__finyear").annotate(dcount=Count('pk'),tcount=Sum('totalWage'))
    workers=Worker.objects.filter(jobcard=eachJobcard)
    for eachWorker in workers:
      workerString+=eachWorker.name
      workerString+="|"
    a=[]
    a.extend([eachPanchayat.name,village,jobcard,workerString,caste,daysWorked19,payOrderAmount19,creditedAmount19,pendingAmount19,daysWorked18,payOrderAmount18,creditedAmount18,pendingAmount18])
    w.writerow(a)
  f.seek(0)
  outcsv=f.getvalue()
  if eachBlock is not None:
    csvfilename=eachBlock.slug+"_"+finyear+"_jobcards.csv"
    saveBlockReport(logger,eachBlock,finyear,reportType,csvfilename,outcsv)
  else:
    csvfilename=eachPanchayat.slug+"_"+finyear+"_jobcards.csv"
    savePanchayatReport(logger,eachPanchayat,finyear,reportType,csvfilename,outcsv)

def getDiffFTOMuster(logger,eachBlock):
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  a=[]
  a.extend(["panchayat","tjobcard","heafOfFamily","caste","applicantNo","applicantName","workCode","workName","musterNo","dateTo","daysWorked","accountNo","payorderNo","payorderDate","epayorderno","epayorderDate","payingAgencyDate","creditedDate","disbursedDate","paymentMode","payOrdeAmount","disbursedAmount","dateDiff"])
  w.writerow(a)
  logger.info("Generating stats for Block %s " % (eachBlock.name))
#  Booking.objects.annotate(days=DiffDays(CastDate(F('end'))-CastDate(F('start'))) + 1)[0].days
  myobjs=APWorkPayment.objects.filter(jobcard__panchayat__block=eachBlock,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).extra(select={'offset': 'epayorderDate - dateTo'}).order_by('-offset')[:50]
  for wd in myobjs:
    logger.info(wd.id)
    if (wd.dateTo is not None) and (wd.epayorderDate is not None):
      diffDays=(wd.epayorderDate-wd.dateTo).days
    else:
      diffDays=None
    if wd.jobcard is not None:
      panchayatName=wd.jobcard.panchayat.name
    tjobcard1="~%s" % (wd.jobcard.tjobcard)
    dateDiff='0'
    if (wd.creditedDate is not None) and (wd.dateTo is not None):
      dateDiff=str((wd.creditedDate-wd.dateTo).days)
    a=[]
    a.extend([panchayatName,tjobcard1,wd.jobcard.headOfHousehold,wd.jobcard.caste,str(wd.applicantNo),wd.name,wd.workCode,wd.workName,wd.musterNo,str(wd.dateTo),str(wd.daysWorked),wd.accountNo,wd.payorderNo,str(wd.payorderDate),wd.epayorderNo,str(wd.epayorderDate),str(wd.payingAgencyDate),str(wd.creditedDate),str(wd.disbursedDate),wd.modeOfPayment,str(wd.payorderAmount),str(wd.disbursedAmount),diffDays])
    w.writerow(a)
  f.seek(0)
#  with open("/tmp/a.csv","wb") as f1:
#    shutil.copyfileobj(f, f1)
  outcsv=f.getvalue()
  with  open("/tmp/max.csv","wb") as f1:
    f1.write(outcsv)


def justlikethat(logger,eachPanchayat):
  myTag="surveyTransactionReport"
  s=''
  s1=''
  myWorkers=Worker.objects.filter(jobcard__panchayat=eachPanchayat,isSample=True)[:1]
  wid=0
  for eachWorker in myWorkers:
    wid=wid+1
    tjobcard=eachWorker.jobcard.tjobcard
    myTransactions=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).values("workName").annotate(tcount=Sum('daysWorked'),wcount=Sum('payorderAmount'))
    for eachTransaction in myTransactions:
      workName=eachTransaction['workName'].replace(",","")
      totalWorkDays=str(eachTransaction['tcount'])
      totalWages=str(int((eachTransaction['wcount'])))
      logger.info("Work name is %s transaction count is %s " % (workName,totalWorkDays))
 
def createTransactionReportHTML(logger,eachPanchayat):
  myTag="surveyTransactionReport"
  outhtml=''
  myWorkers=Worker.objects.filter(jobcard__panchayat=eachPanchayat,isSample=True)
  wid=0
  for eachWorker in myWorkers:
    s=''
    s1=''
    s+="%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (changeLanguage(logger,"english","telugu","workName"),
                                 changeLanguage(logger,"english","telugu","startDate"),
                                 changeLanguage(logger,"english","telugu","endDate"),
                                 changeLanguage(logger,"english","telugu","daysWorked"),
                                 changeLanguage(logger,"english","telugu","wages"),
                                 changeLanguage(logger,"english","telugu","workedyn"),
                                 changeLanguage(logger,"english","telugu","noOfDays"),
                                 changeLanguage(logger,"english","telugu","amount"),
                                 "code")
    s1+="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (changeLanguage(logger,"english","telugu","workName"),
                                 changeLanguage(logger,"english","telugu","startDate"),
                                 changeLanguage(logger,"english","telugu","endDate"),
                                 changeLanguage(logger,"english","telugu","daysWorked"),
                                 changeLanguage(logger,"english","telugu","wages"),
                                 changeLanguage(logger,"english","telugu","payorderNo"),
                                 changeLanguage(logger,"english","telugu","workedyn"),
                                 changeLanguage(logger,"english","telugu","noOfDays"),
                                 changeLanguage(logger,"english","telugu","amount"),
                                 "code")

    wid=wid+1
    tjobcard=eachWorker.jobcard.tjobcard
    myTransactions=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).values("workName").annotate(tcount=Sum('daysWorked'),wcount=Sum('payorderAmount'))
    for eachTransaction in myTransactions:
      workNameRaw=eachTransaction['workName']
      workName=eachTransaction['workName'].replace(",","")
      totalWorkDays=str(eachTransaction['tcount'])
      totalWages=str(int((eachTransaction['wcount'])))
      logger.info("Work name is %s transaction count is %s " % (workName,totalWorkDays))
      wds=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate,workName=workNameRaw).order_by("dateTo")
      i=0
      for wd in wds:
        i=i+1
        name=wd.name
        daysWorked=wd.daysWorked
        wages=int(wd.payorderAmount)
        dateTo=wd.dateTo
        payorderNo=wd.payorderNo
        dateFrom=wd.dateTo-datetime.timedelta(days=wd.daysWorked-1)
        dateFromString=datetime.datetime.strftime(dateFrom,'%d-%m-%Y')
        dateToString=datetime.datetime.strftime(dateTo,'%d-%m-%Y')
        if i == 1:
          dateStartString=dateFromString
        logger.info("Transaction ID %s , dateTo %s dateFrom %s Days WOrked %s" % (str(wd.id),str(wd.dateTo),str(dateFrom),str(daysWorked)))
        s1+="%s,%s,%s,%s,%s,%s,,,,\n" %(workName,dateFromString,dateToString,str(daysWorked),str(wages),payorderNo)
      s+="%s,%s,%s,%s,%s,,,,\n" %(workName,dateStartString,dateToString,str(totalWorkDays),str(totalWages))
    #logger.info(s1)
    outhtml+=getCenterAlignedHeading('Panchayat: %s Jobcard: %s' % (eachPanchayat.name,tjobcard))
    outhtml+=getCenterAlignedHeading('%s Name: %s' % (str(wid),eachWorker.name))
    outhtml+="<h3>code:%s</h3>" % changeLanguage(logger,"english","telugu","code")
    outhtml+="<h3>AggregateTable</h3>"
    outhtml+=csv2Table(logger,s,"workerAggregate")
    outhtml+="<h3>DetailTable</h3>"
    outhtml+=csv2Table(logger,s1,"workerDetail")
    outhtml+='<div class="pagebreak"> </div>'
  title=eachPanchayat.name
  outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
  try:
    outhtml=outhtml.encode("UTF-8")
  except:
    outhtml=outhtml

  filename="/tmp/surveyHTML/%s.html" % (eachPanchayat.slug)
  filename="/tmp/a.html"
  with open(filename,"wb") as f1:
    f1.write(outhtml)
  filename="%s_surveyTransaction.html" % (eachPanchayat.slug)
  saveGenericReport(logger,eachPanchayat,"apSurveyTransaction",outhtml,filename=filename)

def createRajendranReportHTML(logger,eachPanchayat):
  myTag="surveyJKTransactionReport"
  outhtml=''
  myWorkers=Worker.objects.filter(jobcard__panchayat=eachPanchayat,isSample=True)
  wid=0
  for eachWorker in myWorkers:
    s=''
    s1=''
    s+="%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (changeLanguage(logger,"english","hindi","workName"),
                                 changeLanguage(logger,"english","hindi","startDate"),
                                 changeLanguage(logger,"english","hindi","endDate"),
                                 changeLanguage(logger,"english","hindi","daysWorked"),
                                 changeLanguage(logger,"english","hindi","wages"),
                                 changeLanguage(logger,"english","hindi","workedyn"),
                                 changeLanguage(logger,"english","hindi","noOfDays"),
                                 changeLanguage(logger,"english","hindi","amount"),
                                 "code")
    s1+="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (changeLanguage(logger,"english","hindi","workName"),
                                 changeLanguage(logger,"english","hindi","startDate"),
                                 changeLanguage(logger,"english","hindi","endDate"),
                                 changeLanguage(logger,"english","hindi","daysWorked"),
                                 changeLanguage(logger,"english","hindi","wages"),
                                 changeLanguage(logger,"english","hindi","payorderNo"),
                                 changeLanguage(logger,"english","hindi","workedyn"),
                                 changeLanguage(logger,"english","hindi","noOfDays"),
                                 changeLanguage(logger,"english","hindi","amount"),
                                 "code")
    logger.info('s[%s]' % s)
    logger.info('s1[%s]' % s1)
    exit(0)
    wid=wid+1
    myTransactions=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate).values("workName").annotate(tcount=Sum('daysWorked'),wcount=Sum('payorderAmount'))
    for eachTransaction in myTransactions:
      workNameRaw=eachTransaction['workName']
      workName=eachTransaction['workName'].replace(",","")
      totalWorkDays=str(eachTransaction['tcount'])
      totalWages=str(int((eachTransaction['wcount'])))
      logger.info("Work name is %s transaction count is %s " % (workName,totalWorkDays))
      wds=APWorkPayment.objects.filter(worker=eachWorker,dateTo__gte=transactionStartDate,dateTo__lte=transactionEndDate,workName=workNameRaw).order_by("dateTo")
      i=0
      for wd in wds:
        i=i+1
        name=wd.name
        daysWorked=wd.daysWorked
        wages=int(wd.payorderAmount)
        dateTo=wd.dateTo
        payorderNo=wd.payorderNo
        dateFrom=wd.dateTo-datetime.timedelta(days=wd.daysWorked-1)
        dateFromString=datetime.datetime.strftime(dateFrom,'%d-%m-%Y')
        dateToString=datetime.datetime.strftime(dateTo,'%d-%m-%Y')
        if i == 1:
          dateStartString=dateFromString
        logger.info("Transaction ID %s , dateTo %s dateFrom %s Days WOrked %s" % (str(wd.id),str(wd.dateTo),str(dateFrom),str(daysWorked)))
        s1+="%s,%s,%s,%s,%s,%s,,,,\n" %(workName,dateFromString,dateToString,str(daysWorked),str(wages),payorderNo)
      s+="%s,%s,%s,%s,%s,,,,\n" %(workName,dateStartString,dateToString,str(totalWorkDays),str(totalWages))
    #logger.info(s1)
    outhtml+=getCenterAlignedHeading('Panchayat: %s Jobcard: %s' % (eachPanchayat.name,tjobcard))
    outhtml+=getCenterAlignedHeading('%s Name: %s' % (str(wid),eachWorker.name))
    outhtml+="<h3>code:%s</h3>" % changeLanguage(logger,"english","hindi","code")
    outhtml+="<h3>AggregateTable</h3>"
    outhtml+=csv2Table(logger,s,"workerAggregate")
    outhtml+="<h3>DetailTable</h3>"
    outhtml+=csv2Table(logger,s1,"workerDetail")
    outhtml+='<div class="pagebreak"> </div>'
  title=eachPanchayat.name
  outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
  try:
    outhtml=outhtml.encode("UTF-8")
  except:
    outhtml=outhtml

  filename="/tmp/surveyHTML/%s.html" % (eachPanchayat.slug)
  filename="/tmp/a.html"
  with open(filename,"wb") as f1:
    f1.write(outhtml)
  filename="%s_surveyTransaction.html" % (eachPanchayat.slug)
  # saveGenericReport(logger,eachPanchayat,"apSurveyTransaction",outhtml,filename=filename)

def colorAPUgte15Days(logger,eachPanchayat):
    wds=WorkDetail.objects.filter(worker__jobcard__panchayat=eachPanchayat,muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate).values('worker', 'worker__jobcard', 'worker__name').annotate(dcount=Sum('daysWorked')).order_by("worker__jobcard__village__name","worker__jobcard__jcNo","worker__name")
    for wd in wds:
      logger.debug('wd[%s]' % wd)
      eachWorker=Worker.objects.filter(id=wd['worker']).first()
      applicantNo=eachWorker.applicantNo
      jobcard=str(eachWorker.jobcard)
      #daysWorked=str(wd['dcount'])

      eachJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
      daysWorked=int(wd['dcount'])
      if daysWorked >= 15:
        logger.debug('> 15 jobcard[%s] applicantNo[%s] workerID[%s] workerName[%s]' % (jobcard, applicantNo, wd['worker'], wd['worker__name']))
        myWorker=Worker.objects.filter(jobcard=eachJobcard,applicantNo=applicantNo).first()
        if myWorker is None:
          logger.debug("Jobcard ID is %s-%s name is %s " % (str(eachJobcard.id),eachJobcard.jobcard,str(applicantNo)))
        else:
          myWorker.is15Days=True
          myWorker.save()
      else:
        logger.debug('< 15 jobcard[%s] applicantNo[%s] workerID[%s] workerName[%s]' % (jobcard, applicantNo, wd['worker'], wd['worker__name']))
          
def createRajendranWorkDetailsReport(logger,eachPanchayat,dirname):
  logger.info('Creating WorkDetails Report')
  myWorkers=Worker.objects.filter(jobcard__panchayat=eachPanchayat,isExtraSample=True)
  dumpWorkDetails(logger, eachPanchayat, dirname, myWorkers, 'workdetails_main_list1')

  myWorkers=Worker.objects.filter(jobcard__panchayat=eachPanchayat,isExtraSample30=True)
  dumpWorkDetails(logger, eachPanchayat, dirname, myWorkers, 'workdetails_replacement_list2')

def dumpWorkDetails(logger, eachPanchayat, dirname, myWorkers, suffix):
  fwp = BytesIO()
  fwp.write(u'\ufeff'.encode('utf8'))
  wp = csv.writer(fwp, encoding='utf-8-sig',delimiter=',')
  wpdata=[]
  
  a = []
  identifier = str(eachPanchayat.slug) + '-' + suffix
  #a.extend([identifier,'','','','','','','','','',''])
  a.extend(['','','','','',identifier,'','','',''])  
  wp.writerow(a)

  a = []
  a.extend(["WorkerID","गांव","जॉब कार्ड","मज़दूर का नाम","पिता/ पति का नाम","काम का नाम (MIS के अनुसार )","मस्टर","मज़दूरी दर","पेमेंट की स्तिथि","मस्टर का आखरी दिन \n ftoSign \n जमा होने की दिनांक"," काम किए गए \n दिनों की संख्या \n (MIS के अनुसार )"])
  wp.writerow(a)

  rowCount = 0
  for eachWorker in myWorkers:
    logger.debug('eachWorker[%s]' % eachWorker)
    workRecords=WorkDetail.objects.filter(worker=eachWorker,worker__jobcard__panchayat=eachPanchayat, muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate).order_by('worker__jobcard__village','worker__jobcard','creditedDate') 
    for wd in workRecords:
      logger.debug('row[%s]' % wd)
      wprow=[]
      workName=wd.muster.workName
      workCode=wd.muster.workCode
      wagelistArray=wd.wagelist.all()
      if len(wagelistArray) > 0:
        wagelist=wagelistArray[len(wagelistArray) -1 ]
      else:
        wagelist=''
      '''
      workNameArray=workName.split(' ')
      workNameArray[0] += ' '
      for i in range(1, len(workNameArray)):
        if (i % 6) == 0:
          workNameArray[i] += '\n'
        else:
          workNameArray[i] += ' '
      work = ''.join(workNameArray)
      '''
      work = workName
      musterNo = str(wd.muster.musterNo)
      wage = str(wd.totalWage).split(".")[0]
      status = wd.musterStatus
      daysWorked = wd.daysWorked
      worker_id = wd.worker_id
      logger.debug('daysWorked[%s] by worker_id[%s]' % (daysWorked,worker_id))
      srNo=str(wd.id)
      applicantName=wd.worker.name
      fatherHusbandName=wd.worker.fatherHusbandName
      logger.debug('fatherHusbandName[%s]' % fatherHusbandName)
      if wd.muster.dateTo is not None:
        dateTo=str(wd.muster.dateTo.strftime("%d/%m/%Y"))
      else:
        dateTo="FTOnotgenerated"
      if wd.creditedDate is not None:
        creditedDate=str(wd.creditedDate.strftime("%d/%m/%y"))
        creditedDiff=(wd.creditedDate-wd.muster.dateTo).days
      else:
        creditedDate="NotCred"
        creditedDiff=1000
    
      paymentRecord=PaymentInfo.objects.filter(workDetail=wd.id).order_by("-transactionDate").first()
      ftoNo=''
      accountNo=''
      paymentDate=''
      ftoStatus=''
      rejectionReason=''
      if paymentRecord is not None:
        accountNo=paymentRecord.accountNo
        if paymentRecord.fto is not None:
          ftoNo=paymentRecord.fto.ftoNo
          ftoStatus=paymentRecord.status
          rejectionReason=paymentRecord.rejectionReason
          if paymentRecord.fto.secondSignatoryDate:
            paymentDate=str(paymentRecord.fto.secondSignatoryDate.strftime("%d/%m/%y"))
      dateString="%s / %s / %s" %(dateTo,paymentDate,creditedDate)
      ftoAccount="%s/%s" % (ftoNo,accountNo)
      
      if wd.musterStatus == 'Rejected':
        category = 'rejected'
      if ( (wd.musterStatus == 'Credited' ) and (creditedDiff <= 30)):
        category = 'creditedWithin30days' # cc30.writerow(a)
      if (( (wd.musterStatus == 'Credited' ) and (creditedDiff > 30) ) ):
        category = 'creditedAfter30days' #ccdp.writerow(a)
   
      today=datetime.datetime.now().today()
      pendingSince=(today.date()-wd.muster.dateTo).days
      if ( (wd.musterStatus == '') and (pendingSince <= 30)):
        continue
      if ( (wd.musterStatus == '') and (pendingSince > 30)):
        continue

      a = []
      a.extend([worker_id, wd.worker.jobcard.village, str(wd.worker.jobcard), applicantName, fatherHusbandName, work, musterNo, wage, status, dateString, daysWorked])
      wp.writerow(a)
      wpdata.append(a)

      if False:
        rowCount += 1
        if (rowCount % 50) == 0:
          a = []
          identifier = str(eachPanchayat.slug) + '-' + suffix
          a.extend(['','','','','',identifier,'','','','','',''])  
          wp.writerow(a)

          a = []
          a.extend(["WorkerID","गांव","जॉब कार्ड","मज़दूर का नाम","पिता/ पति का नाम","काम का नाम (MIS के अनुसार )","मस्टर","मज़दूरी दर","पेमेंट की स्तिथि","मस्टर का आखरी दिन \n ftoSign \n जमा होने की दिनांक"," काम किए गए \n दिनों की संख्या \n (MIS के अनुसार )","Category"])
          wp.writerow(a)
      
  fwp.seek(0)
  outcsv = fwp.getvalue()
  filename = "%s/%s_%s.csv" % (dirname, eachPanchayat.slug, suffix)
  try:
    outcsv=outcsv.encode("UTF-8")
  except:
    outcsv=outcsv
    with open(filename, 'wb') as outfile:
      logger.info('Writing to file[%s]' % filename)
      outfile.write(outcsv)

def genAggregate(logger, eachPanchayat, dirname, df, suffix):
  fwp = BytesIO()
  fwp.write(u'\ufeff'.encode('utf8'))
  wp = csv.writer(fwp, encoding='utf-8-sig',delimiter=',')
  wpdata=[]
  
  a = []
  identifier = str(eachPanchayat.name) + '-' + suffix
  a.extend(['','','','','',identifier,'','','','','','',''])
    
  # wp.writerow(a)
  
  a = []
  # a.extend([" "," ","कोड"," ","-"," ","1 = हाँ, पूरी राशि मिल गयी"," ","2 = राशि मिली  पर पूरी नहीं"," ","3 = राशि नहीं मिली"," ","4 = मजदूरी प्राप्त की लेकिन नकदी में"," ","999 = काम नहीं किया",""])
  #codeStr = 'कोड - 1=हाँ पूरी राशि मिल गयी  2=राशि मिली  पर पूरी नहीं  3=राशि नहीं मिली  4=मजदूरी प्राप्त की लेकिन नकदी में  999=काम नहीं किया'
  codeStr = 'कोड - 1=हाँ पूरी राशि मिल गयी  2=राशि मिली  पर पूरी नहीं  3=राशि नहीं मिली \n  4=मजदूरी प्राप्त की लेकिन नकदी में  999=काम नहीं किया'
  a.extend(['','','','','',codeStr,'','','','','','','',''])
  # wp.writerow(a)

  '''
  a = []
  if isWorkCode:
    a.extend(["WorkerID","गांव","जॉब कार्ड","मज़दूर का नाम","पिता/ पति का नाम","काम का नाम (MIS के अनुसार )","वर्क कोड","पलहे मस्टर की शुरुवात","आखरी मस्टर की दिनांक","कुल दिन", "कुल मज़दूरी दर","क्या उत्तरदाता ने इस में काम किया है ? (हाँ/ना)","उत्तरदाता के हिसाब से कितने दिन काम किया है?","उत्तरदाता के हिसाब से कितने पैसे मिले?","क्या पूरी राशि मिली? सर्वेयर उत्तरदाता के जवाब के अनुसार कोड को भरे."])
  else:
    a.extend(["WorkerID","गांव","जॉब कार्ड","मज़दूर का नाम","पिता/ पति का नाम","काम का नाम (MIS के अनुसार )","पलहे मस्टर की शुरुवात","आखरी मस्टर की दिनांक","कुल दिन", "कुल मज़दूरी दर","क्या उत्तरदाता ने इस में काम किया है ? (हाँ/ना)","उत्तरदाता के हिसाब से कितने दिन काम किया है?","उत्तरदाता के हिसाब से कितने पैसे मिले?","क्या पूरी राशि मिली? सर्वेयर उत्तरदाता के जवाब के अनुसार कोड को भरे."])
  '''
  a = []
  # a.extend(["WorkerID","गांव","जॉब कार्ड","मज़दूर का नाम","पिता/ पति का नाम","काम का नाम (MIS के अनुसार )","पलहे मस्टर की \n शुरुवात","आखरी मस्टर की \n दिनांक","कुल दिन", "कुल \n मज़दूरी \n दर","क्या उत्तरदाता ने \n इस में काम किया है \n ? (हाँ/ना)","उत्तरदाता के हिसाब  \n से कितने दिन काम \n किया है?","उत्तरदाता के हिसाब \n से कितने पैसे \n मिले?","क्या पूरी राशि मिली? \n सर्वेयर उत्तरदाता के \n जवाब के अनुसार \n कोड को भरे."])
  a.extend(["WorkerID","गांव","जॉब कार्ड","मज़दूर का नाम","पिता/ पति का नाम","काम का नाम (MIS के अनुसार )","पेमेंट की स्तिथि","पलहे मस्टर की \n शुरुवात","आखरी मस्टर की \n दिनांक","कुल दिन", "कुल \n मज़दूरी \n दर","क्या उत्तरदाता ने \n इस में काम किया है \n ? (हाँ/ना)","उत्तरदाता के हिसाब  \n से कितने दिन काम \n किया है?","उत्तरदाता के हिसाब \n से कितने पैसे \n मिले?","क्या पूरी राशि मिली? \n सर्वेयर उत्तरदाता के \n जवाब के अनुसार \n कोड को भरे."])
  wp.writerow(a)

  for index, row in df.iterrows():
    eachWorker = row[u'\ufeff'+'WorkerID'].strip(u'\ufeff')
    category =  row['Category']

    if category == 'rejected':
      logger.info('REJECTED[%s:%s]' % (eachWorker, category))
      workRecords=WorkDetail.objects.filter(Q(musterStatus='Rejected') | (~Q(musterStatus='Credited') & Q(status__startswith='rejected')),worker=eachWorker,worker__jobcard__panchayat=eachPanchayat,muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate).order_by('worker__jobcard__village','worker__jobcard__jobcard','worker__name','muster__workCode').values('worker',"worker__jobcard__village__name","worker__jobcard__jobcard","worker__name","worker__fatherHusbandName","muster__workName", "muster__workCode").annotate(totalWages=Sum('totalWage'),dcount=Sum('daysWorked'))
      status = 'Rejected'

    if (category == 'creditedWithin30days') or (category == 'creditedAfter30days'):
      logger.info('CREDITED[%s:%s]' % (eachWorker, category))
      workRecords=WorkDetail.objects.filter(Q(musterStatus='Credited'),worker=eachWorker,worker__jobcard__panchayat=eachPanchayat,muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate).order_by('worker__jobcard__village','worker__jobcard__jobcard','worker__name','muster__workCode').values('worker',"worker__jobcard__village__name","worker__jobcard__jobcard","worker__name","worker__fatherHusbandName","muster__workName", "muster__workCode").annotate(totalWages=Sum('totalWage'),dcount=Sum('daysWorked'))
      status = 'Credited'
      
    for wd in workRecords:
      logger.info('row[%s]' % wd)
      '''
      musterStatus = wd['musterStatus']
      status = wd['status']

      if (wd.musterStatus == 'Rejected') or ((wd.musterStatus != 'Credited') and 'rejected' in wd.status):
        category = 'rejected'
      elif (wd.musterStatus == 'Credited'):
        category = 'credited' # cc30.writerow(a)
      '''
      worker_id = wd['worker']
      village_name = wd['worker__jobcard__village__name']
      jobcard = wd['worker__jobcard__jobcard']
      applicantName=wd['worker__name']
      fatherHusbandName=wd['worker__fatherHusbandName']
      workName = wd['muster__workName']
      workCode=wd['muster__workCode']
      totalWages = wd['totalWages']
      dcount = wd['dcount']

      wds=WorkDetail.objects.filter(worker=eachWorker,worker__jobcard__panchayat=eachPanchayat, muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate,muster__workCode=workCode).order_by("muster__dateTo")

      logger.debug(wds)
      dateFromString = datetime.datetime.strftime(wds[0].muster.dateFrom,'%d-%m-%Y')
      dateToString = datetime.datetime.strftime(wds[len(wds)-1].muster.dateTo,'%d-%m-%Y')

      logger.debug('From[%s] To[%s]' % (dateFromString, dateToString))

      '''
      i=0
      for wd in wds:
        i=i+1
        daysWorked=wd.daysWorked
        dateTo=wd.muster.dateTo
        #dateFrom=wd.dateTo-datetime.timedelta(days=wd.daysWorked-1)
        dateFrom=wd.muster.dateFrom
        dateFromString=datetime.datetime.strftime(dateFrom,'%d-%m-%Y')
        dateToString=datetime.datetime.strftime(dateTo,'%d-%m-%Y')
        if i == 1:
          dateStartString=dateFromString

      logger.info('From[%s] To[%s]' % (dateStartString, dateToString))
      exit(0)

      wagelistArray=wd.wagelist.all()
      if len(wagelistArray) > 0:
        wagelist=wagelistArray[len(wagelistArray) -1 ]
      else:
        wagelist=''
      wage = str(wd.totalWage).split(".")[0]
      status = wd.musterStatus
      daysWorked = wd.daysWorked
      if wd.muster.dateTo is not None:
        dateTo=str(wd.muster.dateTo.strftime("%d/%m/%Y"))
      else:
        dateTo="FTOnotgenerated"
      if wd.creditedDate is not None:
        creditedDate=str(wd.creditedDate.strftime("%d/%m/%y"))
        creditedDiff=(wd.creditedDate-wd.muster.dateTo).days
      else:
        creditedDate="NotCred"
        creditedDiff=1000

      paymentRecord=PaymentInfo.objects.filter(workDetail=wd.id).order_by("-transactionDate").first()
      ftoNo=''
      accountNo=''
      paymentDate=''
      ftoStatus=''
      rejectionReason=''
      if paymentRecord is not None:
        accountNo=paymentRecord.accountNo
        if paymentRecord.fto is not None:
          ftoNo=paymentRecord.fto.ftoNo
          ftoStatus=paymentRecord.status
          rejectionReason=paymentRecord.rejectionReason
          if paymentRecord.fto.secondSignatoryDate:
            paymentDate=str(paymentRecord.fto.secondSignatoryDate.strftime("%d/%m/%y"))
      dateString="%s / %s / %s" %(dateTo,paymentDate,creditedDate)
      ftoAccount="%s/%s" % (ftoNo,accountNo)
      
      if wd.musterStatus == 'Rejected':
        category = 'rejected'
      if ( (wd.musterStatus == 'Credited' ) and (creditedDiff <= 30)):
        category = 'creditedWithin30days' # cc30.writerow(a)
      if (( (wd.musterStatus == 'Credited' ) and (creditedDiff > 30) ) ):
        category = 'creditedAfter30days' #ccdp.writerow(a)
   
      today=datetime.datetime.now().today()
      pendingSince=(today.date()-wd.muster.dateTo).days
      if ( (wd.musterStatus == '') and (pendingSince <= 30)):
        continue
      if ( (wd.musterStatus == '') and (pendingSince > 30)):
        continue
      '''
      a = []
      a.extend([worker_id, village_name, jobcard, applicantName, fatherHusbandName, workName, status, dateFromString, dateToString, dcount, totalWages,'','','',''])
      wp.writerow(a)
      wpdata.append(a)
      
  fwp.seek(0)
  outcsv = fwp.getvalue()
  filename = "%s/%s_%s.csv" % (dirname, eachPanchayat.name, suffix)
  try:
    outcsv=outcsv.encode("UTF-8")
  except:
    outcsv=outcsv
    with open(filename, 'wb') as outfile:
      logger.info('Writing to file[%s]' % filename)
      outfile.write(outcsv)

  '''
  files = listdir(dirname)
  for file in files:
    filename = '%s/%s' % (dirname, file)
    fields = ['\ufeff'+'WorkerID', 'Category']
    df = pd.read_csv(filename, usecols=fields)
    eachPanchayat = file[:file.find('_sample_')]
    logger.info(eachPanchayat)

    if 'main' in file:
      genAggregate(logger, eachPanchayat, dirname+'Aggregate', df, 'aggregate_main_list1')
    else:
      genAggregate(logger, eachPanchayat, dirname+'Aggregate', df, 'aggregate_replacement_list2')
      
    exit(0)
  '''
# import numpy as np
def genVillages(logger, eachPanchayat, dirname, df, suffix):
  fwp = BytesIO()
  fwp.write(u'\ufeff'.encode('utf8'))
  wp = csv.writer(fwp, encoding='utf-8-sig',delimiter=',')
  #report = pd.pivot_table(df, index=["गांव"], values=["Category"],
  #                         aggfunc=[np.sum], fill_value=0)
  #report.head()
  logger.info('columns[%s] column name[%s]' % (df.columns, df.columns[1]))
  villages = df[df.columns[1]].unique() # df["गांव"].unique()
  logger.info('Panchayat[%s] Villages[%s]' % (eachPanchayat.name,villages))
  a = []
  a.extend(villages)
  wp.writerow(a)

  fwp.seek(0)
  outcsv = fwp.getvalue()
  filename = "%s/%s_%s.csv" % (dirname, eachPanchayat.name, suffix)
  try:
    outcsv=outcsv.encode("UTF-8")
  except:
    outcsv=outcsv
    with open(filename, 'wb') as outfile:
      logger.info('Writing to file[%s]' % filename)
      outfile.write(outcsv)
  
def uniqVillagesInSamplePanchayats(logger,eachPanchayat,dirname):
  logger.info('Creating Uniq Villages Report')
  logger.info(eachPanchayat)

  '''
  if '2721003067' not in eachPanchayat.slug:
    return
  '''

  filename = '%s/%s_sample_main_list1.csv' % (dirname, eachPanchayat.name)
  fields = ['\ufeff'+'WorkerID', 'Category']
  aggregateDir = dirname+'Villages'
  df1 = pd.read_csv(filename)  # , usecols=fields)
  logger.info('Working on file[%s]' % filename)
  genVillages(logger, eachPanchayat, aggregateDir, df1, 'villages_main_list1')

  filename = '%s/%s_sample_replacement_list2.csv' % (dirname, eachPanchayat.name)
  df2 = pd.read_csv(filename)  # , usecols=fields)
  logger.info('Working on file[%s]' % filename)
  genVillages(logger, eachPanchayat, aggregateDir, df2, 'villages_replacement_list2')
  genVillages(logger, eachPanchayat, aggregateDir, pd.concat([df1, df2]), 'villages_merged_list')

  
def createRajendranAggregateReport(logger,eachPanchayat,dirname):
  logger.info('Creating Aggregate Report')
  logger.info(eachPanchayat)

  filename = '%s/%s_sample_main_list1.csv' % (dirname, eachPanchayat.name)
  fields = ['\ufeff'+'WorkerID', 'Category']
  aggregateDir = dirname+'Aggregate'
  df = pd.read_csv(filename, usecols=fields)
  logger.info('Working on file[%s]' % filename)
  genAggregate(logger, eachPanchayat, aggregateDir, df, 'aggregate_main_list1')

  filename = '%s/%s_sample_replacement_list2.csv' % (dirname, eachPanchayat.name)
  df = pd.read_csv(filename, usecols=fields)
  logger.info('Working on file[%s]' % filename)
  genAggregate(logger, eachPanchayat, aggregateDir, df, 'aggregate_replacement_list2')

  '''
  exit(0)
  myWorkers=Worker.objects.filter(jobcard__panchayat=eachPanchayat,isSample=True)
  dumpAggregate(logger, eachPanchayat, dirname, myWorkers, 'aggregate_main_list1')

  myWorkers=Worker.objects.filter(jobcard__panchayat=eachPanchayat,isSample30=True)
  dumpAggregate(logger, eachPanchayat, dirname, myWorkers, 'aggregate_replacement_list2')
  '''
  
def dumpAggregate(logger, eachPanchayat, dirname, myWorkers, suffix):
  fwp = BytesIO()
  fwp.write(u'\ufeff'.encode('utf8'))
  wp = csv.writer(fwp, encoding='utf-8-sig',delimiter=',')
  wpdata=[]
  
  a = []
  identifier = str(eachPanchayat.name) + '-' + suffix
  a.extend(['','','','','',identifier,'','','','','','',''])
    
  # wp.writerow(a)
  
  a = []
  # a.extend([" "," ","कोड"," ","-"," ","1 = हाँ, पूरी राशि मिल गयी"," ","2 = राशि मिली  पर पूरी नहीं"," ","3 = राशि नहीं मिली"," ","4 = मजदूरी प्राप्त की लेकिन नकदी में"," ","999 = काम नहीं किया",""])
  #codeStr = 'कोड - 1=हाँ पूरी राशि मिल गयी  2=राशि मिली  पर पूरी नहीं  3=राशि नहीं मिली  4=मजदूरी प्राप्त की लेकिन नकदी में  999=काम नहीं किया'
  codeStr = 'कोड - 1=हाँ पूरी राशि मिल गयी  2=राशि मिली  पर पूरी नहीं  3=राशि नहीं मिली \n  4=मजदूरी प्राप्त की लेकिन नकदी में  999=काम नहीं किया'
  a.extend(['','','','','',codeStr,'','','','','','','',''])
  # wp.writerow(a)

  '''
  a = []
  if isWorkCode:
    a.extend(["WorkerID","गांव","जॉब कार्ड","मज़दूर का नाम","पिता/ पति का नाम","काम का नाम (MIS के अनुसार )","वर्क कोड","पलहे मस्टर की शुरुवात","आखरी मस्टर की दिनांक","कुल दिन", "कुल मज़दूरी दर","क्या उत्तरदाता ने इस में काम किया है ? (हाँ/ना)","उत्तरदाता के हिसाब से कितने दिन काम किया है?","उत्तरदाता के हिसाब से कितने पैसे मिले?","क्या पूरी राशि मिली? सर्वेयर उत्तरदाता के जवाब के अनुसार कोड को भरे."])
  else:
    a.extend(["WorkerID","गांव","जॉब कार्ड","मज़दूर का नाम","पिता/ पति का नाम","काम का नाम (MIS के अनुसार )","पलहे मस्टर की शुरुवात","आखरी मस्टर की दिनांक","कुल दिन", "कुल मज़दूरी दर","क्या उत्तरदाता ने इस में काम किया है ? (हाँ/ना)","उत्तरदाता के हिसाब से कितने दिन काम किया है?","उत्तरदाता के हिसाब से कितने पैसे मिले?","क्या पूरी राशि मिली? सर्वेयर उत्तरदाता के जवाब के अनुसार कोड को भरे."])
  '''
  a = []
  a.extend(["WorkerID","गांव","जॉब कार्ड","मज़दूर का नाम","पिता/ पति का नाम","काम का नाम (MIS के अनुसार )","पलहे मस्टर की \n शुरुवात","आखरी मस्टर की \n दिनांक","कुल दिन", "कुल \n मज़दूरी \n दर","क्या उत्तरदाता ने \n इस में काम किया है \n ? (हाँ/ना)","उत्तरदाता के हिसाब  \n से कितने दिन काम \n किया है?","उत्तरदाता के हिसाब \n से कितने पैसे \n मिले?","क्या पूरी राशि मिली? \n सर्वेयर उत्तरदाता के \n जवाब के अनुसार \n कोड को भरे."])
  wp.writerow(a)
  for eachWorker in myWorkers:
    if isSample and isExtraSample:
      dirname = 'aggregate_main_list1'
    logger.debug('eachWorker[%s]' % eachWorker)
    #workRecords=WorkDetail.objects.filter(Q(musterStatus='Rejected') | (~Q(musterStatus='Credited') & Q(status__startswith='rejected')),worker=eachWorker,worker__jobcard__panchayat=eachPanchayat,muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate).order_by('worker__jobcard__village','worker__jobcard__jobcard','worker__name','muster__workCode').values('worker',"worker__jobcard__village__name","worker__jobcard__jobcard","worker__name","worker__fatherHusbandName","muster__workName", "muster__workCode").annotate(totalWages=Sum('totalWage'),dcount=Sum('daysWorked'))
    workRecords=WorkDetail.objects.filter(worker=eachWorker,worker__jobcard__panchayat=eachPanchayat,muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate).order_by('worker__jobcard__village','worker__jobcard__jobcard','worker__name','muster__workCode').values('worker',"worker__jobcard__village__name","worker__jobcard__jobcard","worker__name","worker__fatherHusbandName","muster__workName", "muster__workCode","status","musterStatus").annotate(totalWages=Sum('totalWage'),dcount=Sum('daysWorked'))
    for wd in workRecords:
      logger.info('row[%s]' % wd)
      musterStatus = wd['musterStatus']
      status = wd['status']

      if (wd.musterStatus == 'Rejected') or ((wd.musterStatus != 'Credited') and 'rejected' in wd.status):
        category = 'rejected'
      elif (wd.musterStatus == 'Credited'):
        category = 'credited' # cc30.writerow(a)
      
      worker_id = wd['worker']
      village_name = wd['worker__jobcard__village__name']
      jobcard = wd['worker__jobcard__jobcard']
      applicantName=wd['worker__name']
      fatherHusbandName=wd['worker__fatherHusbandName']
      workName = wd['muster__workName']
      workCode=wd['muster__workCode']
      totalWages = wd['totalWages']
      dcount = wd['dcount']

      wds=WorkDetail.objects.filter(worker=eachWorker,worker__jobcard__panchayat=eachPanchayat, muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate,muster__workCode=workCode).order_by("muster__dateTo")

      logger.debug(wds)
      dateFromString = datetime.datetime.strftime(wds[0].muster.dateFrom,'%d-%m-%Y')
      dateToString = datetime.datetime.strftime(wds[len(wds)-1].muster.dateTo,'%d-%m-%Y')

      logger.debug('From[%s] To[%s]' % (dateFromString, dateToString))

      '''
      i=0
      for wd in wds:
        i=i+1
        daysWorked=wd.daysWorked
        dateTo=wd.muster.dateTo
        #dateFrom=wd.dateTo-datetime.timedelta(days=wd.daysWorked-1)
        dateFrom=wd.muster.dateFrom
        dateFromString=datetime.datetime.strftime(dateFrom,'%d-%m-%Y')
        dateToString=datetime.datetime.strftime(dateTo,'%d-%m-%Y')
        if i == 1:
          dateStartString=dateFromString

      logger.info('From[%s] To[%s]' % (dateStartString, dateToString))
      exit(0)

      wagelistArray=wd.wagelist.all()
      if len(wagelistArray) > 0:
        wagelist=wagelistArray[len(wagelistArray) -1 ]
      else:
        wagelist=''
      wage = str(wd.totalWage).split(".")[0]
      status = wd.musterStatus
      daysWorked = wd.daysWorked
      if wd.muster.dateTo is not None:
        dateTo=str(wd.muster.dateTo.strftime("%d/%m/%Y"))
      else:
        dateTo="FTOnotgenerated"
      if wd.creditedDate is not None:
        creditedDate=str(wd.creditedDate.strftime("%d/%m/%y"))
        creditedDiff=(wd.creditedDate-wd.muster.dateTo).days
      else:
        creditedDate="NotCred"
        creditedDiff=1000

      paymentRecord=PaymentInfo.objects.filter(workDetail=wd.id).order_by("-transactionDate").first()
      ftoNo=''
      accountNo=''
      paymentDate=''
      ftoStatus=''
      rejectionReason=''
      if paymentRecord is not None:
        accountNo=paymentRecord.accountNo
        if paymentRecord.fto is not None:
          ftoNo=paymentRecord.fto.ftoNo
          ftoStatus=paymentRecord.status
          rejectionReason=paymentRecord.rejectionReason
          if paymentRecord.fto.secondSignatoryDate:
            paymentDate=str(paymentRecord.fto.secondSignatoryDate.strftime("%d/%m/%y"))
      dateString="%s / %s / %s" %(dateTo,paymentDate,creditedDate)
      ftoAccount="%s/%s" % (ftoNo,accountNo)
      
      if wd.musterStatus == 'Rejected':
        category = 'rejected'
      if ( (wd.musterStatus == 'Credited' ) and (creditedDiff <= 30)):
        category = 'creditedWithin30days' # cc30.writerow(a)
      if (( (wd.musterStatus == 'Credited' ) and (creditedDiff > 30) ) ):
        category = 'creditedAfter30days' #ccdp.writerow(a)
   
      today=datetime.datetime.now().today()
      pendingSince=(today.date()-wd.muster.dateTo).days
      if ( (wd.musterStatus == '') and (pendingSince <= 30)):
        continue
      if ( (wd.musterStatus == '') and (pendingSince > 30)):
        continue
      '''
      a = []
      a.extend([worker_id, village_name, jobcard, applicantName, fatherHusbandName, workName, dateFromString, dateToString, dcount, totalWages,'','','',''])
      wp.writerow(a)
      wpdata.append(a)
      
  fwp.seek(0)
  outcsv = fwp.getvalue()
  filename = "%s/%s_%s.csv" % (dirname, eachPanchayat.name, suffix)
  try:
    outcsv=outcsv.encode("UTF-8")
  except:
    outcsv=outcsv
    with open(filename, 'wb') as outfile:
      logger.info('Writing to file[%s]' % filename)
      outfile.write(outcsv)

#def createAPURajendran(logger,eachPanchayat,transactionStartDate,transactionEndDate,finyear):
def createAPURajendran(logger,eachPanchayat, dirname):
  colorAPUgte15Days(logger, eachPanchayat)
  #createRajendranWorkDetailsReport(logger, eachPanchayat, dirname)
  #return
  #exit(0)

  collected = []
  rejCollected = []
  c30Collected = []
  after30Collected = []
  
  fwp = BytesIO()
  fwp.write(u'\ufeff'.encode('utf8'))
  wp = csv.writer(fwp, encoding='utf-8-sig',delimiter=',')

  fcsv_buffer = BytesIO()
  fcsv_buffer.write(u'\ufeff'.encode('utf8'))
  csv_buffer = csv.writer(fcsv_buffer, encoding='utf-8-sig',delimiter=',')

  ofwp = BytesIO()
  fwp.write(u'\ufeff'.encode('utf8'))
  wp = csv.writer(fwp, encoding='utf-8-sig',delimiter=',')

  fcsv_replacement = BytesIO()
  fcsv_replacement.write(u'\ufeff'.encode('utf8'))
  csv_replacement = csv.writer(fcsv_replacement, encoding='utf-8-sig',delimiter=',')

  wpdata=[]
  suffix1 = 'sample_main_list1'
  suffix2 = 'sample_replacement_list2'
  a = []
  identifier = str(eachPanchayat) + '-' + 'source'
  #a.extend([identifier,'','','','',''])
  a.extend(['','','','','',identifier,''])  
  wp.writerow(a)
  a = []
  identifier = str(eachPanchayat) + '-' + suffix1
  #a.extend([identifier,'','','','',''])
  a.extend(['','','','','',identifier,''])  
  #csv_buffer.writerow(a)
  a = []
  identifier = str(eachPanchayat) + '-' + suffix2
  #a.extend([identifier,'','','','',''])
  a.extend(['','','','','',identifier,''])  
  #csv_replacement.writerow(a)
  
  a=[]
  a.extend(["WorkerID","गांव","जॉब कार्ड","मज़दूर का नाम","पिता/ पति का नाम","काम का नाम (MIS के अनुसार )","Category"])
  wp.writerow(a)
  csv_buffer.writerow(a)
  csv_replacement.writerow(a)

  outmain = []

  rejected_array = []
  #rejected_array.extend(tableCols)
  
  c30_array = []
  # c30_array[].extend(tableCols)
  after30_array = []
  # after30_array[].extend(tableCols)

  rejected_desired_len = 0
  wds = WorkDetail.objects.filter(Q(worker__is15Days=True,worker__jobcard__panchayat=eachPanchayat, muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate) & Q( Q(status__icontains="rejected") & ~Q(musterStatus__icontains="credited")  ) ).values('worker').annotate(dcount=Count('daysWorked'),icount=Count('pk'))
  for wd in wds:
    logger.info('WorkerID[%s]' % wd['worker'])
    #logger.info('WorkerID[%s]' % wd.worker_id)
    rejected_desired_len += 1
  logger.info('EXPECTED[%s]' % rejected_desired_len)
  # exit(0)
  # workRecords=WorkDetail.objects.filter(worker__is15Days=True,worker__jobcard__panchayat=eachPanchayat, muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate).order_by('worker__jobcard__village','worker__jobcard__jcNo','creditedDate')  # .group_by('worker_id')

  rejRecords=WorkDetail.objects.filter(Q(musterStatus='Rejected') | (~Q(musterStatus='Credited') & Q(status__startswith='rejected')),worker__is15Days=True,worker__jobcard__panchayat=eachPanchayat, muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate).order_by('worker__jobcard__village','worker__jobcard__jcNo','creditedDate')  # .group_by('worker_id')
  #rejRecords=WorkDetail.objects.filter(Q(worker__is15Days=True,worker__jobcard__panchayat=eachPanchayat, muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate) & Q( Q(status__icontains="rejected") & ~Q(status__icontains="credited"))).order_by('worker__jobcard__village','worker__jobcard__jcNo','creditedDate')  # .group_by('worker_id')
  #rejRecords=WorkDetail.objects.filter(Q(worker__is15Days=True,worker__jobcard__panchayat=eachPanchayat, muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate) & Q( Q(status__icontains="rejected") & ~Q(status__icontains="credited"))).values('worker').annotate(dcount=Count('daysWorked'),icount=Count('pk'))

  credRecords=WorkDetail.objects.filter(Q(musterStatus='Credited'),worker__is15Days=True,worker__jobcard__panchayat=eachPanchayat, muster__dateTo__gte=transactionStartDate,muster__dateTo__lte=transactionEndDate).order_by('worker__jobcard__village','worker__jobcard__jcNo','creditedDate')  # .group_by('worker_id')

  workRecords = chain(rejRecords, credRecords)
  for wd in workRecords:
    wprow=[]
    workName=wd.muster.workName
    workCode=wd.muster.workCode
    wagelistArray=wd.wagelist.all()
    if len(wagelistArray) > 0:
      wagelist=wagelistArray[len(wagelistArray) -1 ]
    else:
      wagelist=''
    work=workName
    musterNo = str(wd.muster.musterNo)
    wage=str(wd.totalWage).split(".")[0]
    status = wd.musterStatus
    daysWorked = wd.daysWorked
    worker_id = wd.worker_id
    logger.debug('daysWorked[%s] by worker_id[%s]' % (daysWorked,worker_id))
    srNo=str(wd.id)
    applicantName=wd.worker.name
    fatherHusbandName=wd.worker.fatherHusbandName
    logger.debug('fatherHusbandName[%s]' % fatherHusbandName)
    if wd.muster.dateTo is not None:
      dateTo=str(wd.muster.dateTo.strftime("%d/%m/%Y"))
    else:
      dateTo="FTOnotgenerated"
    if wd.creditedDate is not None:
      creditedDate=str(wd.creditedDate.strftime("%d/%m/%y"))
      creditedDiff=(wd.creditedDate-wd.muster.dateTo).days
    else:
      creditedDate="NotCred"
      creditedDiff=1000

    today=datetime.datetime.now().today()
    pendingSince=(today.date()-wd.muster.dateTo).days

    paymentRecord=PaymentInfo.objects.filter(workDetail=wd.id).order_by("-transactionDate").first()
    ftoNo=''
    accountNo=''
    paymentDate=''
    ftoStatus=''
    rejectionReason=''
    if paymentRecord is not None:
      accountNo=paymentRecord.accountNo
      if paymentRecord.fto is not None:
        ftoNo=paymentRecord.fto.ftoNo
        ftoStatus=paymentRecord.status
        rejectionReason=paymentRecord.rejectionReason
        if paymentRecord.fto.secondSignatoryDate:
          paymentDate=str(paymentRecord.fto.secondSignatoryDate.strftime("%d/%m/%y"))
    dateString="%s / %s / %s" %(dateTo,paymentDate,creditedDate)
    ftoAccount="%s/%s" % (ftoNo,accountNo)

    #logger.info('Jobcard[%s]' % str(wd.worker.jobcard))
    a=[]

    if False and 'rejected' in wd.status:
      logger.info('REJECTED otherwise')
      print(worker_id, wd.worker.jobcard.village, str(wd.worker.jobcard), applicantName, fatherHusbandName, work, musterNo, wage, status, dateString, daysWorked)
    
    if (wd.musterStatus == 'Rejected') or ((wd.musterStatus != 'Credited') and 'rejected' in wd.status):
      category = 'rejected'
      if worker_id not in collected:
        collected.append(worker_id)
        rejCollected.append(worker_id)
        a = []
        a.extend([worker_id, wd.worker.jobcard.village, str(wd.worker.jobcard), applicantName, fatherHusbandName, work, category])
        rejected_array.append(a)
    if ( (wd.musterStatus == 'Credited' ) and (creditedDiff <= 30)):
      category = 'creditedWithin30days' # cc30.writerow(a)
      logger.debug('c30Collected[%s]' % c30Collected)
      if worker_id not in collected:
        collected.append(worker_id)
        c30Collected.append(worker_id)
        a = []
        a.extend([worker_id, wd.worker.jobcard.village, str(wd.worker.jobcard), applicantName, fatherHusbandName, work, category])
        c30_array.append(a)
    if (( (wd.musterStatus == 'Credited' ) and (creditedDiff > 30) ) ):
      category = 'creditedAfter30days' #ccdp.writerow(a)
      if worker_id not in collected:
        collected.append(worker_id)
        after30Collected.append(worker_id)
        a = []
        a.extend([worker_id, wd.worker.jobcard.village, str(wd.worker.jobcard), applicantName, fatherHusbandName, work, category])
        after30_array.append(a)
   
    if ( (wd.musterStatus == '') and (pendingSince <= 30)):
      category = 'pendingForLessThan30days' # pp30.writerow(a)
      a = []
      a.extend([worker_id, wd.worker.jobcard.village, str(wd.worker.jobcard), applicantName, fatherHusbandName, work, category])
      wp.writerow(a)
      wpdata.append(a)
      continue
    if ( (wd.musterStatus == '') and (pendingSince > 30)):
      category = 'pendingForMoreThan30days' # ppdp.writerow(a)
      a = []
      a.extend([worker_id, wd.worker.jobcard.village, str(wd.worker.jobcard), applicantName, fatherHusbandName, work, category])
      wp.writerow(a)
      wpdata.append(a)
      continue

    '''
    #### Old PaymentDate ####  
    if wd.muster.paymentDate is not None:
      paymentDate=str(wd.muster.paymentDate.strftime("%d/%m/%y"))
    else:
      logger.debug('Problem')
      paymentDate=""
    dateString="%s / %s / %s" %(dateTo,paymentDate,creditedDate)
    '''
    a = []
    a.extend([worker_id, wd.worker.jobcard.village, str(wd.worker.jobcard), applicantName, fatherHusbandName, work, category])
    wp.writerow(a)
    wpdata.append(a)

  if True:
    fwp.seek(0)      
    outcsv = fwp.getvalue()
    filename = "%s/%s_%s.csv" % (dirname, eachPanchayat.name, 'source')
    try:
      outcsv=outcsv.encode("UTF-8")
    except:
      outcsv=outcsv
    with open(filename, 'wb') as outfile:
        logger.info('Writing to file[%s]' % filename)
        outfile.write(outcsv)
  
  sample_size = 28
  c30_size = sample_size
  after30_size = sample_size
  size = 16 # int(sample_size/2)
  c30_adjusted = size
  after30_adjusted = size

  logger.info('Sampling Begins')
  rejLen = len(rejected_array)
  c30Len = len(c30_array)
  after30Len = len(after30_array)
  logger.info('Length of Rejected [%s] c30[%s] after30[%s]' % (rejLen, c30Len, after30Len))
  if (rejLen+ c30Len+ after30Len) < sample_size*3:
    logger.critical('Not happening [%s]' % (rejLen+ c30Len+ after30Len))
    exit(0)
  
  if rejLen < sample_size:
    logger.info('Sample too less for Rejected[%s]' % rejLen)
    sampleRejLen = rejLen
    remaining = sample_size - rejLen
    c30_size += int(remaining/2)
    after30_size += int((remaining+1)/2)
    logger.info('c30zie[%s] after30size[%s]' % (c30_size, after30_size))
  else:
    sampleRejLen = sample_size

  remaining = size - sampleRejLen
  if remaining > 0:
    c30_adjusted = size + int(remaining/2)
    after30_adjusted = size + int((remaining+1)/2)
    logger.info('c30_adjusted[%s], after30_adjusted[%s]' % (c30_adjusted, after30_adjusted))
  

  logger.info('c30 source[%s], req[%s]' % (c30Len, c30_size))
  if c30Len < c30_size: # sample_size:
    logger.critical('AKBC')
    sampleC30Len = c30Len
    remaining = c30_size - c30Len
    after30_size += remaining
    after30_adjusted += int(remaining/2)
  else:
    sampleC30Len = c30_size

  logger.info('after30 source[%s], req[%s]' % (after30Len, after30_size))
  if after30Len < after30_size: # sample_size:
    logger.critical('AKBC')
    sampleAfter30Len = after30Len
    remaining = after30_size - after30Len
  else:
    remaining = 0 
    sampleAfter30Len = after30_size

  if remaining != 0:
    logger.info('Before remaing[%s] sampleC30Len[%s] c30_adjusted[%s]' % (remaining, sampleC30Len, c30_adjusted))
    sampleC30Len += remaining
    #c30_adjusted += - remaining  # FIXME
    logger.info('After remaing[%s] sampleC30Len[%s] c30_adjusted[%s]' % (remaining, sampleC30Len, c30_adjusted))
    
  logger.info('Sampled :) [%s, %s, %s]' % (sampleRejLen, sampleC30Len, sampleAfter30Len))
  if (sampleRejLen + sampleC30Len + sampleAfter30Len) != sample_size*3:
    logger.critical('Screwed [%s, %s, %s]' % (sampleRejLen, sampleC30Len, sampleAfter30Len))
    exit(0)

  #Verify   sampleRejLen = len(rejSampleObjs)
  rejSampleObjs = random.sample(range(rejLen), sampleRejLen)
  for i in range(0, sampleRejLen):
    a = rejected_array[rejSampleObjs[i]]
    logger.debug('rejected_array[rejSampleObjs[%s]]=[%s]' % (i, a))
    logger.debug('WokerID[%s]' % a[0])
    eachWorker=Worker.objects.filter(id=a[0]).first()
    #    exit(0)
    if i < size:
      csv_buffer.writerow(a)
      logger.info('Rejected [%s]' % rejected_array[rejSampleObjs[i]])
      eachWorker.isSample=True
      eachWorker.isSample30=False
      eachWorker.isExtraSample=True
      eachWorker.isExtraSample30=False
      #libtechTag=LibtechTag.objects.filter(name="jkSurvey2018MainSample").first()
    else:
      csv_replacement.writerow(a)
      logger.info('Rejected Replacement [%s]' % rejected_array[rejSampleObjs[i]])      
      #libtechTag=LibtechTag.objects.filter(name="jk2018MainSample").first()
      eachWorker.isSample30=True
      eachWorker.isSample=False
      eachWorker.isExtraSample=False
      eachWorker.isExtraSample30=True
    #eachWorker.libtechTag.add(libtechTag)
    eachWorker.save()
    
  # Verify sampleC30Len = len(c30SampleObjs)
  c30SampleObjs = random.sample(range(c30Len), sampleC30Len)
  for i in range(0, sampleC30Len):
    a = c30_array[c30SampleObjs[i]]
    eachWorker=Worker.objects.filter(id=a[0]).first()
    if i < c30_adjusted:
      csv_buffer.writerow(a)
      eachWorker.isSample=True
      eachWorker.isSample30=False
    else:
      csv_replacement.writerow(a)
      eachWorker.isSample30=True
      eachWorker.isSample=False
    eachWorker.save()

  # Verify after30Len = len(after30SampleObjs)
  after30SampleObjs = random.sample(range(after30Len), sampleAfter30Len)
  for i in range(0, len(after30SampleObjs)):
    a = after30_array[after30SampleObjs[i]]
    eachWorker=Worker.objects.filter(id=a[0]).first()
    if i < after30_adjusted:
      csv_buffer.writerow(a)
      eachWorker.isSample=True
      eachWorker.isSample30=False
    else:
      csv_replacement.writerow(a)
      eachWorker.isSample30=True
      eachWorker.isSample=False
    eachWorker.save()

  '''
  #outmain.extend(tableCols)
  outmain.extend(rejSampleObjs[:size])
  #logger.info('outmain[%s]' % outmain)
  outmain.extend(c30SampleObjs[:size])
  outmain.extend(after30SampleObjs[:size])
  # outcsv = '\n'.join(row for row in outmain)
  outclean = '\n'.join(str(row).strip('[').strip(']').strip('<Village: ').replace('>', "'").replace(", '",",").replace("',",",").replace(', ','').replace("d'", "d").replace("s'", "s") for row in outmain)
  outcsv = 'vil,jc,name,Name of work,workCode,wage_status,dateTo_ftoSign_credited,sNo,daysWorked,Category\n' + outclean
  logger.info(outcsv)
  suffix = 'main'
  '''  
  # outcsv=fwp.getvalue()
  fcsv_buffer.seek(0)      
  outcsv = fcsv_buffer.getvalue()
  filename = "%s/%s_%s.csv" % (dirname, eachPanchayat.name, suffix1)
  try:
    outcsv=outcsv.encode("UTF-8")
  except:
    outcsv=outcsv
  with open(filename, 'wb') as outfile:
      logger.info('Writing to file[%s]' % filename)
      outfile.write(outcsv)

  fcsv_replacement.seek(0)      
  outcsv = fcsv_replacement.getvalue()
  filename = "%s/%s_%s.csv" % (dirname, eachPanchayat.name, suffix2)
  try:
    outcsv=outcsv.encode("UTF-8")
  except:
    outcsv=outcsv
  with open(filename, 'wb') as outfile:
      logger.info('Writing to file[%s]' % filename)
      outfile.write(outcsv)

  createRajendranAggregateReport(logger, eachPanchayat, dirname)
  uniqVillagesInSamplePanchayats(logger, eachPanchayat, dirname)
  return
