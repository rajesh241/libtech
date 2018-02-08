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
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from wrappers.logger import loggerFetch
import datetime
import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q,Sum
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,PanchayatReport,VillageReport,Village,Jobcard,Worker,Wagelist,Applicant,PanchayatStat,PanchayatCrawlQueue,Stat,FTO,PaymentDetail,PaymentInfo
from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,getCurrentFinYear,savePanchayatReport,correctDateFormat,getjcNumber,getVilCode,getEncodedData,getCenterAlignedHeading,getTelanganaDate,table2csv

musterregex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
statsURL="http://mnregaweb4.nic.in/netnrega/all_lvl_details_new.aspx"
def crawlPanchayatTelangana(logger,qid,stage=None):
  logger.info("Crawling Telangana Panchayat")
  endFinYear=getCurrentFinYear()
  stage7Done=False
  myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
  myQueueObject.crawlStartTime=timezone.now()
  myQueueObject.downloadAttemptCount=myQueueObject.downloadAttemptCount+1
  curPanchayatCode=myQueueObject.panchayat.code
  startFinYear=myQueueObject.startFinYear
  myQueueObject.save()

  eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
  startTime=timezone.now()
  error=None
  logger.info("Starting to crawl Code %s Panchayat %s Block %s District %s State %s" % (eachPanchayat.code,eachPanchayat.name,eachPanchayat.block.name,eachPanchayat.block.district.name,eachPanchayat.block.district.state.name))
  logger.info("Crawling Starting from Fin Year %s to Finyear %s " % (str(startFinYear),str(endFinYear)))

  if ((stage is None) or (stage==1)):
    eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
    logger.info("Step 1: Crawling PanchayatStats")
    myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
    myQueueObject.status=1
    myQueueObject.save()

  if ((stage is None) or (stage==2)):
    eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
    logger.info("Step 2: Crawling Jobcard Register")
    error=saveJobcardRegisterTelangana(logger,eachPanchayat)
    if error is None:
      logger.info("Jobcard Register Crawl Successful")
      logger.info("Step 2: Processing Jobcard Register")
      processJobcardRegisterTelangana(logger,eachPanchayat)
      myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
      myQueueObject.status=2
      myQueueObject.save()


  if ((stage is None) or (stage==3)):
    eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
    logger.info("Step 3: Crawl Download and Process each jobcard Page")
    downloadJobcardsTelangana(logger,eachPanchayat)
    myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
    myQueueObject.status=3
    myQueueObject.save()

  if ((stage is None) or (stage==4)):
    myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
    myQueueObject.status=4
    myQueueObject.save()

  if ((stage is None) or (stage==5)):
    myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
    myQueueObject.status=5
    myQueueObject.save()


  if ((stage is None) or (stage==6)):
    myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
    myQueueObject.status=6
    myQueueObject.save()

  if ((stage is None) or (stage==7)):
    eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
    logger.info("Step 5: Generate Reports")
    for finyear in range(int(startFinYear),int(endFinYear)+1):
      finyear=str(finyear)
      logger.info(finyear)
      createPaymentReportTelangana(logger,eachPanchayat,finyear)
    myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
    myQueueObject.status=7
    myQueueObject.save()

def crawlPanchayat(logger,qid,stage=None):
#  myQueueObject=PanchayatCrawlQueue.objects.filter(panchayat=eachPanchayat,isComplete=False).first()
  endFinYear=getCurrentFinYear()
  stage7Done=False
  myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
  myQueueObject.crawlStartDate=timezone.now()
  myQueueObject.crawlAttemptDate=timezone.now()
  myQueueObject.downloadAttemptCount=myQueueObject.downloadAttemptCount+1
  curPanchayatCode=myQueueObject.panchayat.code
  startFinYear=myQueueObject.startFinYear
  myQueueObject.save()

  eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
  startTime=timezone.now()
  error=None
  logger.info("Starting to crawl Code %s Panchayat %s Block %s District %s State %s" % (eachPanchayat.code,eachPanchayat.name,eachPanchayat.block.name,eachPanchayat.block.district.name,eachPanchayat.block.district.state.name))
  logger.info("Crawling Starting from Fin Year %s to Finyear %s " % (str(startFinYear),str(endFinYear)))

  if ((stage is None) or (stage==1)):
    eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
    logger.info("Step 1: Crawling PanchayatStats")
    error=downloadPanchayatStat(logger,eachPanchayat)
    if error is None:
      processPanchayatStat(logger,eachPanchayat)
      myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
      myQueueObject.status=1
      myQueueObject.save()

  if ((stage is None) or (stage==2)):
    eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
    logger.info("Step 2: Crawling Jobcard Register")
    error=saveJobcardRegister(logger,eachPanchayat)
    if error is None:
      logger.info("Jobcard Register Crawl Successful")
      logger.info("Step 2: Processing Jobcard Register")
      processJobcardRegister(logger,eachPanchayat)
      myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
      myQueueObject.status=2
      myQueueObject.save()
      
  if ((stage is None) or (stage==3)):
    eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
    logger.info("Step 3: Crawl Download and Process Musters")
    for finyear in range(int(startFinYear),int(endFinYear)+1):
      finyear=str(finyear)
      logger.info(finyear)
      crawlMusters(logger,eachPanchayat,finyear)
      downloadMusters(logger,eachPanchayat,finyear)
      processMusters(logger,eachPanchayat,finyear)
      downloadDelayedCompensationReport(logger,eachPanchayat,finyear)
    myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
    myQueueObject.status=3
    myQueueObject.save()

  if ((stage is None) or (stage==4)):
    eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
    logger.info("Step 3: Download and Process Wagelist")
    for finyear in range(int(startFinYear),int(endFinYear)+1):
      finyear=str(finyear)
      downloadWagelist(logger,eachPanchayat,finyear)
      processWagelist(logger,eachPanchayat,finyear)
    myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
    myQueueObject.status=4
    myQueueObject.save()

  if ((stage is None) or (stage==5)):
    eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
    logger.info("Step 3: Download and Process FTOs")
    for finyear in range(int(startFinYear),int(endFinYear)+1):
      finyear=str(finyear)
      #downloadFTO(logger,eachPanchayat,finyear)
    myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
    myQueueObject.status=5
    myQueueObject.save()

  if ((stage is None) or (stage==6)):
    eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
    accuracyIndexSum=0
    i=0
    logger.info("Step 4: Compute the Statistics")
    for finyear in range(int(startFinYear),int(endFinYear)+1):
      i=i+1
      finyear=str(finyear)
      logger.info(finyear)
      curAccuracyIndex=computePanchayatStat(logger,eachPanchayat,finyear)
      accuracyIndexSum+=curAccuracyIndex
      if str(finyear) == str(endFinYear):
        accuracyIndex = curAccuracyIndex

    accuracyIndexAverage=int(accuracyIndexSum/i)

    eachPanchayat.accuracyIndexAverage=accuracyIndexAverage
    eachPanchayat.accuracyIndex=accuracyIndex
    eachPanchayat.save()
    myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
    myQueueObject.status=6
    myQueueObject.save()

  if ((stage is None) or (stage==7)):
    eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
    logger.info("Step 5: Generate Reports")
    for finyear in range(int(startFinYear),int(endFinYear)+1):
      finyear=str(finyear)
      logger.info(finyear)
      createWorkPaymentReport(logger,eachPanchayat,finyear)
      createReportsJSK(logger,eachPanchayat,finyear)
    myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
    myQueueObject.status=7
    myQueueObject.save()
    stage7Done=True
       
#  endTime=datetime.datetime.now()
  eachPanchayat=Panchayat.objects.filter(code=curPanchayatCode).first()
  myQueueObject=PanchayatCrawlQueue.objects.filter(id=qid).first()
  endTime=timezone.now()
  totalMinutes=int( ((endTime-startTime).total_seconds())/60)
  
  if stage7Done == True: 
    eachPanchayat.lastCrawlDate=timezone.now()
    myQueueObject.isComplete=True
  lastCrawlDuration=eachPanchayat.lastCrawlDuration
  if lastCrawlDuration is None:
    lastCrawlDuration=0
  eachPanchayat.lastCrawlDuration=lastCrawlDuration+totalMinutes
  eachPanchayat.save()
  myQueueObject.save()

def validateWagelist(block,myhtml):
  error=None
  myTable=None
  jobcardPrefix=block.district.state.stateShortCode+"-"
  if (jobcardPrefix in myhtml):
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if jobcardPrefix in str(table):
        myTable=table
    if myTable is None:
      error="Wagelist Table Not Found"
  else:
    error="Jobcard Prefix not found"
  return error,myTable

def processWagelist(logger,eachPanchayat,finyear):
  eachBlock=eachPanchayat.block
  myWagelists=Wagelist.objects.filter(isDownloaded=1,isProcessed=0,block=eachBlock,finyear=finyear)
  for eachWagelist in myWagelists:
    logger.info("Wage list id: %s, wagelistno : %s " % (str(eachWagelist.id),eachWagelist.wagelistNo))
    myhtml=eachWagelist.wagelistFile.read()
    stateShortCode=eachWagelist.block.district.state.stateShortCode
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    isComplete=True
    mytable=htmlsoup.find('table',id="myTable")
    rows = mytable.findAll('tr')
    for row in rows:
      cols=row.findAll('td')
      if "WageList No" in str(row):
        logger.info("Skipping this row")
        for i,col in enumerate(cols):
          if col.text.lstrip().rstrip() == "FTO No.":
            ftoIndex=i
        logger.info(ftoIndex)
      else:
        ftoNo=cols[ftoIndex].text.lstrip().rstrip()
        logger.info(ftoNo)
        if stateShortCode not in ftoNo:
          isComplete=False
        else:
          logger.info("FTO Number seems to be correct")
          matchedFTO=FTO.objects.filter(ftoNo=ftoNo,block=eachWagelist.block,finyear=eachWagelist.finyear).first()
          if matchedFTO is not None:
            logger.info("FTO Found")
          else:
            FTO.objects.create(ftoNo=ftoNo,block=eachWagelist.block,finyear=eachWagelist.finyear)
            logger.info("Created FTO")
    eachWagelist.isProcessed=1
    logger.info("Value of is Complete is %s " % str(isComplete))
    eachWagelist.isComplete=isComplete
    eachWagelist.save()

def downloadFTO(logger,eachPanchayat,finyear):
  eachBlock=eachPanchayat.block
  myobjs=FTO.objects.filter( Q(isDownloaded=False,block=eachBlock) | Q(downloadAttemptDate__lt = musterTimeThreshold,isComplete=0,isProcessed=1,block=eachBlock) ).order_by("downloadAttemptDate")
  j=len(myobjs)
  if len(myobjs) > 0:
    n=getNumberProcesses(len(myobjs))
    queueSize=n+len(myobjs)+10
    q = Queue(maxsize=queueSize)
    logger.info("Queue Size %s Numbe of Threads %s " % (str(queueSize),str(n)))
    for obj in myobjs:
      q.put(obj.id)
      obj.downloadAttemptDate=timezone.now()
      obj.save()

    for i in range(n):
      logger.info("Starting worker Thread %s " % str(i))
      t = Thread(name = 'Thread-' + str(i), target=FTODownloadWorker, args=(logger,q ))
      t.daemon = True  
      t.start()


    q.join()       # block until all tasks are done
    for i in range(n):
      q.put(None)

def FTODownloadWorker(logger,q):
  while True:
    FTOID = q.get()  # if there is no url, this will wait
    if FTOID is None:
      break
    name = threading.currentThread().getName()

    eachFTO=FTO.objects.filter(id=FTOID).first()
    errorString=''
    logger.info("Current Queue: %s Thread : %s FTOID: %s FullblockCode: %s status: %s" % (str(q.qsize()),name,str(eachFTO.id),eachFTO.block.code,errorString))
 
#    logger.info("%s FTO ID: %s FTO No: %s " % (str(j),str(eachFTO.id),eachFTO.ftoNo)) 
    stateCode=eachFTO.block.district.state.code
    ftoNo=eachFTO.ftoNo
    splitFTO=ftoNo.split("_")
    ftoyear=splitFTO[1][4:6]
    ftomonth=splitFTO[1][2:4]
    if int(ftomonth) > 3:
      ftofinyear=str(int(ftoyear)+1)
    else:
      ftofinyear=ftoyear
    finyear=eachFTO.finyear
    logger.info("FTO Finyear is %s finyear is %s " % (ftofinyear,finyear))
    fullfinyear=getFullFinYear(ftofinyear)
    block=eachFTO.block
    blockName=block.name
    districtName=block.district.name
    stateName=block.district.state.name
    htmlresponse,htmlsource = getFTO(logger,fullfinyear,stateCode,ftoNo,districtName)
    logger.info("Response = %s " % htmlresponse)
    if htmlresponse['status'] == '200':
      logger.info("Status is 200")
      error,myTable,summaryTable=validateFTO(block,htmlsource)
      if error is None:
        logger.info("No error")
        outhtml=''
        outhtml+=stripTableAttributes(summaryTable,"summaryTable")
        outhtml+=stripTableAttributes(myTable,"myTable")
        #outcsv+=table2csv(dcTable)
        title="FTO state:%s District:%s block:%s FTO No: %s finyear:%s " % (stateName,districtName,blockName,ftoNo,fullfinyear)
        outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
        try:
          outhtml=outhtml.encode("UTF-8")
        except:
          outhtml=outhtml
        filename="%s.html" % (ftoNo)
        eachFTO.ftoFile.save(filename, ContentFile(outhtml))
        eachFTO.downloadAttemptDate=timezone.now()
        eachFTO.isDownloaded=True
        eachFTO.isProcessed=False
        eachFTO.ftofinyear=ftofinyear
        eachFTO.save()
      else:
        logger.info(error)
        eachFTO.downloadAttemptDate=timezone.now()
        eachFTO.ftofinyear=ftofinyear
        eachFTO.downloadError=error
        eachFTO.save()
    q.task_done()


def downloadWagelist(logger,eachPanchayat,finyear):
  wagelistRegex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  eachBlock=eachPanchayat.block
  myWagelists=Wagelist.objects.filter(Q(block=eachBlock,finyear=finyear,isComplete=False) & Q( Q(downloadAttemptDate__lt = wagelistTimeThreshold) | Q (downloadAttemptDate__isnull = True))   )
  n = len(myWagelists)
  for eachWagelist in myWagelists:
    wagelistNo=eachWagelist.wagelistNo
    fullfinyear=getFullFinYear(eachWagelist.finyear)
    fullDistrictCode=eachWagelist.block.district.code
    stateName=eachWagelist.block.district.state.name
    districtName=eachWagelist.block.district.name
    fullBlockCode=eachWagelist.block.code
    stateShortCode=eachWagelist.block.district.state.stateShortCode
    blockName=eachWagelist.block.name
    eachBlock=eachWagelist.block
    logger.info("%s - %s " % (str(n),wagelistNo))
    n=n-1
    url="http://%s/netnrega/srch_wg_dtl.aspx?state_code=&district_code=%s&state_name=%s&district_name=%s&block_code=%s&wg_no=%s&short_name=%s&fin_year=%s&mode=wg" % (searchIP,fullDistrictCode,stateName.upper(),districtName.upper(),fullBlockCode,wagelistNo,stateShortCode,fullfinyear)
    logger.info(url)
    try:
      r  = requests.get(url)
      error=0
    except requests.exceptions.RequestException as e:  # This is the correct syntax
      logger.info(e) 
      error=1
    if error==0:
      curtime = time.strftime('%Y-%m-%d %H:%M:%S')
      htmlsource=r.text
      htmlsource1=re.sub(wagelistRegex,"",htmlsource)
      error,myTable=validateWagelist(eachBlock,htmlsource1)
      if error is None:
        logger.info("Error is None, Saving Wagelist File")
        outhtml=''
        outcsv=''
        outhtml+=stripTableAttributes(myTable,"myTable")
        #outcsv+=table2csv(dcTable)
        title="WageList : state:%s District:%s block:%s Wagelist: %s finyear:%s " % (stateName,districtName,blockName,wagelistNo,fullfinyear)
        outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
        try:
          outhtml=outhtml.encode("UTF-8")
        except:
          outhtml=outhtml
        filename="%s.html" % (wagelistNo)
        eachWagelist.wagelistFile.save(filename, ContentFile(outhtml))
        eachWagelist.downloadAttemptDate=timezone.now()
        eachWagelist.isDownloaded=True
        eachWagelist.isProcessed=False
        eachWagelist.save()
      else:
        eachWagelist.downloadAttemptDate=timezone.now()
        eachWagelist.downloadError=error
        eachWagelist.save()
 
def createWorkPaymentReport(logger,eachPanchayat,finyear):
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  #w = csv.writer(f, newline='',delimiter=',')
  reportType="workPaymentDelayAnalysis"
  logger.info("Createing work Payment report for panchayat: %s panchayatCode: %s ID: %s" % (eachPanchayat.name,eachPanchayat.code,str(eachPanchayat.id)))
  a=[]
#  workRecords=WorkDetail.objects.filter(id=16082209)
  a.extend(["jobcard","name","musterNo","workCode","workName","dateFrom","dateTo","daysWorked","totalWage","accountNo","musterStatus","creditedDate","secondSignatoryDate","wagelistNo"])
  w.writerow(a)
  workRecords=WorkDetail.objects.filter(worker__jobcard__panchayat=eachPanchayat,muster__finyear=finyear)
  logger.info("Total Work Records: %s " %str(len(workRecords)))
  for wd in workRecords:
    workName=wd.muster.workName
    applicantName=wd.worker.name
    wagelistArray=wd.wagelist.all()
    if len(wagelistArray) > 0:
      wagelist=wagelistArray[len(wagelistArray) -1 ]
    else:
      wagelist=''
    fatherHusbandName=wd.worker.fatherHusbandName
    a=[]
    a.extend([wd.worker.jobcard.jobcard,applicantName,wd.muster.musterNo,wd.muster.workCode,workName,str(wd.muster.dateFrom),str(wd.muster.dateTo),str(wd.daysWorked),str(wd.totalWage),wd.zaccountNo,wd.musterStatus,str(wd.creditedDate),str(wd.muster.paymentDate),wagelist])
    w.writerow(a)
  f.seek(0)
#  with open("/tmp/a.csv","wb") as f1:
#    shutil.copyfileobj(f, f1)
  outcsv=f.getvalue()
  csvfilename=eachPanchayat.slug+"_"+finyear+"_wpda.csv"
  savePanchayatReport(logger,eachPanchayat,finyear,reportType,csvfilename,outcsv)

def createReportsJSK(logger,eachPanchayat,finyear):
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

  wpdata=[]
  rejecteddata=[]
  invaliddata=[]
  pendingdata=[]
  a=[]
  tableCols=["vil","hhd","name","Name of work","workCode","wage_status","dateTo_ftoSign_credited","sNo"]
  a.extend(["vil","hhd","name","Name of work","workCode","wage_status","dateTo_ftoSign_credited","sNo"])
  wp.writerow(a)
  rp.writerow(a)
  ip.writerow(a)
  pp.writerow(a)


  workRecords=WorkDetail.objects.filter(worker__jobcard__panchayat=eachPanchayat,muster__finyear=finyear).order_by('zvilCode','zjcNo','creditedDate')

  for wd in workRecords:
    wprow=[]
    workName=wd.muster.workName
    workCode=wd.muster.workCode
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
    else:
      creditedDate="NotCred"
    if wd.muster.paymentDate is not None:
      paymentDate=str(wd.muster.paymentDate.strftime("%d/%m/%y"))
    else:
      paymentDate=""
    dateString="%s / %s / %s" %(dateTo,paymentDate,creditedDate)
    a=[]
    a.extend([wd.zvilCode,str(wd.zjcNo),applicantName,work,workCode,wageStatus,dateString,srNo])
    wp.writerow(a)
    wpdata.append(a)
    
    if wd.musterStatus == 'Rejected':
      rp.writerow(a)
      rejecteddata.append(a)
    if wd.musterStatus == 'Invalid Account':
      invaliddata.append(a)
      ip.writerow(a)
    if wd.musterStatus == '':
      pendingdata.append(a)
      pp.writerow(a)

  fwp.seek(0)
  frp.seek(0)
  fip.seek(0)
  fpp.seek(0)

  savePanchayatReportJSKWrapper(logger,finyear,eachPanchayat,tableCols,"workPayment","wp",wpdata,fwp.getvalue() )
  savePanchayatReportJSKWrapper(logger,finyear,eachPanchayat,tableCols,"rejectedPayment","rp",rejecteddata,frp.getvalue() )
  savePanchayatReportJSKWrapper(logger,finyear,eachPanchayat,tableCols,"invalidPayment","ip",invaliddata,fip.getvalue() )
  savePanchayatReportJSKWrapper(logger,finyear,eachPanchayat,tableCols,"pendingPayment","pp",pendingdata,fpp.getvalue() )

def createReportsJSK1(logger,eachPanchayat,finyear):
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
  
  savePanchayatReportJSKWrapper(logger,finyear,eachPanchayat,tableCols,"workPayment","wp",wpdata,wpcsv)
  savePanchayatReportJSKWrapper(logger,finyear,eachPanchayat,tableCols,"rejectedPayment","rp",rejecteddata,rejectedcsv)
  savePanchayatReportJSKWrapper(logger,finyear,eachPanchayat,tableCols,"invalidPayment","ip",invaliddata,invalidcsv)
  savePanchayatReportJSKWrapper(logger,finyear,eachPanchayat,tableCols,"pendingPayment","pp",pendingdata,pendingcsv)

def savePanchayatReportJSKWrapper(logger,finyear,eachPanchayat,tableCols,reportType,reportsuffix,myData,csvData):  

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




def crawlMusters(logger,eachPanchayat,finyear):
  fullfinyear=getFullFinYear(finyear)
  logger.info("Processing : panchayat: %s " % (eachPanchayat.name))
  stateCode=eachPanchayat.block.district.state.code
  fullDistrictCode=eachPanchayat.block.district.code
  fullBlockCode=eachPanchayat.block.code
  fullPanchayatCode=eachPanchayat.code
  districtName=eachPanchayat.block.district.name
  blockName=eachPanchayat.block.name
  stateName=eachPanchayat.block.district.state.name
  crawlIP=eachPanchayat.block.district.state.crawlIP
  panchayatName=eachPanchayat.name
  musterType='10'
  url="http://"+crawlIP+"/netnrega/state_html/emuster_wage_rep1.aspx?type="+str(musterType)+"&lflag=eng&state_name="+stateName+"&district_name="+districtName+"&block_name="+blockName+"&panchayat_name="+panchayatName+"&panchayat_code="+fullPanchayatCode+"&fin_year="+fullfinyear
  logger.info(url)
  try:
    r  = requests.get(url)
    error=0
  #except requests.exceptions.RequestException as e:  # This is the correct syntax
  except:  # This is the correct syntax
    error=1
  if error==0:
    curtime = time.strftime('%Y-%m-%d %H:%M:%S')
    htmlsource=r.text
    htmlsource1=re.sub(musterregex,"",htmlsource)
    htmlsoup=BeautifulSoup(htmlsource1,"html.parser")
    try:
      table=htmlsoup.find('table',bordercolor="green")
      rows = table.findAll('tr')
      errorflag=0
    except:
      status=0
      errorflag=1
    if errorflag==0:
      for tr in rows:
        cols = tr.findAll('td')
        tdtext=''
        district= cols[1].string.strip()
        block= cols[2].string.strip()
        panchayat= cols[3].string.strip()
        worknameworkcode=cols[5].text
        if district!="District":
          emusterno="".join(cols[6].text.split())
          datefromdateto="".join(cols[7].text.split())
          datefromstring=datefromdateto[0:datefromdateto.index("-")]
          datetostring=datefromdateto[datefromdateto.index("-") +2:len(datefromdateto)]
          if datefromstring != '':
            datefrom = time.strptime(datefromstring, '%d/%m/%Y')
            datefrom = time.strftime('%Y-%m-%d', datefrom)
          else:
            datefrom=''
          if datetostring != '':
            dateto = time.strptime(datetostring, '%d/%m/%Y')
            dateto = time.strftime('%Y-%m-%d', dateto)
          else:
            dateto=''
          #worknameworkcodearray=re.match(r'(.*)\(330(.*)\)',worknameworkcode)
          worknameworkcodearray=re.match(r'(.*)\('+stateCode+r'(.*)\)',worknameworkcode)
          if worknameworkcodearray is not None:
            workName=worknameworkcodearray.groups()[0]
            workCode=stateCode+worknameworkcodearray.groups()[1]
            logger.info(emusterno+" "+datefromstring+"  "+datetostring+"  "+workCode)
            musterURL="http://%s/netnrega/citizen_html/musternew.aspx?state_name=%s&district_name=%s&block_name=%s&panchayat_name=%s&workcode=%s&panchayat_code=%s&msrno=%s&finyear=%s&dtfrm=%s&dtto=%s&wn=%s&id=1" % (eachPanchayat.block.district.state.crawlIP,stateName,districtName,blockName,panchayatName,workCode,fullPanchayatCode,emusterno,fullfinyear,datefromstring,datetostring,workName.replace(" ","+"))
            #logger.info(musterURL)
            myMuster=Muster.objects.filter(finyear=finyear,musterNo=emusterno,block__code=fullBlockCode).first()
            if myMuster is  None:
              #logger.info("Muster does not exists") 
              Muster.objects.create(block=eachPanchayat.block,finyear=finyear,musterNo=emusterno)
            myMuster=Muster.objects.filter(finyear=finyear,musterNo=emusterno,block__code=fullBlockCode).first()
            myMuster.dateFrom=datefrom
            myMuster.dateTo=dateto
            myMuster.workCode=workCode
            myMuster.workName=workName 
            myMuster.musterType='10'
            myMuster.musterURL=musterURL
            myMuster.isRequired=1
            myMuster.panchayat=eachPanchayat
            myMuster.save()

def computePanchayatStat(logger,eachPanchayat,finyear):
  logger.info(eachPanchayat.name+","+eachPanchayat.code+","+finyear)
  mustersTotal=len(Muster.objects.filter(panchayat=eachPanchayat,finyear=finyear))
  logger.info("Muster Total")
  mustersDownloaded=len(Muster.objects.filter(panchayat=eachPanchayat,finyear=finyear,isDownloaded=True))
  logger.info("Muster Downloaded")
  mustersProcessed=len(Muster.objects.filter(panchayat=eachPanchayat,finyear=finyear,isDownloaded=True,isProcessed=True))
  logger.info("Muster Processed")
  mustersComplete=len(Muster.objects.filter(panchayat=eachPanchayat,finyear=finyear,isDownloaded=True,isProcessed=True,isComplete=True))
  logger.info("Muster Complete")
  mustersAllApplicantsFound=len(Muster.objects.filter(panchayat=eachPanchayat,finyear=finyear,isDownloaded=True,isProcessed=True,allWorkerFound=True))
  jobcardsTotal=len(Jobcard.objects.filter(panchayat=eachPanchayat)) 
  logger.info("Jobcards total Complete")
  workersTotal=len(Worker.objects.filter(jobcard__panchayat=eachPanchayat,isDeleted=False))
  libtechWorkDaysPanchayatwise=WorkDetail.objects.filter(muster__panchayat=eachPanchayat,muster__finyear=finyear).aggregate(Sum('daysWorked')).get('daysWorked__sum')
  logger.info("Libtech Work Days")
  libtechWorkDays=WorkDetail.objects.filter(worker__jobcard__panchayat=eachPanchayat,muster__finyear=finyear).aggregate(Sum('daysWorked')).get('daysWorked__sum')
  if libtechWorkDays is None:
    libtechWorkDays=0
  if libtechWorkDaysPanchayatwise is None:
    libtechWorkDaysPanchayatwise = 0
  logger.info(libtechWorkDaysPanchayatwise)
  mustersPendingDownload=mustersTotal-mustersDownloaded
  mustersPendingProcessing=mustersDownloaded-mustersProcessed
  mustersMissingApplicant=mustersProcessed-mustersAllApplicantsFound
  mustersInComplete=mustersProcessed-mustersComplete
  logger.info("MustersTotal %d, musters Downloaded %d Muster Processed %d Musters Complete %d " % (mustersTotal,mustersDownloaded,mustersProcessed,mustersComplete))
  logger.info("mustersAllApplicantsFound %d, jobcards Total %d workers Total %d " % (mustersAllApplicantsFound,jobcardsTotal,workersTotal))
  logger.info("mustersPendingDownload %d,mustersPendingProcessing %d, mustersMissingApplicant %d, mustersInComplete %d " % (mustersPendingDownload,mustersPendingProcessing,mustersMissingApplicant,mustersInComplete))
  logger.info("Libtech WOrk Days %d, libtechWorkDaysPanchayatwise %d " % (libtechWorkDays,libtechWorkDaysPanchayatwise))
  myPanchayatStat=PanchayatStat.objects.filter(panchayat=eachPanchayat,finyear=finyear).first()
  if myPanchayatStat is None:
    PanchayatStat.objects.create(panchayat=eachPanchayat,finyear=finyear)
  myPanchayatStat=PanchayatStat.objects.filter(panchayat=eachPanchayat,finyear=finyear).first()
  nicWorkDays=myPanchayatStat.nicWorkDays
  myPanchayatStat.mustersTotal=mustersTotal
  myPanchayatStat.mustersPendingDownload=mustersPendingDownload
  myPanchayatStat.mustersPendingProcessing=mustersPendingProcessing
  myPanchayatStat.musterMissingApplicants=mustersMissingApplicant
  myPanchayatStat.mustersDownloaded=mustersDownloaded
  myPanchayatStat.mustersProcessed=mustersProcessed
  myPanchayatStat.mustersInComplete=mustersInComplete
  myPanchayatStat.jobcardsTotal=jobcardsTotal
  myPanchayatStat.workersTotal=workersTotal
  myPanchayatStat.libtechWorkDays=libtechWorkDays
  myPanchayatStat.libtechWorkDaysPanchayatwise=libtechWorkDaysPanchayatwise
  if (nicWorkDays is None) or (nicWorkDays == 0):
    workDaysAccuracyIndex =0
  else:
    workDaysAccuracyIndex=int(libtechWorkDays*100/nicWorkDays)
  myPanchayatStat.workDaysAccuracyIndex =workDaysAccuracyIndex
  myPanchayatStat.save() 
  return workDaysAccuracyIndex
 
def processPanchayatStat(logger,eachPanchayat):
  reportType="nicStatsHTML"
  curfinyear=getCurrentFinYear()
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
    nicTotalJobcards=None
    for row in rows:
      if "Total No. of Workers" in str(row):
        cols=row.findAll("td")
        wArray=[]
        for col in cols:
          wArray.append(col.text.lstrip().rstrip().replace(",",""))
        logger.info(str(wArray))  
        nicTotalApplicants=wArray[1]
      
      if "Total No. of JobCards issued" in str(row):
        cols=row.findAll("td")
        wArray=[]
        for col in cols:
          wArray.append(col.text.lstrip().rstrip().replace(",",""))
        logger.info(str(wArray))  
        nicTotalJobcards=wArray[1]
        
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
  
  curfinyear=getCurrentFinYear()
  mypanchayatStat=PanchayatStat.objects.filter(finyear=curfinyear,panchayat=eachPanchayat).first()
  if mypanchayatStat is None:
    PanchayatStat.objects.create(finyear=curfinyear,panchayat=eachPanchayat)
  myStat=PanchayatStat.objects.filter(finyear=curfinyear,panchayat=eachPanchayat).first()
  myStat.nicWorkersTotal=nicTotalApplicants
  myStat.nicJobcardsTotal=nicTotalJobcards 
  myStat.save()
  if statFound == 1:
    for i,finyear in enumerate(fArray):
      if i != 0:
        workDays=fArrayData[i]
        mypanchayatStat=PanchayatStat.objects.filter(finyear=finyear,panchayat=eachPanchayat).first()
        if mypanchayatStat is None:
          PanchayatStat.objects.create(finyear=finyear,panchayat=eachPanchayat)
        myStat=PanchayatStat.objects.filter(finyear=finyear,panchayat=eachPanchayat).first()
        myStat.nicWorkDays=workDays
        myStat.save()


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


def downloadPanchayatStat(logger,eachPanchayat):
  reportType="nicStatsHTML"
  finyear=getCurrentFinYear()
  statusURL="%s?panchayat_code=%s&panchayat_name=%s&block_code=%s&block_name=%s&district_code=%s&district_name=%s&state_code=%s&state_name=%s&page=p&fin_year=2014-2015" % (statsURL,eachPanchayat.code,eachPanchayat.name,eachPanchayat.block.code,eachPanchayat.block.name,eachPanchayat.block.district.code,eachPanchayat.block.district.name,eachPanchayat.block.district.state.code,eachPanchayat.block.district.state.name)
  logger.info(statusURL) 
 
  try:
    r  = requests.get(statusURL)
    error=None
  except requests.exceptions.RequestException as e:  # This is the correct syntax
    logger.info(e) 
    error=1
  if error is None:
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
  return error
 
def getNumberProcesses(q):
  if q < 10:
    n=1
  elif q < 100:
    n=10
  elif q< 500:
    n=40
  else:
    n=80
  return n

def parseMuster(logger,eachMuster):
  error=None
  if error is None:
    #logger.info("MusterID: %s MusterNo: %s, blockCode: %s, finyear: %s workName:%s" % (eachMuster.id,eachMuster.musterNo,eachMuster.block.code,eachMuster.finyear,eachMuster.workName))
#    logger.info(eachMuster.panchayat.code+eachMuster.panchayat.crawlRequirement+eachMuster.panchayat.name)
    myhtml=eachMuster.musterFile.read()

#Getting the Payment Date from Muster HTML
    s1=myhtml.decode("UTF-8").replace(u'\xa0', u' ')
    s=s1.replace("\n","").replace("\r","").replace(" ","")
    r=re.search('PaymentDate:([^\<]*)',s)
    if r is not None:
      paymentDateString=r.group(1).lstrip().rstrip()
      if paymentDateString != '':
        paymentDate = time.strptime(paymentDateString, '%d/%m/%Y')
        paymentDate = time.strftime('%Y-%m-%d', paymentDate)
      else:
        paymentDate=None
    else:
      paymentDate=None

    stateShortCode=eachMuster.block.district.state.stateShortCode
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    mytable=htmlsoup.find('table',id="musterDetails")
    tr_list = mytable.findAll('tr')
    acnoPresent=0
    for tr in tr_list: #This loop is to find staus Index
      cols = tr.findAll('th')
      if len(cols) > 7:
        i=0
        
        while i < len(cols):
          value="".join(cols[i].text.split())
          if "Status" in value:
            statusindex=i
          if ("Sharpening Charge" in cols[i].text) or ("औज़ार सम्बंधित भुगतान" in cols[i].text):
            sharpeningIndex=i
          if ("A/C No." in cols[i].text) or ("खाता क्रमांक" in cols[i].text):
            acnoPresent=1
          i=i+1
    isComplete=1
    allApplicantFound=1
    allWorkerFound=True
    totalCount=0
    totalPending=0
    reMatchString="%s-" % (stateShortCode)
    #logger.info("Account No Presnet: %s " % str(acnoPresent))
    #logger.info("Sharpening Index is %s " % str(sharpeningIndex))
    for i in range(len(tr_list)):
      cols=tr_list[i].findAll("td")
      if len(cols) > 7:
        nameandjobcard=cols[1].text.lstrip().rstrip()
        if stateShortCode in nameandjobcard:
          totalCount=totalCount+1
          status=cols[statusindex].text.lstrip().rstrip()
          if status != 'Credited':
            totalPending=totalPending+1
            isComplete=0      
          musterIndex=cols[0].text.lstrip().rstrip()
          nameandjobcard=cols[1].text.lstrip().rstrip()
          nameandjobcard=nameandjobcard.replace('\n',' ')
          nameandjobcard=nameandjobcard.replace("\\","")
          nameandjobcardarray=re.match(r'(.*)'+reMatchString+'(.*)',nameandjobcard)
          name_relationship=nameandjobcardarray.groups()[0]
          name=name_relationship.split("(")[0].lstrip().rstrip()
#          accountno=cols[statusindex-5].text.lstrip().rstrip()
          totalWage=cols[sharpeningIndex-2].text.lstrip().rstrip()
          dayWage=cols[sharpeningIndex-3].text.lstrip().rstrip()
          daysWorked=cols[sharpeningIndex-4].text.lstrip().rstrip()
          jobcard=reMatchString+nameandjobcardarray.groups()[1].lstrip().rstrip()
         #if acnoPresent == 1:
         #  totalWage=cols[statusindex-6].text.lstrip().rstrip()
         #  dayWage=cols[statusindex-10].text.lstrip().rstrip()
         #  daysWorked=cols[statusindex-11].text.lstrip().rstrip()
         #else:
         #  totalWage=cols[statusindex-5].text.lstrip().rstrip()
         #  dayWage=cols[statusindex-9].text.lstrip().rstrip()
         #  daysWorked=cols[statusindex-10].text.lstrip().rstrip()
          #logger.info("TotalWage: %s daywage: %s " % (totalWage,dayWage))
          wagelistNo=cols[statusindex-1].text.lstrip().rstrip()
          creditedDateString=cols[statusindex+1].text.lstrip().rstrip()
          if creditedDateString != '':
            creditedDate = time.strptime(creditedDateString, '%d/%m/%Y')
            creditedDate = time.strftime('%Y-%m-%d', creditedDate)
          else:
            creditedDate=None
        myWDRecord=WorkDetail.objects.filter(muster=eachMuster,musterIndex=musterIndex).first()
        if myWDRecord is None:
          #logger.info("New Record Created")
          WorkDetail.objects.create(muster=eachMuster,musterIndex=musterIndex)
        myWDRecord=WorkDetail.objects.filter(muster=eachMuster,musterIndex=musterIndex).first()
        
        matchedWagelist=Wagelist.objects.filter(wagelistNo=wagelistNo,block=eachMuster.panchayat.block,finyear=eachMuster.finyear).first()
        if matchedWagelist is None:
          try:
            Wagelist.objects.create(wagelistNo=wagelistNo,block=eachMuster.panchayat.block,finyear=eachMuster.finyear)
          except:
            logger.info("Wagelist created by Another Thread")
        matchedWagelist=Wagelist.objects.filter(wagelistNo=wagelistNo,block=eachMuster.panchayat.block,finyear=eachMuster.finyear).first()

        myWDRecord.wagelist.add(matchedWagelist)

        # Now we would create the record for all the  PaymentInfo
        myPaymentInfo=PaymentInfo.objects.filter(workDetail=myWDRecord,wagelist=matchedWagelist).first()
        if myPaymentInfo is None:
          myPaymentInfo=PaymentInfo.objects.create(workDetail=myWDRecord,wagelist=matchedWagelist)

        matchedWorkers=Worker.objects.filter(jobcard__jobcard=jobcard,name=name)
        if len(matchedWorkers) == 1:
          myWDRecord.worker=matchedWorkers.first()
        else:
          logger.info("Worker Not Found %s-%s " % (jobcard,name))
          allWorkerFound=False
           
        myWDRecord.zjcNo=getjcNumber(jobcard) 
        myWDRecord.zvilCode=getVilCode(jobcard) 
        myWDRecord.zname=name
        myWDRecord.zjobcard=jobcard
        myWDRecord.totalWage=totalWage
        myWDRecord.dayWage=dayWage
        myWDRecord.daysWorked=daysWorked
        myWDRecord.creditedDate=creditedDate
        myWDRecord.musterStatus=status 
        myWDRecord.save()
    eachMuster.isComplete=isComplete
    eachMuster.paymentDate=paymentDate
    eachMuster.isProcessed=1
    eachMuster.allApplicantFound=allApplicantFound
    eachMuster.allWorkerFound=allWorkerFound
    eachMuster.save()
    #logger.info("Processed Muster: MusterID: %s MusterNo: %s, blockCode: %s, finyear: %s workName:%s all ApplicantFound: %s " % (eachMuster.id,eachMuster.musterNo,eachMuster.block.code,eachMuster.finyear,eachMuster.workName,str(allApplicantFound)))
  
  return error

def validateDCReport(panchayat,myhtml):
  error=None
  dcTable=None
  jobcardPrefix=panchayat.block.district.state.stateShortCode+"-"
  if (jobcardPrefix in myhtml):
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if jobcardPrefix in str(table):
        dcTable=table
    if dcTable is None:
      error="Delay Compensation Table nout found"
  else:
    error="Jobcard Prefix not found"
  return error,dcTable


def downloadDelayedCompensationReport(logger,eachPanchayat,finyear):
  regexDC=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  stateCode=eachPanchayat.block.district.state.code
  fullDistrictCode=eachPanchayat.block.district.code
  fullBlockCode=eachPanchayat.block.code
  fullPanchayatCode=eachPanchayat.code
  districtName=eachPanchayat.block.district.name
  fullfinyear=getFullFinYear(finyear)
  blockName=eachPanchayat.block.name
  stateName=eachPanchayat.block.district.state.name
  crawlIP=eachPanchayat.block.district.state.crawlIP
  panchayatName=eachPanchayat.name
  url="http://%s/netnrega/state_html/delay_comp_dtl.aspx?page=p&state_name=%s&state_code=%s&fin_year=%s&district_name=%s&district_code=%s&block_name=%s&block_code=%s&panchayat_name=%s&panchayat_code=%s&source=national&" %(crawlIP,stateName,stateCode,fullfinyear,districtName,fullDistrictCode,blockName,fullBlockCode,panchayatName,fullPanchayatCode)
  logger.info(url)
  try:
    r  = requests.get(url)
    error=0
  except requests.exceptions.RequestException as e:  # This is the correct syntax
    logger.info(e) 
    error=1
  if error==0:
    curtime = time.strftime('%Y-%m-%d %H:%M:%S')
    htmlsource=r.text
    htmlsource1=re.sub(regexDC,"",htmlsource)
    error,dcTable=validateDCReport(eachPanchayat,htmlsource1)
    if error is None:
      outhtml=''
      outcsv=''
      outhtml+=stripTableAttributes(dcTable,"dcTable")
      outcsv+=table2csv(dcTable)
      title="Delay Compensation report state:%s District:%s block:%s panchayat: %s finyear:%s " % (stateName,districtName,blockName,panchayatName,fullfinyear)
      outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
      try:
        outhtml=outhtml.encode("UTF-8")
      except:
        outhtml=outhtml
  
      try:
        outcsv=outcsv.encode("UTF-8")
      except:
        outcsv=outcsv
      filename="dc_%s_%s.html" % (eachPanchayat.slug,finyear)
      csvfilename="dc_%s_%s.csv" % (eachPanchayat.slug,finyear)
      reportType="delayedCompensationHTML"
      savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,outhtml)
      reportType="delayCompensationCSV"
      savePanchayatReport(logger,eachPanchayat,finyear,reportType,csvfilename,outcsv)
 
def processMusters(logger,eachPanchayat,finyear):
  myMusters=Muster.objects.filter( isDownloaded=True,panchayat=eachPanchayat,finyear=finyear,isProcessed=False)
  logger.info("Number of Musters that needs to be Processed %s " % str(len(myMusters)))
  if len(myMusters) > 0:
    n=getNumberProcesses(len(myMusters))
    queueSize=n+len(myMusters)+10
    q = Queue(maxsize=queueSize)
    logger.info("Queue Size %s Numbe of Threads %s " % (str(queueSize),str(n)))
    for eachMuster in myMusters:
      q.put(eachMuster.id)
      eachMuster.musterDownloadAttemptDate=timezone.now()
      eachMuster.save()

    for i in range(n):
      logger.info("Starting worker Thread %s " % str(i))
      t = Thread(name = 'Thread-' + str(i), target=musterProcessWorker, args=(logger,q ))
      t.daemon = True  
      t.start()


    q.join()       # block until all tasks are done
    for i in range(n):
      q.put(None)

def musterProcessWorker(logger,q):
  while True:
    musterID = q.get()  # if there is no url, this will wait
    if musterID is None:
      break
    name = threading.currentThread().getName()

    eachMuster=Muster.objects.filter(id=musterID).first()
    error=parseMuster(logger,eachMuster)
    errorString='' 
    logger.info("Current Queue: %s Thread : %s musterID: %s musterNo: %s FullblockCode: %s status: %s" % (str(q.qsize()),name,str(eachMuster.id),eachMuster.musterNo,eachMuster.block.code,errorString))

    q.task_done()
 

def downloadMusters(logger,eachPanchayat,finyear):
  myMusters=Muster.objects.filter( Q(isDownloaded=False,panchayat=eachPanchayat,finyear=finyear) | Q(panchayat=eachPanchayat,finyear=finyear,isProcessed=True,isDownloaded=True,isComplete=False) ).order_by("downloadAttemptCount")
  logger.info("Number of Musters that needs to be download %s " % str(len(myMusters)))
  if len(myMusters) > 0:
    n=getNumberProcesses(len(myMusters))
    queueSize=n+len(myMusters)+10
    q = Queue(maxsize=queueSize)
    logger.info("Queue Size %s Numbe of Threads %s " % (str(queueSize),str(n)))
    for eachMuster in myMusters:
      q.put(eachMuster.id)
      eachMuster.musterDownloadAttemptDate=timezone.now()
      eachMuster.save()

    for i in range(n):
      logger.info("Starting worker Thread %s " % str(i))
      t = Thread(name = 'Thread-' + str(i), target=musterDownloadWorker, args=(logger,q ))
      t.daemon = True  
      t.start()


    q.join()       # block until all tasks are done
    for i in range(n):
      q.put(None)


def getMuster(logger,eachMuster):
  url = 'http://%s/netnrega/citizen_html/musternew.aspx' % (eachMuster.panchayat.block.district.state.crawlIP)
  #logger.info("Printing Muster URl %s" % url)
  headers = {
      'Accept-Encoding': 'gzip, deflate',
      'Accept-Language': 'en-US,en;q=0.8',
      'Upgrade-Insecure-Requests': '1',
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36 Vivaldi/1.91.867.42',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
  }
  stateName=eachMuster.panchayat.block.district.state.name
  districtName=eachMuster.panchayat.block.district.name
  blockName=eachMuster.panchayat.block.name
  panchayatName=eachMuster.panchayat.name
  workCode=eachMuster.workCode
  workName=eachMuster.workName
  panchayatCode=eachMuster.panchayat.code
  musterNo=eachMuster.musterNo
  fullfinyear=getFullFinYear(eachMuster.finyear)
  #logger.info(stateName+districtName+fullfinyear)
  dateArray=str(eachMuster.dateFrom).split("-")
  dateFrom="%s/%s/%s" % (dateArray[2],dateArray[1],dateArray[0])
  dateArray=str(eachMuster.dateTo).split("-")
  dateTo="%s/%s/%s" % (dateArray[2],dateArray[1],dateArray[0])

  params = (
      ('state_name', stateName),
      ('district_name', districtName),
      ('block_name', blockName),
      ('panchayat_name', panchayatName),
      ('workcode', workCode),
      ('panchayat_code', panchayatCode),
      ('msrno', musterNo),
      ('finyear', fullfinyear),
      ('dtfrm', dateFrom),
      ('dtto', dateTo),
      ('wn', workName),
      ('id', '1'),
  )

  response = requests.get(url, headers=headers, params=params)
  cookies = response.cookies
  #logger.info(cookies)
      
  response = requests.get(url, headers=headers, params=params, cookies=cookies)
  #logger.info(response.cookies)

  return response.text


def validateMusterHTML(muster,myhtml):
  error=None
  musterTable=None
  musterSummaryTable=None
  jobcardPrefix=muster.block.district.state.stateShortCode+"-"
  if (jobcardPrefix in myhtml):
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if muster.workCode in str(table):
        musterSummaryTable=table
    if musterSummaryTable is None:
      error="Muster Summary Table not found"
    musterTable=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
    if musterTable is None:
      error="Muster Table not found"
  else:
    error="Jobcard Prefix not found"
  return error,musterTable,musterSummaryTable


def musterDownloadWorker(logger,q):
  while True:
    musterID = q.get()  # if there is no url, this will wait
    if musterID is None:
      break
    name = threading.currentThread().getName()

    eachMuster=Muster.objects.filter(id=musterID).first()
    try:
      myhtml=getMuster(logger,eachMuster)
      myhtml=myhtml.replace("</td></td>","</td>")
      error,musterTable,musterSummaryTable=validateMusterHTML(eachMuster,myhtml)
    except:
      error="downloadError"
  
    if error is None:
      errorString="No ERROR"
    else:
      errorString=error

    logger.info("Current Queue: %s Thread : %s musterID: %s musterNo: %s FullblockCode: %s status: %s" % (str(q.qsize()),name,str(eachMuster.id),eachMuster.musterNo,eachMuster.block.code,errorString))
    #logger.info(eachMuster.musterURL)

    if error is None:  
      outhtml=''
      outhtml+=stripTableAttributes(musterSummaryTable,"musterSummary")
      outhtml+=stripTableAttributes(musterTable,"musterDetails")
      title="Muster: %s state:%s District:%s block:%s finyear:%s " % (eachMuster.musterNo,eachMuster.block.district.state.name,eachMuster.block.district.name,eachMuster.block.name,getFullFinYear(eachMuster.finyear))
      outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
      try:
        outhtml=outhtml.encode("UTF-8")
      except:
        outhtml=outhtml
      filename="%s.html" % (eachMuster.musterNo)
      eachMuster.musterFile.save(filename, ContentFile(outhtml))
      eachMuster.musterDownloadAttemptDate=timezone.now()
      eachMuster.downloadAttemptCount=eachMuster.downloadAttemptCount+1
      eachMuster.downloadCount=eachMuster.downloadCount+1
      eachMuster.isDownloaded=True
      eachMuster.isProcessed=False
      eachMuster.save()
    else:
      eachMuster.musterDownloadAttemptDate=timezone.now()
      eachMuster.downloadAttemptCount=eachMuster.downloadAttemptCount+1
      eachMuster.downloadError=error
      eachMuster.save()

    q.task_done()
 
def processJobcardRegister(logger,eachPanchayat):
  reportType="applicationRegister"
  curfinyear=getCurrentFinYear()
  logger.info(eachPanchayat.name+","+eachPanchayat.code)
  panchayatReport=PanchayatReport.objects.filter(reportType=reportType,finyear=curfinyear,panchayat=eachPanchayat).first()
  if panchayatReport is not None:
    logger.info("Panchayat Report Exists")
    myhtml=panchayatReport.reportFile.read()  
    logger.info("Read the HTML")
    htmlsoup=BeautifulSoup(myhtml,"lxml")
    myTable=htmlsoup.find('table',id="myTable")
    jobcardPrefix=eachPanchayat.block.district.state.stateShortCode+"-"
    logger.info(jobcardPrefix)
    if myTable is not None:
      logger.info("Found the table")
      rows=myTable.findAll('tr')
      headOfHousehold=''
      applicantNo=0
      fatherHusbandName=''
      village=''
      for row in rows:
        if "Villages : " in str(row):
          logger.info("Village Name Found")
          cols=row.findAll('td')
          villagestr=cols[0].text.lstrip().rstrip()
          villageName=villagestr.replace("Villages :" ,"").lstrip().rstrip()
          logger.info(villageName)
          myVillage=Village.objects.filter(panchayat=eachPanchayat,name=villageName).first()
          if myVillage is None:
            Village.objects.create(panchayat=eachPanchayat,name=villageName)
          myVillage=Village.objects.filter(panchayat=eachPanchayat,name=villageName).first()
          logger.info(myVillage) 
        if jobcardPrefix in str(row):
          isDeleted=False
          isDisabled=False
          isMinority=False
          cols=row.findAll('td')
          rowIndex=cols[0].text.lstrip().rstrip()
          jobcard=cols[9].text.lstrip().rstrip().split(",")[0]
          if len(cols[9].text.lstrip().rstrip().split(",")) > 1:
            issueDateString=cols[9].text.lstrip().rstrip().split(",")[1]
          else:
            issueDateString=''
          gender=cols[6].text.lstrip().rstrip()
          age=cols[7].text.lstrip().rstrip()
          applicationDateString=cols[8].text.lstrip().rstrip()
          remarks=cols[10].text.lstrip().rstrip()
          disabledString=cols[11].text.lstrip().rstrip()
          minorityString=cols[12].text.lstrip().rstrip()
          name=cols[4].text.lstrip().rstrip()
          logger.info("Processing %s - %s " % (jobcard,name))
          issueDate=correctDateFormat(issueDateString)
          applicationDate=correctDateFormat(applicationDateString)
          if cols[1].text.lstrip().rstrip() != '':
            headOfHousehold=cols[1].text.lstrip().rstrip()
            caste=cols[2].text.lstrip().rstrip()
            applicantNo=1
            fatherHusbandName=cols[5].text.lstrip().rstrip()
            #Gather Jobcard Replated Info
            myJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
            if myJobcard is None:
              Jobcard.objects.create(jobcard=jobcard,panchayat=eachPanchayat)
            myJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
            myJobcard.jcNo=getjcNumber(jobcard)
            myJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
            myJobcard.caste=caste
            myJobcard.headOfHousehold=headOfHousehold
            myJobcard.village=myVillage
            myJobcard.issueDate=issueDate
            myJobcard.applicantDate=applicationDate
            myJobcard.save()  
          else:
            applicantNo=applicantNo+1
          if '*' in name:
            isDeleted=True
          if disabledString == 'Y':
            isDisabled=True
          if minorityString == 'Y':
            isMinority=True
          name=name.rstrip('*')
          myWorker=Worker.objects.filter(jobcard=myJobcard,name=name).first()
          if myWorker is None:
            Worker.objects.create(jobcard=myJobcard,name=name,applicantNo=applicantNo)
          myWorker=Worker.objects.filter(jobcard=myJobcard,name=name).first()
          logger.info(applicantNo)
          myWorker.applicantNo=applicantNo
          myWorker.gender=gender
          myWorker.age=age
          myWorker.fatherHusbandName=fatherHusbandName
          myWorker.isDeleted=isDeleted
          myWorker.isDisabled=isDisabled
          myWorker.isMinority=isMinority
          myWorker.remarks=remarks
          myWorker.save() 
 


def saveJobcardRegister(logger,eachPanchayat):
  finyear=getCurrentFinYear()
  fullfinyear=getFullFinYear(finyear)
  myhtml=getJobcardRegister1(logger,eachPanchayat)
  with open("/tmp/a.html","wb") as f:
    f.write(myhtml)
#  myhtml=str(myhtml).replace("</nobr><br>",",")
#  myhtml=myhtml.encode("UTF-8")
  myhtml=myhtml.replace(b'</nobr><br>',b',')
  myhtml=myhtml.replace(b"bordercolor='#111111'>",b"bordercolor='#111111'><tr>")
  error,myTable=validateApplicationRegister(logger,myhtml,eachPanchayat.block)
  logger.info(error)
  
  if error is None:
    logger.info("No error")
    outhtml=''
    outhtml+=stripTableAttributes(myTable,"myTable")
    title="Jobcard Register: state:%s District:%s block:%s panchayat: %s finyear:%s " % (eachPanchayat.block.district.state.name,eachPanchayat.block.district.name,eachPanchayat.block.name,eachPanchayat.name,fullfinyear)
    outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
    try:
      outhtml=outhtml.encode("UTF-8")
    except:
      outhtml=outhtml
    with open("/tmp/out.html","wb") as f:
      f.write(outhtml)
    filename="applicationRegister_%s_%s.html" % (eachPanchayat.slug,finyear)
    reportType="applicationRegister"
    savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,outhtml)
    eachPanchayat.applicationRegisterCrawlDate=timezone.now()
    eachPanchayat.save() 
  else:
    logger.info("Error")
  return error

def validateApplicationRegister(logger,myhtml,block):
  error=None
  myTable=None
  jobcardPrefix=block.district.state.stateShortCode+"-"
  if (jobcardPrefix in str(myhtml)):
    htmlsoup=BeautifulSoup(myhtml,"lxml")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if "Head of HouseHold"  in str(table):
        myTable=table
  else:
    error="job card Prefix not found"
  if myTable is None:
    error="Table not found"
  return error,myTable

def getJobcardRegister(logger,eachPanchayat):
  logger.info("Processing : panchayat: %s " % (eachPanchayat.name))
  stateCode=eachPanchayat.block.district.state.code
  fullDistrictCode=eachPanchayat.block.district.code
  fullBlockCode=eachPanchayat.block.code
  fullPanchayatCode=eachPanchayat.code
  districtName=eachPanchayat.block.district.name
  blockName=eachPanchayat.block.name
  stateName=eachPanchayat.block.district.state.name
  panchayatName=eachPanchayat.name
  crawlIP=eachPanchayat.block.district.state.crawlIP
  finyear=getCurrentFinYear()
  fullfinyear=getFullFinYear(finyear) 
  logger.info("Processing StateCode %s, fullDistrictCode : %s, fullBlockCode : %s, fullPanchayatCode: %s " % (stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode))
  panchayatPageURL="http://%s/netnrega/IndexFrame.aspx?lflag=eng&District_Code=%s&district_name=%s&state_name=%s&state_Code=%s&block_name=%s&block_code=%s&fin_year=%s&check=1&Panchayat_name=%s&Panchayat_Code=%s" % (crawlIP,fullDistrictCode,districtName,stateName,stateCode,blockName,fullBlockCode,fullfinyear,panchayatName,fullPanchayatCode)
  panchayatDetailURL="http://%s/netnrega/Citizen_html/Panchregpeople.aspx" % crawlIP
  #panchayatDetailURL="http://mnregaweb2.nic.in/netnrega/writereaddata/citizen_out/panchregpeople_2721001029_eng1718.html"
  panchayatDetailURL="http://%s/netnrega/writereaddata/citizen_out/panchregpeople_%s_eng1718.html" % (crawlIP,fullPanchayatCode)
  logger.info(panchayatPageURL)
  logger.info(panchayatDetailURL)
  #Starting the Download Process
  url="http://nrega.nic.in/netnrega/home.aspx"
  #response = requests.get(url, headers=headers, params=params)
  response = requests.get(panchayatPageURL)
  cookies = response.cookies
  logger.info(cookies)
  headers = {
    #'Host': 'nregasp2.nic.in',
    'Host': crawlIP,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
#    'Referer': panchayatPageURL,
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

  params = (
    ('lflag', 'eng'),
    ('fin_year', fullfinyear),
    ('Panchayat_Code', fullPanchayatCode),
    ('type', 'a'),
  )

  response=requests.get(panchayatDetailURL, headers=headers, params=params, cookies=cookies)
  logger.info("Downloaded StateCode %s, fullDistrictCode : %s, fullBlockCode : %s, fullPanchayatCode: %s " % (stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode))
  return response.content


def getJobcardRegister1(logger,eachPanchayat):
  logger.info("Processing : panchayat: %s " % (eachPanchayat.name))
  stateCode=eachPanchayat.block.district.state.code
  fullDistrictCode=eachPanchayat.block.district.code
  fullBlockCode=eachPanchayat.block.code
  fullPanchayatCode=eachPanchayat.code
  districtName=eachPanchayat.block.district.name
  blockName=eachPanchayat.block.name
  stateName=eachPanchayat.block.district.state.name
  panchayatName=eachPanchayat.name
  crawlIP=eachPanchayat.block.district.state.crawlIP
  finyear=getCurrentFinYear()
  fullfinyear=getFullFinYear(finyear) 
  logger.info("Processing StateCode %s, fullDistrictCode : %s, fullBlockCode : %s, fullPanchayatCode: %s " % (stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode))
  panchayatPageURL="http://%s/netnrega/IndexFrame.aspx?lflag=eng&District_Code=%s&district_name=%s&state_name=%s&state_Code=%s&block_name=%s&block_code=%s&fin_year=%s&check=1&Panchayat_name=%s&Panchayat_Code=%s" % (crawlIP,fullDistrictCode,districtName,stateName,stateCode,blockName,fullBlockCode,fullfinyear,panchayatName,fullPanchayatCode)
#  panchayatPageURL=panchayatPageURL.replace(" ","+")
  panchayatDetailURL="http://%s/netnrega/Citizen_html/Panchregpeople.aspx" % crawlIP
  logger.info(panchayatPageURL)
  logger.info(panchayatDetailURL)
  #Starting the Download Process
  url="http://nrega.nic.in/netnrega/home.aspx"
  #response = requests.get(url, headers=headers, params=params)
  response = requests.get(panchayatPageURL)
  myhtml=str(response.content)
  splitString="Citizen_html/Panchregpeople.aspx?lflag=eng&fin_year=%s&Panchayat_Code=%s&type=a&Digest=" % (fullfinyear,fullPanchayatCode)
  myhtmlArray=myhtml.split(splitString)
  myArray=myhtmlArray[1].split('"')
  digest=myArray[0]
  cookies = response.cookies
  logger.info(cookies)
  headers = {
    'Host': crawlIP,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
#    'Referer': panchayatPageURL,
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

  params = (
    ('lflag', 'eng'),
    ('fin_year', fullfinyear),
    ('Panchayat_Code', fullPanchayatCode),
    ('type', 'a'),
    ('Digest', digest),

  )

  response=requests.get(panchayatDetailURL, headers=headers, params=params, cookies=cookies)
  logger.info("Downloaded StateCode %s, fullDistrictCode : %s, fullBlockCode : %s, fullPanchayatCode: %s " % (stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode))
  return response.content

def fetchDataTelanganaJobcardRegister(logger,fullPanchayatCode,eachPanchayat):
  stateCode='02'
  districtCode=eachPanchayat.block.district.code[-2:]
  blockCode=eachPanchayat.block.tcode[-2:]
  #districtCode=fullPanchayatCode[2:4]
  #blockCode=fullPanchayatCode[5:7]
  panchayatCode=fullPanchayatCode[8:10]
  logger.info("DistrictCode: %s, blockCode : %s , panchayatCode: %s " % (districtCode,blockCode,panchayatCode))
  headers = {
    'Host': 'www.nrega.telangana.gov.in',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=Common_Ajax_engRH&actionVal=Display&page=commondetails_eng',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

  params = (
    ('requestType', 'Household_engRH'),
    ('actionVal', 'view'),
)

  data = [
  ('State', '02'),
  ('District', districtCode),
  ('Mandal', blockCode),
  ('Panchayat', panchayatCode),
  ('Village', '-1'),
  ('HouseHoldId', ''),
  ('Go', ''),
  ('spl', 'Select'),
  ('input2', ''),
]
  url='http://www.nrega.telangana.gov.in/Nregs/FrontServlet'
  response = requests.post(url, headers=headers, params=params, data=data)
  cookies = response.cookies
  logger.info(cookies)
      
  logger.info(response.cookies)
  response=requests.post('http://www.nrega.telangana.gov.in/Nregs/FrontServlet', headers=headers, params=params, cookies=cookies, data=data)
  return response.text

def validateDataTelanganaJobcardRegister(logger,myhtml):
  error=None
  myTable=None
  htmlsoup=BeautifulSoup(myhtml,"html.parser")
  myTable=htmlsoup.find('table',id='sortable')
  if myTable is None:
    logger.info("Table not found")
    error="Table not found"
  return error,myTable


def processJobcardRegisterTelangana(logger,eachPanchayat):
  finyear=getCurrentFinYear()
  fullfinyear=getFullFinYear(finyear)
  reportType="telanganaJobcardRegister"
  logger.info(eachPanchayat.block.name+eachPanchayat.code+eachPanchayat.name) 
  panchayatReport=PanchayatReport.objects.filter(reportType=reportType,finyear=finyear,panchayat=eachPanchayat).first()
  fullPanchayatCode=eachPanchayat.code
  districtCode=eachPanchayat.block.district.code[-2:]
  #jobcardPrefix="TS-%s-" %(districtCode)
  jobcardPrefix="TS-" 
  if panchayatReport is not None:
    logger.info("Panchayat Report Exists")
    myhtml=panchayatReport.reportFile.read()  
    #myhtml=eachPanchayat.jobcardRegisterFile.read()
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    myTable=htmlsoup.find('table',id="myTable")
    rows=myTable.findAll("tr")
    for row in rows:
      if jobcardPrefix in str(row):
        cols=row.findAll('td')
        tjobcard=cols[1].text.lstrip().rstrip()
        jobcard=cols[2].text.lstrip().rstrip()
        myJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
        if myJobcard is None:
          Jobcard.objects.create(jobcard=jobcard)
        myJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
        myJobcard.panchayat=eachPanchayat
        myJobcard.tjobcard=tjobcard
        myJobcard.isRequired=1
        logger.info(tjobcard+jobcard)
        myJobcard.save()
   
def saveJobcardRegisterTelangana(logger,eachPanchayat):
  error=None
  finyear=getCurrentFinYear()
  fullfinyear=getFullFinYear(finyear)
  reportType="telanganaJobcardRegister"
  logger.info("Saving Jobcard Register for Telangana")
  fullPanchayatCode=eachPanchayat.code
  stateName=eachPanchayat.block.district.state.name
  districtName=eachPanchayat.block.district.name
  blockName=eachPanchayat.block.name
  panchayatName=eachPanchayat.name

  myhtml=fetchDataTelanganaJobcardRegister(logger,fullPanchayatCode,eachPanchayat)
  myhtml=myhtml.replace("<tbody>","")
  myhtml=myhtml.replace("</tbody>","")
  error,myTable=validateDataTelanganaJobcardRegister(logger,myhtml) 
  if error is  None:
    logger.info('No Error')
    outhtml=''
    outhtml+=stripTableAttributes(myTable,"myTable")
    title="jobcards state:%s District:%s block:%s panchayat: %s finyear:%s " % (stateName,districtName,blockName,panchayatName,fullfinyear)
    outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
    try:
      outhtml=outhtml.encode("UTF-8")
    except:
      outhtml=outhtml
    filename="jr_%s_%s.html" % (eachPanchayat.slug,finyear)
    savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,outhtml)
 
  return error



def downloadJobcardsTelangana(logger,eachPanchayat):
  myJobcards=Jobcard.objects.filter(panchayat=eachPanchayat)
  logger.info("Number of Musters that needs to be download %s " % str(len(myJobcards)))
  if len(myJobcards) > 0:
    n=getNumberProcesses(len(myJobcards))
    queueSize=n+len(myJobcards)+10
    q = Queue(maxsize=queueSize)
    logger.info("Queue Size %s Numbe of Threads %s " % (str(queueSize),str(n)))
    for eachJobcard in myJobcards:
      q.put(eachJobcard.id)
      eachJobcard.downloadAttemptDate=timezone.now()
      eachJobcard.save()

    for i in range(n):
      logger.info("Starting worker Thread %s " % str(i))
      t = Thread(name = 'Thread-' + str(i), target=jobcardDownloadWorker, args=(logger,q ))
      t.daemon = True  
      t.start()


    q.join()       # block until all tasks are done
    for i in range(n):
      q.put(None)

def fetchJobcardTelangana(logger,tjobcard):
  headers = {
    'Host': 'www.nrega.telangana.gov.in',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=HouseholdInf_engRH&actionVal=SearchJOB&JOB_No=152003910014010001',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

  params = (
    ('requestType', 'HouseholdInf_engRH'),
    ('actionVal', 'SearchJOB'),
    ('JOB_No', tjobcard),
)
  url='http://www.nrega.telangana.gov.in/Nregs/FrontServlet'
  response=requests.get(url, headers=headers, params=params)
  cookies = response.cookies
  logger.info(cookies)
  logger.info(response.cookies)
  response=requests.get(url, headers=headers, params=params, cookies=cookies)
  return response.text

def validateJobcardDataTelangana(logger,myhtml):
  habitation=None
  result = re.search('Habitation(.*)nbsp',myhtml)
  if result is not None:
     logger.info("Found")
     searchText=result.group(1)
     habitation=searchText.replace("&nbsp","").replace(":","").replace(";","").replace("&","").lstrip().rstrip()
     logger.info(habitation)
  error=None
  jobcardTable=None
  workerTable=None
  aggregateTable=None
  paymentTable=None
  error="noError"
  bs = BeautifulSoup(myhtml, "html.parser")
  bs = BeautifulSoup(myhtml, "lxml")
  main1 = bs.find('div',id='main1')
  logger.debug("Main1[%s]" % main1)

  if main1 != None:
    table1 = main1.find('table')
    logger.debug("Table1[%s]" % table1)

    jobcardTable = table1.find('table', id='sortable')

    workerTable = jobcardTable.findNext('table', id='sortable')
  main2 = bs.find(id='main2')
  if main2 is not  None:
    aggregateTable = main2.find('table')
  main3 = bs.find(id='main3')
  if main3 is not  None:
    paymentTable = main3.find('table')
  if jobcardTable is None:
    error+="jobcardTable not found"
  if workerTable is None:
    error+="WorkerTable not found     " 
  if aggregateTable is None:
    error+="Aggregate Table not found"
  if paymentTable is None:
    error+="Payment Table not found"
  if error == "noError":
    error=None
  return error,habitation,jobcardTable,workerTable,aggregateTable,paymentTable


def jobcardDownloadWorker(logger,q):
  while True:
    jobcardID = q.get()  # if there is no url, this will wait
    if jobcardID is None:
      break
    name = threading.currentThread().getName()

    eachJobcard=Jobcard.objects.filter(id=jobcardID).first()
    logger.info("Current Queue: %s Thread : %s musterID: %s tjobcard: %s " % (str(q.qsize()),name,str(eachJobcard.id),eachJobcard.tjobcard))
    logger.info(eachJobcard.tjobcard) 
    tjobcard=eachJobcard.tjobcard
    eachPanchayat=eachJobcard.panchayat
    stateName=eachPanchayat.block.district.state.name
    districtName=eachPanchayat.block.district.name
    blockName=eachPanchayat.block.name
    panchayatName=eachPanchayat.name
    
    myhtml=fetchJobcardTelangana(logger,tjobcard)
    error,villageName,jobcardTable,workerTable,aggregateTable,paymentTable=validateJobcardDataTelangana(logger,myhtml)
    if error is None:
      logger.info("Yipee no Error")
        
      outhtml=''
      outhtml+=getCenterAlignedHeading("Jobcard Details")      
      outhtml+=stripTableAttributes(jobcardTable,"jobcardTable")
      outhtml+=getCenterAlignedHeading("Worker Details")      
      outhtml+=stripTableAttributes(workerTable,"workerTable")
      outhtml+=getCenterAlignedHeading("Aggregate Work Details")      
      outhtml+=stripTableAttributes(aggregateTable,"aggregateTable")
      outhtml+=getCenterAlignedHeading("Payment Details")      
      outhtml+=stripTableAttributes(paymentTable,"paymentTable")
      title="Jobcard Details state:%s District:%s block:%s panchayat: %s jobcard:%s " % (stateName,districtName,blockName,panchayatName,tjobcard)
      outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
      try:
        outhtml=outhtml.encode("UTF-8")
      except:
        outhtml=outhtml
    
      filename="%s.html" % (tjobcard)
      eachJobcard.jobcardFile.save(filename, ContentFile(outhtml))
      if villageName is not None:
        myVillage=Village.objects.filter(panchayat=eachPanchayat,name=villageName).first()
        if myVillage is None:
          Village.objects.create(panchayat=eachPanchayat,name=villageName)
        myVillage=Village.objects.filter(panchayat=eachPanchayat,name=villageName).first()
        eachJobcard.village=myVillage
      eachJobcard.isDownloaded=True
      eachJobcard.isProcessed=False
      eachJobcard.downloadAttemptCount=eachJobcard.downloadAttemptCount+1
      eachJobcard.downloadCount=eachJobcard.downloadCount+1
      eachJobcard.downloadAttemptDate=timezone.now()
      eachJobcard.downloadDate=timezone.now()
      eachJobcard.downloadError=None
    else:
      logger.info("Error: %s " % error)
      eachJobcard.downloadAttemptDate=timezone.now()
      eachJobcard.downloadAttemptCount=eachJobcard.downloadAttemptCount+1
      #eachJobcard.downloadError=error
    eachJobcard.save()
    processJobcardTelangana(logger,eachJobcard)
    q.task_done()


def processJobcardTelangana(logger,eachJobcard):
  regex=re.compile("^[0-9]{4}-[0-9]{4}$")
  benchMark = datetime.datetime.strptime(telanganaThresholdDate, "%Y-%m-%d") 
  telanganaStateCode='36'
  logger.info(eachJobcard.tjobcard+"-"+eachJobcard.jobcard)
  tjobcard=eachJobcard.tjobcard
  jobcard=eachJobcard.jobcard
  eachPanchayat=eachJobcard.panchayat
  myhtml=eachJobcard.jobcardFile.read()  
  #To find teh surname
  m=re.findall ('Surname</td><td>(.*?)</td>',str(myhtml.decode("UTF-8")),re.DOTALL)
  if len(m)>0:
    surname=m[0].lstrip().rstrip()
  else:
    surname=''
  logger.info("surname is %s " % surname)
  m=re.findall ('Head of the Family</td><td>(.*?)</td>',str(myhtml.decode("UTF-8")),re.DOTALL)
  if len(m)>0:
    headOfFamily=m[0].lstrip().rstrip()
  else:
    headOfFamily=''
  logger.info("headOfFamily is %s " % headOfFamily)
  m=re.findall ('Caste</td><td>(.*?)</td>',str(myhtml.decode("UTF-8")),re.DOTALL)
  if len(m)>0:
    caste=m[0].lstrip().rstrip()
  else:
    caste=''
  logger.info("caste is %s " % caste)
  #myhtml=eachPanchayat.jobcardRegisterFile.read()
  htmlsoup=BeautifulSoup(myhtml,"lxml")
  myTable=htmlsoup.find('table',id="workerTable")
  allApplicantFound=True
  if  "Relationship" in str(myTable):
    logger.info("Found the Worker Table")
    rows=myTable.findAll('tr')
    for row in rows:
      cols=row.findAll('td')
      if len(cols)>0:
        logger.info(str(row))
        applicantNo=cols[1].text.lstrip().rstrip()
        if applicantNo.isdigit():
          applicantNo=int(applicantNo)
        else:
      #  if isinstance(applicantNo,int) is False:
          applicantNo=0
        logger.info("applicantNo is %s " % str(applicantNo)) 
        name=cols[2].text.lstrip().rstrip()
        logger.info(str(applicantNo)+name)
        myWorker=Worker.objects.filter(jobcard=eachJobcard,name=name).first()
        if myWorker is None:
           myWorker=Worker.objects.create(jobcard=eachJobcard,name=name,applicantNo=applicantNo)
        myWorker.applicantNo=applicantNo
        myWorker.gender=cols[4].text.lstrip().rstrip()
        myWorker.age=cols[3].text.lstrip().rstrip()
        myWorker.relationship=cols[5].text.lstrip().rstrip()
        myWorker.save()

        myApplicant=Applicant.objects.filter(jobcard=eachJobcard,applicantNo=applicantNo).first()
        if myApplicant is None:
          logger.info("Applicant not Found")
          Applicant.objects.create(jobcard=eachJobcard,applicantNo=applicantNo,panchayat=eachPanchayat)
          myApplicant=Applicant.objects.filter(jobcard=eachJobcard,applicantNo=applicantNo).first()
          myApplicant.source='tel'
          allApplicantFound=False
        else:
          logger.info("Applicant Found")
        myApplicant.panchayat=eachPanchayat
        myApplicant.gender=cols[4].text.lstrip().rstrip()
        myApplicant.age=cols[3].text.lstrip().rstrip()
        myApplicant.relationship=cols[5].text.lstrip().rstrip()
        myApplicant.name=name
        logger.info("Applicant Id is %d" %myApplicant.id)
        myApplicant.save()
  
  myTable=htmlsoup.find('table',id="paymentTable")
  rows=myTable.findAll('tr')
  for row in rows:
    cols=row.findAll('td')
    if len(cols)>0:
      epayorderNo=cols[0].text.lstrip().rstrip()
      payorderDateString=cols[5].text.lstrip().rstrip()
      applicantName=cols[8].text.replace(surname,"").lstrip().rstrip()
      fullApplicantName=cols[8].text.lstrip().rstrip()
      applicantName=re.sub(surname, '', fullApplicantName, flags=re.IGNORECASE).lstrip().rstrip()
      applicantName=cols[8].text.lstrip().lstrip(surname).lstrip(surname.title()).lstrip().rstrip()
      logger.info("Applicant Name after subtrancting surname is %s " % (applicantName))
      applicantNameArray=cols[8].text.lstrip().rstrip().split()
      if epayorderNo != "Total":
        logger.info(epayorderNo+" "+str(applicantNameArray)) 
        #surname=applicantNameArray[0]
        #name=applicantNameArray[1]
        transactionDateString=cols[5].text.lstrip().rstrip()
        transactionDate=getTelanganaDate(transactionDateString,'smallYear')
        myWorker=Worker.objects.filter(jobcard__jobcard=jobcard,name=applicantName).first()
        if myWorker is not None:
          ftoNo=cols[1].text.lstrip().rstrip()
          finyear=str(int(ftoNo[5:7])+1)
          myFTO=FTO.objects.filter(ftoNo=ftoNo,finyear=finyear,block=eachPanchayat.block).first()
          if myFTO is None:
            FTO.objects.create(ftoNo=ftoNo,finyear=finyear,block=eachPanchayat.block)
          myFTO=FTO.objects.filter(ftoNo=ftoNo,finyear=finyear,block=eachPanchayat.block).first()
  
          payorderNo=cols[7].text.lstrip().rstrip()
          creditedAmount=cols[11].text.lstrip().rstrip()
          daysWorked=cols[10].text.lstrip().rstrip()
          processedDateString=cols[12].text.lstrip().rstrip()
          disbursedAmount=cols[13].text.lstrip().rstrip()
          disbursedDateString=cols[14].text.lstrip().rstrip()
          processedDate=getTelanganaDate(processedDateString,'smallYear')
          disbursedDate=getTelanganaDate(disbursedDateString,'bigYear')
          myPaymentRecord=PaymentDetail.objects.filter(fto=myFTO,referenceNo=epayorderNo).first()
          if myPaymentRecord is None:
            PaymentDetail.objects.create(fto=myFTO,referenceNo=epayorderNo)
          myPaymentRecord=PaymentDetail.objects.filter(fto=myFTO,referenceNo=epayorderNo).first()
          myPaymentRecord.worker=myWorker
          myPaymentRecord.payorderNo=payorderNo
          myPaymentRecord.transactionDate=transactionDate
          myPaymentRecord.processDate=processedDate
          myPaymentRecord.disbursedDate=disbursedDate
          myPaymentRecord.daysWorked=daysWorked
          myPaymentRecord.creditedAmount=creditedAmount
          myPaymentRecord.disbursedAmount=disbursedAmount
          myPaymentRecord.save()
        else:
          logger.info("Applicant Not Found")
          if transactionDate >= benchMark:
            allApplicantFound=False
  
  myTable=htmlsoup.find('table',id="aggregateTable")
  rows=myTable.findAll('tr')
  for row in rows:
    cols=row.findAll('td')
    if len(cols)>0:
      fullfinyear=cols[0].text.lstrip().rstrip()
      if regex.match(fullfinyear):
        totalWorkDays=cols[1].text.lstrip().rstrip()
        totalWage=cols[2].text.lstrip().rstrip()
        finyear=fullfinyear[-2:]
        if totalWorkDays !='':
          myStat=Stat.objects.filter(jobcard=eachJobcard,finyear=finyear,statType="TWD").first()
          if myStat is None:
            Stat.objects.create(jobcard=eachJobcard,finyear=finyear,statType="TWD")
          myStat=Stat.objects.filter(jobcard=eachJobcard,finyear=finyear,statType="TWD").first()
          myStat.value=totalWorkDays
          myStat.save()
        if totalWage !='':
          myStat=Stat.objects.filter(jobcard=eachJobcard,finyear=finyear,statType="TWA").first()
          if myStat is None:
            Stat.objects.create(jobcard=eachJobcard,finyear=finyear,statType="TWA")
          myStat=Stat.objects.filter(jobcard=eachJobcard,finyear=finyear,statType="TWA").first()
          myStat.value=totalWage
          myStat.save()
  
  
  eachJobcard.allApplicantFound=allApplicantFound
  eachJobcard.surname=surname
  eachJobcard.jcNo=getjcNumber(jobcard)
  eachJobcard.headOfHousehold=headOfFamily
  eachJobcard.caste=caste
  eachJobcard.isProcessed=True
  logger.info("Processed Jobcard: %s,allApplicant FOund: %s " % (jobcard,str(allApplicantFound)))
  eachJobcard.save()


def createPaymentReportTelangana(logger,eachPanchayat,finyear):
  logger.info("Creating a Payment Report %s " % finyear)
  panchayatName=eachPanchayat.slug
  logger.info(panchayatName)
  myPaymentDetails=PaymentDetail.objects.filter(worker__jobcard__panchayat=eachPanchayat,fto__finyear=finyear)
#  myPaymentDetails=PaymentDetail.objects.filter(worker__jobcard__panchayat=eachPanchayat)
  reportType="paymentDetailsTelangana"
  outcsv=''
  outcsv+="Panchayat,name,jobcard,fto,payorderNo,epayorderno,creditedAmount,payOrderDate,creditedDate,disbursedDate,CreditedPayorderDiff,DisbusedCreditedDate,pendingDays\n"
  logger.info(len(myPaymentDetails))
  for eachPayment in myPaymentDetails:
    if eachPayment.processDate is not None and eachPayment.transactionDate is not None:
      creditedPayorderDiff=(eachPayment.processDate-eachPayment.transactionDate).days
    else:
      creditedPayorderDiff=''
    if eachPayment.transactionDate is not None and eachPayment.disbursedDate is None:
      pendingDays=(datetime.datetime.now().date()-eachPayment.transactionDate).days
    else:
      pendingDays=''
    if eachPayment.disbursedDate is not None and eachPayment.processDate is not None:
      disbursedCreditedDiff=(eachPayment.disbursedDate-eachPayment.processDate).days
    else:
      disbursedCreditedDiff=''
    outcsv+="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (panchayatName,eachPayment.worker.name,"~"+eachPayment.worker.jobcard.tjobcard,eachPayment.fto.ftoNo,eachPayment.payorderNo,eachPayment.referenceNo,eachPayment.creditedAmount,str(eachPayment.transactionDate),str(eachPayment.processDate),str(eachPayment.disbursedDate),str(creditedPayorderDiff),str(disbursedCreditedDiff),str(pendingDays))
  try:
    outcsv=outcsv.encode("UTF-8")
  except:
    outcsv=outcsv
  logger.info("Processed Panchayat %s " % panchayatName)
  csvfilename=eachPanchayat.slug+"_"+finyear+"_pdt.csv"
  savePanchayatReport(logger,eachPanchayat,finyear,reportType,csvfilename,outcsv)
#  with open("/tmp/%s_%s.csv" % (eachPanchayat.slug,finyear),"w") as f:
#    f.write(outcsv)

def validateFTO(block,myhtml):
  error=None
  myTable=None
  summaryTable=None
  jobcardPrefix=block.district.state.stateShortCode+"-"
  if (jobcardPrefix in str(myhtml)):
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if"FTO_Acc_signed_dt_p2w"  in str(table):
        summaryTable=table
      elif "Reference No" in str(table):
        myTable=table
    if myTable is None:
      error="FTO Details Table Not Found"
    if summaryTable is None:
      error="Summary Table not found"
  else:
    error="Jobcard Prefix not found"
  return error,myTable,summaryTable

def getFTO(logger,fullfinyear,stateCode,ftoNo,districtName):
  httplib2.debuglevel = 1
  h = httplib2.Http('.cache')
  url = "http://164.100.129.6/netnrega/fto/fto_status_dtl.aspx?fto_no=%s&fin_year=%s&state_code=%s" % (ftoNo, fullfinyear, stateCode)
  logger.info("FTO URL %s " % url)
  logger.info("finyear: %s, stateCode: %s, ftoNo: %s, districtName: %s " % (fullfinyear,stateCode,ftoNo,districtName))
  try:
    response = urlopen(url)
    html_source = response.read()
    bs = BeautifulSoup(html_source, "html.parser")
    state = bs.find(id='__VIEWSTATE').get('value')
    validation = bs.find(id='__EVENTVALIDATION').get('value')
    data = {
      '__EVENTTARGET':'ctl00$ContentPlaceHolder1$Ddfto',
      '__EVENTARGUMENT':'',
      '__LASTFOCUS':'',
      '__VIEWSTATE': state,
      '__VIEWSTATEENCRYPTED':'',
      '__EVENTVALIDATION': validation,
      'ctl00$ContentPlaceHolder1$Ddfin': fullfinyear,
      'ctl00$ContentPlaceHolder1$Ddstate': stateCode,
      'ctl00$ContentPlaceHolder1$Txtfto': ftoNo,
      'ctl00$ContentPlaceHolder1$Ddfto': ftoNo,
    }
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
  except:
    response={'status': '404'}
    content=''

  return response,content


