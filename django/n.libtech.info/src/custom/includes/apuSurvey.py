
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

