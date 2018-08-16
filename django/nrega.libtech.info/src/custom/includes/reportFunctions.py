import re
import shutil
import unicodecsv as csv
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
#import csv
from io import BytesIO
from bs4 import BeautifulSoup
from customSettings import repoDir,djangoDir,djangoSettings,telanganaThresholdDate,telanganaJobcardTimeThreshold,searchIP,wagelistTimeThreshold,musterTimeThreshold
import sys
import time
import os
from queue import Queue
from threading import Thread
import threading
import requests
import time
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from wrappers.logger import loggerFetch
import datetime
import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q,Sum,Count
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,PanchayatReport,VillageReport,Village,Jobcard,Worker,Wagelist,Applicant,PanchayatStat,PanchayatCrawlQueue,Stat,FTO,PaymentDetail,PaymentInfo,APWorkPayment
from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,getCurrentFinYear,saveBlockReport,savePanchayatReport,correctDateFormat,getjcNumber,getVilCode,getEncodedData,getCenterAlignedHeading,getTelanganaDate,table2csv

musterregex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
statsURL="http://mnregaweb4.nic.in/netnrega/all_lvl_details_new.aspx"


def createWorkDaysReport(logger,eachPanchayat):
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  a=[]
  a.extend(["panchayat","village","jobcard","name","totalTransaction","daysWorked"])
  w.writerow(a)
 #workers=Worker.objects.filter(jobcard__panchayat=eachPanchayat).order_by("jobcard__jcNo","applicantNo")
 #for eachWorker in workers:
 #  if eachWorker.jobcard.tjobcard is not None:
 #    jobcard="~%s" %(eachWorker.jobcard.tjobcard)
 #  else:
 #    jobcard=eachWorker.jobcard
 #  applicantNo=eachWorker.applicantNo
 #  name=eachWorker.name
 #  caste=eachWorker.jobcard.caste
 #  headOfFamily=eachWorker.jobcard.headOfHousehold
 #  if eachWorker.jobcard.village is not None:
 #    village=eachWorker.jobcard.village.name
 #  else:
 #    village=''
  wds=WorkDetail.objects.filter(worker__jobcard__panchayat=eachPanchayat).values('worker').annotate(tcount=Count('pk'),dcount=Sum('daysWorked'))
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
  outcsv=f.getvalue()
  filename="%s.csv" % (eachPanchayat.name)
  with open("/tmp/bhim/%s" % filename,"wb") as w:
    w.write(outcsv)

def createWorkPaymentReportAP(logger,eachPanchayat,finyear,eachBlock=None):
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
    a.extend(["panchayat","tjobcard","heafOfFamily","caste","applicantNo","applicantName","workCode","workName","musterNo","dateTo","daysWorked","accountNo","payorderNo","payorderDate","epayorderno","epayorderDate","payingAgencyDate","creditedDate","disbursedDate","paymentMode","payOrdeAmount","disbursedAmount"])
    w.writerow(a)
    workRecords=APWorkPayment.objects.filter(jobcard__panchayat__block=eachBlock,finyear=finyear).order_by("jobcard__tjobcard","epayorderDate")
  else:
    a.extend(["panchayat","tjobcard","heafOfFamily","caste","applicantNo","applicantName","workCode","workName","musterNo","dateTo","daysWorked","accountNo","payorderNo","payorderDate","epayorderno","epayorderDate","payingAgencyDate","creditedDate","disbursedDate","paymentMode","payOrdeAmount","disbursedAmount"])
    w.writerow(a)
    workRecords=APWorkPayment.objects.filter(jobcard__panchayat=eachPanchayat,finyear=finyear).order_by("jobcard__tjobcard","epayorderDate")
  logger.info("Total Work Records: %s " %str(len(workRecords)))
  for wd in workRecords:
    if wd.jobcard is not None:
      panchayatName=wd.jobcard.panchayat.name
    tjobcard1="~%s" % (wd.jobcard.tjobcard)
    a=[]
    a.extend([panchayatName,tjobcard1,wd.jobcard.headOfHousehold,wd.jobcard.caste,str(wd.applicantNo),wd.name,wd.workCode,wd.workName,wd.musterNo,str(wd.dateTo),str(wd.daysWorked),wd.accountNo,wd.payorderNo,str(wd.payorderDate),wd.epayorderNo,str(wd.epayorderDate),str(wd.payingAgencyDate),str(wd.creditedDate),str(wd.disbursedDate),wd.modeOfPayment,str(wd.payorderAmount),str(wd.disbursedAmount)])
    w.writerow(a)
  f.seek(0)
#  with open("/tmp/a.csv","wb") as f1:
#    shutil.copyfileobj(f, f1)
  outcsv=f.getvalue()
  if eachBlock is not None:
    csvfilename=eachBlock.slug+"_"+finyear+"_wpAP.csv"
    saveBlockReport(logger,eachBlock,finyear,reportType,csvfilename,outcsv)
  else:
    csvfilename=eachPanchayat.slug+"_"+str(finyear)+"_wpAP.csv"
    savePanchayatReport(logger,eachPanchayat,finyear,reportType,csvfilename,outcsv)

def createFieldRPReport(logger,eachPanchayat,finyear,eachBlock=None):
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  reportType="fieldRPReport"
  a=[]
  if eachBlock is not None:
    a.extend(["panchayat","village","jobcard","name","father/husname","musterNo","workName","dateFrom","dateTo","daysWorked","totalWage","currentStatus","rejectionReason","totalAttempts","primaryAccountHolder","ftoaccountNo","firstRejectionDate","lastRejectionDate","wagelist","ftoNo"])
    w.writerow(a)
    workRecords=WorkDetail.objects.filter( Q ( Q(worker__jobcard__panchayat__block=eachBlock,muster__finyear=finyear) & Q ( Q(musterStatus='Rejected') | Q (musterStatus="Invalid Account") )     ) ).order_by("worker__jobcard__panchayat__name","worker__jobcard__village__name","worker__jobcard__jcNo")
  else:
    a.extend(["village","jobcard","name","father/husname","musterNo","workName","dateFrom","dateTo","daysWorked","totalWage","currentStatus","rejectionReason","totalAttempts","primaryAccountHolder","ftoaccountNo","firstRejectionDate","lastRejectionDate","wagelist","ftoNo"])
    w.writerow(a)
    workRecords=WorkDetail.objects.filter( Q ( Q(worker__jobcard__panchayat=eachPanchayat,muster__finyear=finyear) & Q ( Q(musterStatus='Rejected') | Q (musterStatus="Invalid Account") )     ) ).order_by("worker__jobcard__village__name","worker__jobcard__jcNo")
  logger.info("Total Work Records: %s " %str(len(workRecords)))
  for wd in workRecords:
    workName=wd.muster.workName
    applicantName=wd.worker.name
    village=wd.worker.jobcard.village.name
    caste=wd.worker.jobcard.caste
    headOfHousehold=wd.worker.jobcard.headOfHousehold
    jcNo=wd.worker.jobcard.jcNo
    wagelistArray=wd.wagelist.all()
    if len(wagelistArray) > 0:
      wagelist=wagelistArray[len(wagelistArray) -1 ]
    else:
      wagelist=''
    fatherHusbandName=wd.worker.fatherHusbandName
    paymentRecords=PaymentInfo.objects.filter(workDetail=wd.id).order_by("transactionDate")
    paymentAttempts=len(paymentRecords)
    i=0
    firstRejectionDate=None
    lastRejectionDate=None
    currentStatus="Rejected"
    for pr in paymentRecords:
      i=i+1
      if i == 1:
        firstRejectionDate=pr.processDate
      if pr.processDate is not None:
        lastRejectionDate=pr.processDate
      if i == paymentAttempts:
        paymentStatus="current"
      else:
        paymentStatus="archive"
      wagelist=pr.wagelist.wagelistNo
      ftoNo=''
      firstSignatoryDate=''
      secondSignatoryDate=''
      ftofinyear=''
      paymentMode=''
      if pr.fto is  None:
        currentStatus="FTONotGenerated"
      else:
        if pr.processDate is None:
          currenStatus="FTONotProcessed"

      if pr.fto is not None:
        ftoNo=pr.fto.ftoNo
        firstSignatoryDate=pr.fto.firstSignatoryDate
        secondSignatoryDate=pr.fto.secondSignatoryDate
        ftofinyear=pr.fto.ftofinyear
        paymentMode=pr.fto.paymentMode
      a=[]
    currentStatus="Rejected"
    if eachBlock is not None:
      a.extend([wd.worker.jobcard.panchayat.name,village,wd.worker.jobcard.jobcard,applicantName,wd.worker.fatherHusbandName,wd.muster.musterNo,workName,str(wd.muster.dateFrom),str(wd.muster.dateTo),str(wd.daysWorked),str(wd.totalWage),currentStatus,pr.rejectionReason,str(paymentAttempts),pr.primaryAccountHolder,pr.accountNo,str(firstRejectionDate),str(lastRejectionDate),wagelist,ftoNo])
    else:
      a.extend([village,wd.worker.jobcard.jobcard,applicantName,wd.worker.fatherHusbandName,wd.muster.musterNo,workName,str(wd.muster.dateFrom),str(wd.muster.dateTo),str(wd.daysWorked),str(wd.totalWage),currentStatus,pr.rejectionReason,str(paymentAttempts),pr.primaryAccountHolder,pr.accountNo,str(firstRejectionDate),str(lastRejectionDate),wagelist,ftoNo])
    w.writerow(a)
  f.seek(0)
#  with open("/tmp/a.csv","wb") as f1:
#    shutil.copyfileobj(f, f1)
  outcsv=f.getvalue()
  if eachBlock is not None:
    csvfilename=eachBlock.slug+"_"+finyear+"_fieldRejPayment.csv"
    saveBlockReport(logger,eachBlock,finyear,reportType,csvfilename,outcsv)
  else:
    csvfilename=eachPanchayat.slug+"_"+finyear+"_fieldRejPayment.csv"
    savePanchayatReport(logger,eachPanchayat,finyear,reportType,csvfilename,outcsv)
 
def createExtendedRPReport(logger,eachPanchayat,finyear,eachBlock=None):
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  #w = csv.writer(f, newline='',delimiter=',')
  reportType="extendedRPReport"
#  logger.info("Createing extended Rejected Payment ReportsPayment for panchayat: %s panchayatCode: %s ID: %s" % (eachPanchayat.name,eachPanchayat.code,str(eachPanchayat.id)))
  a=[]
#  workRecords=WorkDetail.objects.filter(id=16082209)
  if eachBlock is not None:
    a.extend(["panchayat","village","jobcard","name","father/hus name","musterNo","workName","dateFrom","dateTo","daysWorked","totalWage","firstSignatory","secondSignatory","ftoStatus","rejectionReason","totalAttempts","attemptCount","current/archive","transactionDate","processDate","primaryAccountHolder","ftoaccountNo","wagelist","ftoNo"])
    w.writerow(a)
    workRecords=WorkDetail.objects.filter( Q ( Q(worker__jobcard__panchayat__block=eachBlock,muster__finyear=finyear) & Q ( Q(musterStatus='Rejected') | Q (musterStatus="Invalid Account") )     ) ).order_by("worker__jobcard__panchayat__name","worker__jobcard__village__name","worker__jobcard__jcNo")
  else:
    a.extend(["village","jobcard","name","father/hus name","musterNo","workName","dateFrom","dateTo","daysWorked","totalWage","firstSignatory","secondSignatory","ftoStatus","rejectionReason","totalAttempts","attemptCount","current/archive","transactionDate","processDate","primaryAccountHolder","ftoaccountNo","wagelist","ftoNo"])
    w.writerow(a)
    workRecords=WorkDetail.objects.filter( Q ( Q(worker__jobcard__panchayat=eachPanchayat,muster__finyear=finyear) & Q ( Q(musterStatus='Rejected') | Q (musterStatus="Invalid Account") )     ) ).order_by("worker__jobcard__village__name","worker__jobcard__jcNo")
  logger.info("Total Work Records: %s " %str(len(workRecords)))
  for wd in workRecords:
    workName=wd.muster.workName
    applicantName=wd.worker.name
    village=wd.worker.jobcard.village.name
    caste=wd.worker.jobcard.caste
    headOfHousehold=wd.worker.jobcard.headOfHousehold
    jcNo=wd.worker.jobcard.jcNo
    wagelistArray=wd.wagelist.all()
    if len(wagelistArray) > 0:
      wagelist=wagelistArray[len(wagelistArray) -1 ]
    else:
      wagelist=''
    fatherHusbandName=wd.worker.fatherHusbandName
    paymentRecords=PaymentInfo.objects.filter(workDetail=wd.id).order_by("transactionDate")
    paymentAttempts=len(paymentRecords)
    i=0
    for pr in paymentRecords:
      i=i+1
      if i == paymentAttempts:
        paymentStatus="current"
      else:
        paymentStatus="archive"
      wagelist=pr.wagelist.wagelistNo
      ftoNo=''
      firstSignatoryDate=''
      secondSignatoryDate=''
      ftofinyear=''
      paymentMode=''
      if pr.fto is not None:
        ftoNo=pr.fto.ftoNo
        firstSignatoryDate=pr.fto.firstSignatoryDate
        secondSignatoryDate=pr.fto.secondSignatoryDate
        ftofinyear=pr.fto.ftofinyear
        paymentMode=pr.fto.paymentMode
      a=[]
      if eachBlock is not None:
        a.extend([wd.worker.jobcard.panchayat.name,village,wd.worker.jobcard.jobcard,applicantName,wd.worker.fatherHusbandName,wd.muster.musterNo,workName,str(wd.muster.dateFrom),str(wd.muster.dateTo),str(wd.daysWorked),str(wd.totalWage),str(firstSignatoryDate),str(secondSignatoryDate),pr.status,pr.rejectionReason,str(paymentAttempts),str(i),paymentStatus,str(pr.transactionDate),str(pr.processDate),pr.primaryAccountHolder,pr.accountNo,wagelist,ftoNo])
      else:
      #  a.extend([village,wd.worker.jobcard.jobcard,applicantName,wd.worker.fatherHusbandName,wd.muster.musterNo,workName,str(wd.muster.dateFrom),str(wd.muster.dateTo),str(wd.daysWorked),str(wd.totalWage),str(firstSignatoryDate),str(secondSignatoryDate),pr.status,pr.rejectionReason,str(paymentAttempts),str(i),paymentStatus,str(pr.transactionDate),str(pr.processDate),pr.primaryAccountHolder,pr.accountNo,wagelist,ftoNo])
        a.extend([village,wd.worker.jobcard.jobcard,applicantName,wd.worker.fatherHusbandName,wd.muster.musterNo,workName,str(wd.muster.dateFrom),str(wd.muster.dateTo),str(wd.daysWorked),str(wd.totalWage),str(firstSignatoryDate),str(secondSignatoryDate),pr.status,pr.rejectionReason,str(paymentAttempts),str(i),paymentStatus,str(pr.transactionDate),str(pr.processDate),pr.primaryAccountHolder,pr.accountNo,wagelist,ftoNo,wd.id,pr.id,pr.referenceNo])
      w.writerow(a)
  f.seek(0)
#  with open("/tmp/a.csv","wb") as f1:
#    shutil.copyfileobj(f, f1)
  outcsv=f.getvalue()
  if eachBlock is not None:
    csvfilename=eachBlock.slug+"_"+finyear+"_extdRejPayment.csv"
    saveBlockReport(logger,eachBlock,finyear,reportType,csvfilename,outcsv)
  else:
    csvfilename=eachPanchayat.slug+"_"+finyear+"_extdRejPayment.csv"
    savePanchayatReport(logger,eachPanchayat,finyear,reportType,csvfilename,outcsv)
 
  
def createReportsAPU(logger,eachPanchayat,filepath,finyear,startDate,endDate):
  today=datetime.datetime.now().today()
  fwp = BytesIO()
  fwp.write(u'\ufeff'.encode('utf8'))
  wp = csv.writer(fwp, encoding='utf-8-sig',delimiter=',')

  frp = BytesIO()
  frp.write(u'\ufeff'.encode('utf8'))
  rp = csv.writer(frp, encoding='utf-8-sig',delimiter=',')

  fip = BytesIO()
  fip.write(u'\ufeff'.encode('utf8'))
  ip = csv.writer(fip, encoding='utf-8-sig',delimiter=',')

  fpp = BytesIO()
  fpp.write(u'\ufeff'.encode('utf8'))
  pp = csv.writer(fpp, encoding='utf-8-sig',delimiter=',')

  fjr = BytesIO()
  fjr.write(u'\ufeff'.encode('utf8'))
  jr = csv.writer(fjr, encoding='utf-8-sig',delimiter=',')

  fcc30= BytesIO()
  fcc30.write(u'\ufeff'.encode('utf8'))
  cc30 = csv.writer(fcc30, encoding='utf-8-sig',delimiter=',')

  fccdp= BytesIO()
  fccdp.write(u'\ufeff'.encode('utf8'))
  ccdp = csv.writer(fccdp, encoding='utf-8-sig',delimiter=',')


  fpp30= BytesIO()
  fpp30.write(u'\ufeff'.encode('utf8'))
  pp30 = csv.writer(fpp30, encoding='utf-8-sig',delimiter=',')

  fppdp= BytesIO()
  fppdp.write(u'\ufeff'.encode('utf8'))
  ppdp = csv.writer(fppdp, encoding='utf-8-sig',delimiter=',')

  wpdata=[]
  rejecteddata=[]
  invaliddata=[]
  pendingdata=[]
  jrdata=[]

  a=[]
  tableCols=["vil","hhd","name","Name of work","wage_status","dateTo_ftoSign_credited","sNo"]
  a.extend(["vil","hhd","name","Name of work","wage_status","dateTo_ftoSign_credited","fto_accountNo","rejectionReason"])
  rp.writerow(a)
  ip.writerow(a)
  a=[]
  a.extend(["vil","hhd","name","Name of work","wage_status","dateTo_ftoSign_credited","fto_accountNo","sNo"])
  wp.writerow(a)
  pp.writerow(a)
  cc30.writerow(a)
  ccdp.writerow(a)
  pp30.writerow(a)
  ppdp.writerow(a)
  ajr=[]

  workRecords=WorkDetail.objects.filter(worker__jobcard__panchayat=eachPanchayat,muster__dateFrom__gte=startDate,muster__dateFrom__lte=endDate).order_by('worker__jobcard__village__name','worker__jobcard__jcNo','creditedDate')

  for wd in workRecords:
    wprow=[]
    workName=wd.muster.workName
    workCode=wd.muster.workCode
    villageName=''
    if wd.worker.jobcard.village:
      villageName=wd.worker.jobcard.village.name
    wagelistArray=wd.wagelist.all()
    if len(wagelistArray) > 0:
      wagelist=wagelistArray[len(wagelistArray) -1 ]
    else:
      wagelist=''
    work=workName+"/"+str(wd.muster.musterNo)
    wageStatus=str(wd.totalWage).split(".")[0]+"/"+wd.musterStatus
    srNo=str(wd.id)
    applicantName=wd.worker.name
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
    a=[]
    a.extend([villageName,str(wd.worker.jobcard.jcNo),applicantName,work,wageStatus,dateString,ftoAccount,srNo])
    wp.writerow(a)
    wpdata.append(a)
    
    if wd.musterStatus == 'Rejected':
      a=[]
      a.extend([villageName,str(wd.worker.jobcard.jcNo),applicantName,work,wageStatus,dateString,ftoAccount,rejectionReason])
      rp.writerow(a)
      rejecteddata.append(a)
    if wd.musterStatus == 'Invalid Account':
      a=[]
      a.extend([villageName,str(wd.worker.jobcard.jcNo),applicantName,work,wageStatus,dateString,ftoAccount,rejectionReason])
      invaliddata.append(a)
      ip.writerow(a)
    if wd.musterStatus == '':
      pendingdata.append(a)
      pp.writerow(a)
    if ( (wd.musterStatus == 'Credited' ) and (creditedDiff <= 30)):
      cc30.writerow(a)
    if (( (wd.musterStatus == 'Credited' ) and (creditedDiff > 30) ) ):
      ccdp.writerow(a)
    if ( (wd.musterStatus == '') and (pendingSince <= 30)):
      pp30.writerow(a)
    if ( (wd.musterStatus == '') and (pendingSince > 30)):
      ppdp.writerow(a)
  fwp.seek(0)
  frp.seek(0)
  fip.seek(0)
  fpp.seek(0)
  fjr.seek(0)
  fcc30.seek(0)
  fccdp.seek(0)
  fpp30.seek(0)
  fppdp.seek(0)

  fileDir="%s/%s" % (filepath,eachPanchayat)
  if not os.path.exists(fileDir):
    os.makedirs(fileDir)
  with open("%s/workPayment.csv" % (fileDir),"wb") as f:
    f.write(getEncodedData(fwp.getvalue()))
  with open("%s/rejectedPayment.csv" % (fileDir),"wb") as f:
    f.write(getEncodedData(frp.getvalue()))
  with open("%s/invalidPayment.csv" % (fileDir),"wb") as f:
    f.write(getEncodedData(fip.getvalue()))
  with open("%s/pendingPayment.csv" % (fileDir),"wb") as f:
    f.write(getEncodedData(fpp.getvalue()))
  with open("%s/ccWithin30.csv" % (fileDir),"wb") as f:
    f.write(getEncodedData(fcc30.getvalue()))
  with open("%s/ccafter30.csv" % (fileDir),"wb") as f:
    f.write(getEncodedData(fccdp.getvalue()))
  with open("%s/pendingafter30.csv" % (fileDir),"wb") as f:
    f.write(getEncodedData(fppdp.getvalue()))
  with open("%s/pendingWithin30.csv" % (fileDir),"wb") as f:
    f.write(getEncodedData(fpp30.getvalue()))


