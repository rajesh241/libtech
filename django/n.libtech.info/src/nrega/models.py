from django.db import models
from django.db.models.signals import pre_save,post_save
from django.utils.text import slugify
import time
import datetime
import os
#File Uploads

def getFullFinYear(shortFinYear):
  shortFinYear_1 = int(shortFinYear) -1
  fullFinYear="20%s-20%s" % (str(shortFinYear_1), str(shortFinYear))
  return fullFinYear
def get_report_upload_path(instance, filename):
  if instance.panchayat is not None:
    return os.path.join("nrega",instance.panchayat.block.district.state.slug,instance.panchayat.block.district.slug,instance.panchayat.block.slug,instance.panchayat.slug,"DATA","NICREPORTS",filename)
  elif instance.block is not None:
    return os.path.join( "nrega",instance.block.district.state.slug,instance.block.district.slug,instance.block.slug,"DATA","NICREPORTS",filename)
  else:
    return os.path.join( "misc",filename)


def get_genericreport_upload_path(instance,filename):
  return os.path.join("genericReport",filename)


def get_jobcard_upload_path(instance, filename):
  return os.path.join(
    "nrega",instance.panchayat.block.district.state.slug,instance.panchayat.block.district.slug,instance.panchayat.block.slug,instance.panchayat.slug,"DATA","JOBCARDS",filename)


def get_blockfile_upload_path(instance, filename):
  fullfinyear=getFullFinYear(instance.finyear)
  modelType=instance.__class__.__name__
  return os.path.join(
    "nrega",instance.block.district.state.slug,instance.block.district.slug,instance.block.slug,"DATA",modelType,fullfinyear,filename)

class LibtechTag(models.Model):
  '''
  This Model is for generic Tags, we can define Tags, for example Survey2019 and tag any object, panchayat, jobcard etc with the tag. Then the objects can be retrieved by using the tag
  '''
  name=models.CharField(max_length=256,default='NONE')
  slug=models.SlugField(blank=True) 
  class Meta:
    db_table = 'libtechTag'
  def __str__(self):
    return self.name

class State(models.Model):
  '''
  This is Model for the States. States are identified with unique code, which is based on code on Nrega Website. Additionally each NIC Nrega state has a different server, which is identified with crawlIP. 
  isNIC field is true for State nrega websites which are hosted on NREGA
  '''
  name=models.CharField(max_length=256)
  code=models.CharField(max_length=2,unique=True)
  slug=models.SlugField(blank=True) 
  crawlIP=models.CharField(max_length=256,null=True,blank=True)
  stateShortCode=models.CharField(max_length=2)
  isNIC=models.BooleanField(default=True)
  class Meta:
    db_table = 'state'
  def __str__(self):
    return self.name

class District(models.Model):
  state=models.ForeignKey('state',on_delete=models.CASCADE)
  name=models.CharField(max_length=256)
  code=models.CharField(max_length=4,unique=True)
  slug=models.SlugField(blank=True) 
  tcode=models.CharField(max_length=8,blank=True,null=True)
  isEnumerated=models.BooleanField(default=False)
  class Meta:
    db_table = 'district'
  def __str__(self):
    return self.name

class Block(models.Model):
  district=models.ForeignKey('district',on_delete=models.CASCADE)
  name=models.CharField(max_length=256)
  code=models.CharField(max_length=7,unique=True)
  slug=models.SlugField(blank=True) 
  tcode=models.CharField(max_length=7,unique=True,null=True,blank=True)
  class Meta:
    db_table = 'block'
  def __str__(self):
    return self.name

class Panchayat(models.Model):
  block=models.ForeignKey('block',on_delete=models.CASCADE)
  name=models.CharField(max_length=256)
  code=models.CharField(max_length=10,unique=True)
  slug=models.SlugField(blank=True) 
  tcode=models.CharField(max_length=10,blank=True,null=True)
  libtechTag=models.ManyToManyField('LibtechTag',related_name="panchayatTag",blank=True)
  remarks=models.CharField(max_length=256,blank=True,null=True)
  lastCrawlDate=models.DateTimeField(null=True,blank=True)
  lastCrawlDuration=models.IntegerField(blank=True,null=True)  #This is Duration that last Crawl took in Minutes
  accuracyIndex=models.IntegerField(blank=True,null=True)  #This is Accuracy Index of Last Financial Year
  accuracyIndexAverage=models.IntegerField(blank=True,null=True)
  isDataAccurate=models.BooleanField(default=False)
  class Meta:
    db_table = 'panchayat'
  def __str__(self):
    return "%s-%s-%s-%s" % (self.block.district.state.name,self.block.district.name,self.block.name,self.name)

class Village(models.Model):
  panchayat=models.ForeignKey('Panchayat',on_delete=models.CASCADE,null=True,blank=True)
  name=models.CharField(max_length=256,null=True,blank=True)
  code=models.CharField(max_length=12,null=True,blank=True)  #Field only for compatibility with otherlocations not used for TElangana
  slug=models.SlugField(blank=True) 
  tcode=models.CharField(max_length=12,null=True,blank=True)
  class Meta:
    db_table = 'village'

  def __str__(self):
    return self.name


#Models for Reports
#The below Model is used to uploading generic reports like on the fly zip of existing reports etc etc
class GenericReport(models.Model):
  panchayat=models.ForeignKey('Panchayat',on_delete=models.CASCADE,null=True,blank=True)
  libtechTag=models.ForeignKey('LibtechTag',on_delete=models.CASCADE,null=True,blank=True)
  reportFile=models.FileField(null=True, blank=True,upload_to=get_genericreport_upload_path,max_length=512)
  updateDate=models.DateTimeField(auto_now=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  class Meta:
    db_table = 'genericReport'
  def __str__(self):
    if (self.panchayat is not None) and (self.libtechTag is not None):
      return "%s-%s" % (self.panchayat.name,self.libtechTag.name)
    else:
      return str(self.id)
  def filename(self):
    return os.path.basename(self.reportFile.name)
#The below Model is used to store block and panchayat level reports
class Report(models.Model):
  block=models.ForeignKey('Block',on_delete=models.CASCADE,null=True,blank=True)
  panchayat=models.ForeignKey('Panchayat',on_delete=models.CASCADE,null=True,blank=True)
  reportFile=models.FileField(null=True, blank=True,upload_to=get_report_upload_path,max_length=512)
  reportType=models.CharField(max_length=256)
  finyear=models.CharField(max_length=2)
  created=models.DateTimeField(auto_now_add=True)
  modified=models.DateTimeField(auto_now=True)
  class Meta:
    unique_together = ('block', 'panchayat','reportType','finyear')  
    db_table = 'report'
  def __str__(self):
    if self.block is not None:
      return self.block.name+"-"+self.reportType
    elif self.panchayat is not None:
      return self.panchayat.name+"-"+self.reportType
    else:
      return reportType

class CrawlState(models.Model):
  CRAWL_TYPE_OPTIONS = (
        ('NIC', 'NIC'),
        ('AP', 'AP'),
        ('TELANGANA','TELANGANA')
        )
  name=models.CharField(max_length=256)
  sequence=models.PositiveSmallIntegerField(default=0)
  crawlType=models.CharField(max_length=32,choices=CRAWL_TYPE_OPTIONS,default='NIC')
  needsQueueManager=models.BooleanField(default=False)
  isActive=models.BooleanField(default=False)
  nicHourRestriction=models.BooleanField(default=False)
  isPanchayatLevelProcess=models.BooleanField(default=False)
  iterateFinYear=models.BooleanField(default=True)
  threshold=models.IntegerField(blank=True,null=True,default=3600)
  objLimit=models.IntegerField(blank=True,null=True,default=1000)
  class Meta:
    db_table = 'crawlState'
  def __str__(self):
    return self.crawlType+"-"+self.name
  
class CrawlQueue(models.Model):
  CRAWL_STATUS_OPTIONS = (
        ('STARTCRAWL', 'STARTCRAWL'),
        ('NICStats', 'NICStats'),
        ('JobcardRegister', 'JobcardRegister'),
        ('APJobcardDownload', 'APJobcardDownload'),
        ('APJobcardProcess', 'APJobcardProcess'),
        ('MusterCrawl', 'MusterCrawl'),
        ('MusterDownload', 'MusterDownload'),
        ('MusterProcess', 'MusterProcess'),
        ('WagelistDownload', 'WagelistDownload'),
        ('WagelistCrawl', 'WagelistCrawl'),
        ('WagelistProcess', 'WagelistProcess'),
        ('FTODownload', 'FTODownload'),
        ('FTOProcess', 'FTOProcess'),
        ('ComputeStats', 'ComputeStats'),
        ('PanchayatReport', 'PanchayatReport'),
        ('DetailPanchayatReport', 'DetailPanchayatReport'),
        ('ComputePaymentStatus', 'ComputePaymentStatus'),
        ('ComputeJobcardStat', 'ComputeJobcardStat'),
        ('APReport', 'APReport'),
        ('Complete', 'Complete'),
    )
 

  panchayat=models.ForeignKey('panchayat',on_delete=models.CASCADE,null=True,blank=True)
  block=models.ForeignKey('block',on_delete=models.CASCADE,null=True,blank=True)
  crawlState=models.ForeignKey('CrawlState',on_delete=models.CASCADE,null=True,blank=True)
  priority=models.PositiveSmallIntegerField(default=0)
  startFinYear=models.CharField(max_length=2,default='16')
  status=models.CharField(max_length=256,choices=CRAWL_STATUS_OPTIONS,default='STARTCRAWL')
  progress=models.PositiveSmallIntegerField(default=0)
  stepError=models.BooleanField(default=False)
  downloadAttemptCount=models.PositiveSmallIntegerField(default=0)
  crawlStartDate=models.DateTimeField(null=True,blank=True)
  crawlAttemptDate=models.DateTimeField(null=True,blank=True)
  pending=models.IntegerField(blank=True,null=True,default=0)
  isComplete=models.BooleanField(default=False)
  isError=models.BooleanField(default=False)
  isProcessDriven=models.BooleanField(default=False)
  error=models.CharField(max_length=4086,blank=True,null=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  class Meta:
    db_table = 'crawlQueue'
  def __str__(self):
    if self.panchayat is not  None:
      return "%s-%s-%s-%s" % (self.panchayat.block.district.state.name,self.panchayat.block.district.name,self.panchayat.block.name,self.panchayat.name)
    elif self.block is not  None:
      return "%s-%s-%s" % (self.block.district.state.name,self.block.district.name,self.block.name)
    else:
      return self.id

class WorkerStat(models.Model):
  worker=models.ForeignKey('Worker',db_index=True,on_delete=models.CASCADE,blank=True,null=True)
  finyear=models.CharField(max_length=2)
  workDays=models.IntegerField(blank=True,null=True)
  totalCredited=models.IntegerField(blank=True,null=True)
  totalPending=models.IntegerField(blank=True,null=True)
  totalRejected=models.IntegerField(blank=True,null=True)
  totalWages=models.IntegerField(blank=True,null=True)
  class Meta:
    unique_together = ( 'worker','finyear')  
    db_table = 'workerStat'
  def __str__(self):
    if self.worker.jobcard.tjobcard is not None:
      displayJobcard=self.worker.jobcard.tjobcard
    else:
      jobcard=self.worker.jobcard.jobcard
    return displayJobcard+"-"+self.worker.name+"-"+finyear
    

class JobcardStat(models.Model):
  jobcard=models.ForeignKey('Jobcard',db_index=True,on_delete=models.CASCADE,blank=True,null=True)
  finyear=models.CharField(max_length=2)
  workDays=models.IntegerField(blank=True,null=True)
  totalCredited=models.IntegerField(blank=True,null=True)
  totalPending=models.IntegerField(blank=True,null=True)
  totalRejected=models.IntegerField(blank=True,null=True)
  totalWages=models.IntegerField(blank=True,null=True)
  class Meta:
    unique_together = ( 'jobcard','finyear')  
    db_table = 'jobcardStat'
  def __str__(self):
    if self.jobcard.tjobcard is not None:
      displayJobcard=self.jobcard.tjobcard
    else:
      jobcard=self.jobcard.jobcard
    return displayJobcard+"-"+finyear
    
class PanchayatStat(models.Model):
  panchayat=models.ForeignKey('panchayat',on_delete=models.CASCADE)
  finyear=models.CharField(max_length=2)
  nicWorkDays=models.IntegerField(blank=True,null=True)
  nicJobcardsTotal=models.IntegerField(blank=True,null=True)
  nicWorkersTotal=models.IntegerField(blank=True,null=True)
  libtechWorkDays=models.IntegerField(blank=True,null=True)
  libtechWorkDaysPanchayatwise=models.IntegerField(blank=True,null=True)
  jobcardsTotal=models.IntegerField(blank=True,null=True)
  workersTotal=models.IntegerField(blank=True,null=True)
  mustersTotal=models.IntegerField(blank=True,null=True)
  mustersPendingDownload=models.IntegerField(blank=True,null=True)
  mustersPendingProcessing=models.IntegerField(blank=True,null=True)
  mustersInComplete=models.IntegerField(blank=True,null=True)
  musterMissingApplicants=models.IntegerField(blank=True,null=True)
  mustersDownloaded=models.IntegerField(blank=True,null=True)
  mustersProcessed=models.IntegerField(blank=True,null=True)
  workDaysAccuracyIndex=models.IntegerField(blank=True,null=True)
  totalTransactions=models.IntegerField(blank=True,null=True)
  totalPending=models.IntegerField(blank=True,null=True)
  totalRejected=models.IntegerField(blank=True,null=True)
  totalInvalid=models.IntegerField(blank=True,null=True)
  totalPendingPercentage=models.IntegerField(blank=True,null=True)
  totalRejectedPercentage=models.IntegerField(blank=True,null=True)
  totalInvalidPercentage=models.IntegerField(blank=True,null=True)
   
  class Meta:
    unique_together = ( 'panchayat','finyear')  
    db_table = 'panchayatStat'
  def __str__(self):
    return self.panchayat.name+"-"+self.panchayat.block.name

class Jobcard(models.Model):
  panchayat=models.ForeignKey('Panchayat',db_index=True,on_delete=models.CASCADE,blank=True,null=True)
  village=models.ForeignKey('Village',on_delete=models.CASCADE,blank=True,null=True)
  libtechTag=models.ManyToManyField('LibtechTag',related_name="jobcardTag",blank=True)
  tjobcard=models.CharField(max_length=24,null=True,blank=True,db_index=True)
  jobcard=models.CharField(max_length=256,db_index=True,null=True,blank=True)
  jcNo=models.BigIntegerField(blank=True,null=True)
  headOfHousehold=models.CharField(max_length=512,blank=True,null=True)
  surname=models.CharField(max_length=512,blank=True,null=True)
  caste=models.CharField(max_length=64,blank=True,null=True)
  issueDate=models.DateField(null=True,blank=True,auto_now_add=True)
  jobcardFile=models.FileField(null=True, blank=True,upload_to=get_jobcard_upload_path,max_length=512)
  isVillageInfoMissing=models.BooleanField(default=False)
  isWorkerTableMissing=models.BooleanField(default=False)
  isPaymentTableMissing=models.BooleanField(default=False)
  allApplicantFound=models.BooleanField(default=False)

  
  downloadManager=models.ForeignKey('DownloadManager',on_delete=models.CASCADE)


  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  class Meta:
    unique_together = ( 'jobcard','tjobcard')  
    db_table = 'jobcard'
  def __str__(self):
    return self.jobcard

class Worker(models.Model):
  jobcard=models.ForeignKey('Jobcard',db_index=True,on_delete=models.CASCADE,blank=True,null=True)
  name=models.CharField(max_length=512)
  libtechTag=models.ManyToManyField('LibtechTag',related_name="workerTag",blank=True)
  applicantNo=models.PositiveSmallIntegerField()
  fatherHusbandName=models.CharField(max_length=512,blank=True,null=True)
  relationship=models.CharField(max_length=64,blank=True,null=True)
  gender=models.CharField(max_length=256,blank=True,null=True)
  age=models.PositiveIntegerField(blank=True,null=True)
  isDeleted=models.BooleanField(default=False)
  isDisabled=models.BooleanField(default=False)
  isMinority=models.BooleanField(default=False)
  remarks=models.CharField(max_length=512,blank=True,null=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  is15Days=models.BooleanField(default=False)
  isSample30=models.BooleanField(default=False)
  isSample=models.BooleanField(default=False)
  isExtraSample30=models.BooleanField(default=False)
  isExtraSample=models.BooleanField(default=False)
   
  class Meta:
    unique_together = ('jobcard', 'name','applicantNo')  
    db_table = 'worker'
  def __str__(self):
    return self.name+"-"+str(self.id)

class DownloadManager(models.Model):
  downloadType=models.CharField(max_length=64,blank=True,null=True)
  isDownloaded=models.BooleanField(default=False)
  isProcessed=models.BooleanField(default=False)
  isError=models.BooleanField(default=False)
  downloadAttemptDate=models.DateTimeField(null=True,blank=True)
  downloadDate=models.DateTimeField(null=True,blank=True)
  downloadAttemptCount=models.PositiveSmallIntegerField(default=0)
  downloadCount=models.PositiveSmallIntegerField(default=0)
  errorDescription=models.CharField(max_length=256,blank=True,null=True)
  class Meta:
        db_table="downloadManager"
  def __str__(self):
    return str(self.id)

  
class Muster(models.Model):
  panchayat=models.ForeignKey('Panchayat',on_delete=models.CASCADE,db_index=True,blank=True,null=True)
  block=models.ForeignKey('block',on_delete=models.CASCADE)
  finyear=models.CharField(max_length=2)
  musterNo=models.CharField(max_length=64,db_index=True)
  musterType=models.CharField(max_length=4)
  workCode=models.CharField(max_length=128)
  workName=models.CharField(max_length=2046)
  dateFrom=models.DateField(default=datetime.date.today)
  dateTo=models.DateField(default=datetime.date.today)
  paymentDate=models.DateField(blank=True,null=True)
  musterURL=models.CharField(max_length=1024)
  contentFile=models.FileField(null=True, blank=True,upload_to=get_blockfile_upload_path,max_length=512)
  allApplicantFound=models.BooleanField(default=False)
  allWorkerFound=models.BooleanField(default=False)
  isComplete=models.BooleanField(default=False)

  downloadManager=models.ForeignKey('DownloadManager',on_delete=models.CASCADE)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  class Meta:
        unique_together = ('musterNo', 'block', 'finyear')  
        db_table="muster"
  def __str__(self):
    return self.musterNo

class Wagelist(models.Model):
  block=models.ForeignKey('block',on_delete=models.CASCADE,db_index=True)
  wagelistNo=models.CharField(max_length=256)
  finyear=models.CharField(max_length=2,db_index=True)
  contentFile=models.FileField(null=True, blank=True,upload_to=get_blockfile_upload_path,max_length=512)
  generateDate=models.DateField(blank=True,null=True)
  isComplete=models.BooleanField(default=False)
  
  downloadManager=models.ForeignKey('DownloadManager',on_delete=models.CASCADE)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  class Meta:
        unique_together = ('wagelistNo', 'block', 'finyear') 
        db_table="wagelist"
  def __str__(self):
    return self.wagelistNo

class FTO(models.Model):
  block=models.ForeignKey('block',on_delete=models.CASCADE,db_index=True)
  ftoNo=models.CharField(max_length=256,db_index=True)
  paymentMode=models.CharField(max_length=64,blank=True,null=True)
  finyear=models.CharField(max_length=2,db_index=True)
  firstSignatoryDate=models.DateField(null=True,blank=True)
  secondSignatoryDate=models.DateField(null=True,blank=True)
  ftofinyear=models.CharField(max_length=2,blank=True,null=True)
  contentFile=models.FileField(null=True, blank=True,upload_to=get_blockfile_upload_path,max_length=512)
  allWorkerFound=models.BooleanField(default=False)
  allWDFound=models.BooleanField(default=False)
  isComplete=models.BooleanField(default=False)

  downloadManager=models.ForeignKey('DownloadManager',on_delete=models.CASCADE)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)

  class Meta:
        unique_together = ('ftoNo', 'block', 'finyear')  
        db_table = "fto"
  def __str__(self):
    return self.ftoNo


class WorkDetail(models.Model):  
  worker=models.ForeignKey('Worker',on_delete=models.CASCADE,db_index=True,null=True,blank=True)
  muster=models.ForeignKey('Muster',on_delete=models.CASCADE,db_index=True)
  wagelist=models.ManyToManyField('Wagelist',related_name="wdWagelist",blank=True)
  paymentInfo=models.ManyToManyField('PaymentInfo',related_name="wdPaymentInfo",blank=True)
  musterIndex=models.PositiveSmallIntegerField()
  daysWorked=models.PositiveSmallIntegerField(null=True,blank=True)
  dayWage=models.DecimalField(max_digits=10,decimal_places=4,null=True,blank=True)
  totalWage=models.DecimalField(max_digits=10,decimal_places=4,null=True,blank=True)
  musterStatus=models.CharField(max_length=64,null=True,blank=True)
  status=models.CharField(max_length=64,null=True,blank=True)
  isCredited=models.BooleanField(default=False)
  creditedDate=models.DateField(null=True,blank=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  class Meta:
        unique_together = ('muster', 'musterIndex')  
        db_table="workDetail"
  def __str__(self):
    return self.muster.musterNo+" "+str(self.musterIndex)
 
class PaymentInfo(models.Model):
  workDetail=models.ForeignKey('WorkDetail',on_delete=models.CASCADE,db_index=True)
  wagelist=models.ForeignKey('Wagelist',on_delete=models.CASCADE,db_index=True)
  fto=models.ForeignKey('FTO',on_delete=models.CASCADE,null=True,blank=True)
  payorderNo=models.CharField(max_length=256,null=True,blank=True)
  referenceNo=models.CharField(max_length=256,null=True,blank=True)
  transactionDate=models.DateField(null=True,blank=True)
  processDate=models.DateField(null=True,blank=True)
  status=models.CharField(max_length=256,null=True,blank=True)
  rejectionReason=models.CharField(max_length=256,null=True,blank=True)
  creditedAmount=models.DecimalField(max_digits=10,decimal_places=4,null=True,blank=True)
  daysWorked=models.DecimalField(null=True,blank=True,max_digits=21,decimal_places=2)
  accountNo=models.CharField(max_length=256,blank=True,null=True)
  primaryAccountHolder=models.CharField(max_length=512,blank=True,null=True)
  bankCode=models.CharField(max_length=16,blank=True,null=True)
  ifscCode=models.CharField(max_length=64,blank=True,null=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  class Meta:
        unique_together = ('workDetail', 'wagelist')  
        db_table="paymentInfo"
  def __str__(self):
    return str(self.id)

class APWorkPayment(models.Model):
  jobcard=models.ForeignKey('Jobcard',db_index=True,on_delete=models.CASCADE,blank=True,null=True)
  worker=models.ForeignKey('Worker',on_delete=models.CASCADE,db_index=True,null=True,blank=True)
  name=models.CharField(max_length=512,null=True,blank=True)
  applicantNo=models.PositiveSmallIntegerField(db_index=True,null=True,blank=True)
  musterNo=models.CharField(max_length=64,db_index=True,null=True,blank=True)
  finyear=models.CharField(max_length=2,null=True,blank=True)
  workCode=models.CharField(max_length=128,null=True,blank=True)
  workName=models.CharField(max_length=2046,null=True,blank=True)
  dateTo=models.DateField(null=True,blank=True)
  daysWorked=models.PositiveSmallIntegerField(null=True,blank=True)
  accountNo=models.CharField(max_length=256,blank=True,null=True)
  modeOfPayment=models.CharField(max_length=256,blank=True,null=True)
  payorderAmount=models.DecimalField(max_digits=10,decimal_places=4,null=True,blank=True)
  payorderNo=models.CharField(max_length=256,null=True,blank=True)
  payorderDate=models.DateField(null=True,blank=True)
  epayorderNo=models.CharField(db_index=True,max_length=256,null=True,blank=True)
  epayorderDate=models.DateField(null=True,blank=True)
  payingAgencyDate=models.DateField(null=True,blank=True)
  creditedDate=models.DateField(null=True,blank=True)
  disbursedAmount=models.DecimalField(max_digits=10,decimal_places=4,null=True,blank=True)
  disbursedDate=models.DateField(null=True,blank=True)
  isDelayedPayment=models.BooleanField(default=False)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  class Meta:
        unique_together = ('jobcard', 'applicantNo','epayorderNo')  
        db_table="apWorkPayment" 
  def __str__(self):
    return self.epayorderNo

class RN6TransactionDetail(models.Model):
  worker=models.ForeignKey('Worker',on_delete=models.CASCADE,db_index=True,null=True,blank=True)
  name=models.CharField(max_length=256,null=True,blank=True)
  transactionDate=models.DateField(null=True,blank=True)
  transactionReference=models.CharField(max_length=256,null=True,blank=True)
  withdrawnAt=models.CharField(max_length=256,null=True,blank=True)
  deposit=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  withdrawal=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  balance=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  class Meta:
        unique_together = ('worker', 'transactionDate','transactionReference')  
        db_table="rn6TransactionDetail" 
  def __str__(self):
    return self.transactionReference
  
class Task(models.Model):
  crawlQueue=models.ForeignKey('CrawlQueue',on_delete=models.CASCADE,db_index=True,null=True,blank=True)
  crawlState=models.ForeignKey('CrawlState',on_delete=models.CASCADE,null=True,blank=True)
  processName=models.CharField(max_length=256,null=True,blank=True)
  libName=models.CharField(max_length=256,default='crawl')
  objID=models.IntegerField(null=True,blank=True)
  hasDownloadManager=models.BooleanField(default=False)
  finyear=models.CharField(max_length=2,blank=True,null=True)
  isComplete=models.BooleanField(default=False)
  inProgress=models.BooleanField(default=False)
  isError=models.BooleanField(default=False)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  class Meta:
        db_table="task" 
  def __str__(self):
    return "%s-%s" % (self.processName,str(self.objID))

class LibtechProcess(models.Model):
  pid=models.PositiveSmallIntegerField(default=0)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)

class LanguageDict(models.Model):
  phrase1=models.CharField(max_length=1024)
  lang1=models.CharField(max_length=1024)
  phrase2=models.CharField(max_length=1024,null=True,blank=True)
  lang2=models.CharField(max_length=1024,null=True,blank=True)
  class Meta:
        db_table="languageDict" 
  def __str__(self):
    return "%s-%s" % (self.phrase1+self.lang1)


def createslug(instance):
  myslug=slugify(instance.name)[:50]
  if myslug == '':
    if hasattr(instance, 'code'):
      myslug="%s-%s" % (instance.__class__.__name__ , str(instance.code))
    else:
      myslug="%s-%s" % (instance.__class__.__name__ , str(instance.id))
  return myslug

def crawlqueue_post_save_receiver(sender,instance,*args,**kwargs):
  myCrawlState=CrawlState.objects.filter(name="initial").first()
  if instance.crawlState is None:
    instance.crawlState=myCrawlState
    instance.save()

def location_post_save_receiver(sender,instance,*args,**kwargs):
  myslug=createslug(instance)
  if instance.slug != myslug:
    instance.slug = myslug
    instance.save()
#  print(instance.__class__.__name__)
post_save.connect(location_post_save_receiver,sender=State)
post_save.connect(location_post_save_receiver,sender=District)
post_save.connect(location_post_save_receiver,sender=Block)
post_save.connect(location_post_save_receiver,sender=Panchayat)
post_save.connect(location_post_save_receiver,sender=Village)
post_save.connect(location_post_save_receiver,sender=LibtechTag)
post_save.connect(crawlqueue_post_save_receiver,sender=CrawlQueue)

