from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save,post_save
from django.utils.text import slugify
import datetime
import time
import os
from django.utils import timezone

def getFullFinYear(shortFinYear):
  shortFinYear_1 = int(shortFinYear) -1
  fullFinYear="20%s-20%s" % (str(shortFinYear_1), str(shortFinYear))
  return fullFinYear

def get_fpsStatus_upload_path(instance, filename):
  fpsYear=str(instance.fpsYear)
  fpsMonth=str(instance.fpsMonth)
  return os.path.join(
    "nrega",instance.fpsShop.block.district.state.slug,instance.fpsShop.block.district.slug,instance.fpsShop.block.slug,"FPS",fpsYear,fpsMonth,filename)
def get_broadcast_audio_upload_path(instance,filename):
  curTime=str(int(time.time()))
  return os.path.join(
    "callmgr","audio",instance.partner.slug,curTime+"_"+filename)

def get_fto_upload_path(instance, filename):
  fullfinyear=getFullFinYear(instance.finyear)
  return os.path.join(
    "nrega",instance.block.district.state.slug,instance.block.district.slug,instance.block.slug,"DATA","FTOs",fullfinyear,filename)
def get_wagelist_upload_path(instance, filename):
  fullfinyear=getFullFinYear(instance.finyear)
  return os.path.join(
    "nrega",instance.block.district.state.slug,instance.block.district.slug,instance.block.slug,"DATA","WAGELISTS",fullfinyear,filename)
def get_muster_upload_path(instance, filename):
  fullfinyear=getFullFinYear(instance.finyear)
  return os.path.join(
    "nrega",instance.block.district.state.slug,instance.block.district.slug,instance.block.slug,"DATA","MUSTERS",fullfinyear,filename)
def get_telanganajobcard_upload_path(instance, filename):
  return os.path.join(
    "nrega",instance.panchayat.block.district.state.slug,instance.panchayat.block.district.slug,instance.panchayat.block.slug,instance.panchayat.slug,"DATA","JOBCARDS",filename)
def get_blockreport_upload_path(instance, filename):
  return os.path.join(
    "nrega",instance.panchayat.block.district.state.slug,instance.panchayat.block.district.slug,instance.panchayat.block.slug,"DATA","NICREPORTS",filename)
def get_panchayatreport_upload_path(instance, filename):
  return os.path.join(
    "nrega",instance.panchayat.block.district.state.slug,instance.panchayat.block.district.slug,instance.panchayat.block.slug,instance.panchayat.slug,"DATA","NICREPORTS",filename)
def get_sssreport_upload_path(instance, filename):
  return os.path.join(
    "nrega",instance.village.panchayat.block.district.state.slug,instance.village.panchayat.block.district.slug,instance.village.panchayat.block.slug,instance.village.panchayat.slug,instance.village.slug,"DATA","NICREPORTS",filename)
def get_villagereport_upload_path(instance, filename):
  return os.path.join(
    "nrega",instance.village.panchayat.block.district.state.slug,instance.village.panchayat.block.district.slug,instance.village.panchayat.block.slug,instance.village.panchayat.slug,instance.village.slug,"DATA","NICREPORTS",filename)
def get_blockreport_upload_path(instance, filename):
  return os.path.join(
    "nrega",instance.block.district.state.slug,instance.block.district.slug,instance.block.slug,"DATA","NICREPORTS",filename)
def get_panchayat_upload_path(instance, filename):
  return os.path.join(
    "nrega",instance.block.district.state.slug,instance.block.district.slug,instance.block.slug,instance.slug,filename)


# Create your models here.
class State(models.Model):
  name=models.CharField(max_length=256)
  crawlIP=models.CharField(max_length=256)
  code=models.CharField(max_length=2,unique=True)
  stateShortCode=models.CharField(max_length=2)
  isNIC=models.BooleanField(default=True)
  slug=models.SlugField(blank=True) 

  def __str__(self):
    return self.name

class District(models.Model):
  state=models.ForeignKey('state',on_delete=models.CASCADE)
  name=models.CharField(max_length=256)
  code=models.CharField(max_length=4,unique=True)
  tcode=models.CharField(max_length=8,blank=True,null=True)
  fpsCode=models.CharField(max_length=4,unique=True,blank=True,null=True)
  slug=models.SlugField(blank=True) 
  def stateName(self):
    return self.state.name
  def __str__(self):
    return self.name

class Block(models.Model):
  CRAWL_CHOICES = (
        ('FULL', 'Full Data'),
        ('NONE', 'No Crawl'),
        ('STAT', 'Only Statistics'),
    )
  partners=models.ManyToManyField(settings.AUTH_USER_MODEL,related_name="ngoPartners",blank=True)
  district=models.ForeignKey('district',on_delete=models.CASCADE)
  name=models.CharField(max_length=256)
  code=models.CharField(max_length=7,unique=True)
  tcode=models.CharField(max_length=7,unique=True,null=True,blank=True)
  fpsCode=models.CharField(max_length=8,unique=True,blank=True,null=True)
  crawlRequirement=models.CharField(max_length=4,choices=CRAWL_CHOICES,default='NONE')
  isRequired=models.BooleanField(default=False)
  fpsRequired=models.BooleanField(default=False)
  slug=models.SlugField(blank=True) 

  def districtName(self):
    return self.district.name
  def stateName(self):
    return self.district.state.name

  def __str__(self):
    return self.name

class nicBlockReport(models.Model):
  block=models.ForeignKey('block',on_delete=models.CASCADE)
  reportFile=models.FileField(null=True, blank=True,upload_to=get_blockreport_upload_path,max_length=512)
  reportType=models.CharField(max_length=256)
  finyear=models.CharField(max_length=2)
  class Meta:
        unique_together = ('block', 'reportType','finyear')  
  def __str__(self):
    return self.reportType+self.finyear
 
class BlockReport(models.Model):
  block=models.ForeignKey('block',on_delete=models.CASCADE)
  reportFile=models.FileField(null=True, blank=True,upload_to=get_blockreport_upload_path,max_length=512)
  reportType=models.CharField(max_length=256)
  finyear=models.CharField(max_length=2)
  updateDate=models.DateTimeField(auto_now=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  isProcessed=models.BooleanField(default=False)
  class Meta:
        unique_together = ('block', 'reportType','finyear')  
  def __str__(self):
    return self.block.name+"-"+self.reportType
 
 
class PanchayatReport(models.Model):
  panchayat=models.ForeignKey('panchayat',on_delete=models.CASCADE)
  reportFile=models.FileField(null=True, blank=True,upload_to=get_panchayatreport_upload_path,max_length=512)
  reportType=models.CharField(max_length=256)
  finyear=models.CharField(max_length=2)
  updateDate=models.DateTimeField(auto_now=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  isProcessed=models.BooleanField(default=False)
  class Meta:
        unique_together = ('panchayat', 'reportType','finyear')  
  def __str__(self):
    return self.panchayat.name+"-"+self.reportType
 
class FPSShop(models.Model):
  block=models.ForeignKey('block',on_delete=models.CASCADE)
  name=models.CharField(max_length=256)
  remarks=models.CharField(max_length=256,blank=True,null=True)
  fpsCode=models.CharField(max_length=12,unique=True)
  slug=models.SlugField(blank=True) 
 
  def __str__(self):
    return self.name

class FPSVillage(models.Model):
  fpsShop=models.ForeignKey('FPSShop',on_delete=models.CASCADE)
  name=models.CharField(max_length=256)
  libtechTag=models.ManyToManyField('LibtechTag',related_name="FPSVillageTag",blank=True)
  slug=models.SlugField(blank=True) 
  villageCode=models.CharField(max_length=10)
  
  def __str__(self):
    return self.villageCode+"-"+self.name

class VillageFPSStatus(models.Model):
  fpsVillage=models.ForeignKey('FPSVillage')
  fpsStatus=models.ForeignKey('FPSStatus')

  def __str__(self):
    return "%s" % (self.fpsVillage)
  def getAAYDeliveryDate(self):
    return self.fpsStatus.AAYDeliveryDate
  def getPHHDeliveryDate(self):
    return self.fpsStatus.PHHDeliveryDate
  def getFPSMonth(self):
    return self.fpsStatus.fpsMonth
  def getFPSYear(self):
    return self.fpsStatus.fpsYear
  def getFPSBlock(self):
    return self.fpsStatus.fpsShop.block.name
  def getVillageType(self):
    typeArray=self.fpsVillage.libtechTag.all()
    if len(typeArray) != 0:
      return typeArray[len(typeArray) -1 ]
    else:
      return ""

class FPSStatus(models.Model):
  fpsShop=models.ForeignKey('FPSShop',on_delete=models.CASCADE)
  fpsMonth=models.PositiveSmallIntegerField(null=True,blank=True)
  fpsYear=models.PositiveSmallIntegerField(null=True,blank=True)
  statusFile=models.FileField(null=True, blank=True,upload_to=get_fpsStatus_upload_path,max_length=512)
  downloadAttemptDate=models.DateTimeField(null=True,blank=True)
  AAYDeliveryDate=models.DateField(null=True,blank=True)
  PHHDeliveryDate=models.DateField(null=True,blank=True)
  isDownloaded=models.BooleanField(default=False)
  isProcessed=models.BooleanField(default=False)
  isComplete=models.BooleanField(default=False)
  def __str__(self):
    return self.fpsShop.name+"-"+str(self.fpsMonth)+"-"+str(self.fpsYear)
  

class Panchayat(models.Model):
  CRAWL_CHOICES = (
        ('FULL', 'Full Data'),
        ('NONE', 'No Crawl'),
        ('STAT', 'Only Statistics'),
        ('ONET', 'One Time '),
    )
  STAT_CHOICES = (
        ('0', 'No Data'),
        ('1', 'JRCrawled'),
        ('2', 'JRProcessed'),
        ('3', 'JRMusterCrawled'),
        ('4', 'JRMusterStatCrawled'),
    )
  block=models.ForeignKey('block',on_delete=models.CASCADE)
  name=models.CharField(max_length=256)
  remarks=models.CharField(max_length=256,blank=True,null=True)
  code=models.CharField(max_length=10,unique=True)
  tcode=models.CharField(max_length=10,blank=True,null=True)
  slug=models.SlugField(blank=True) 
  libtechTag=models.ManyToManyField('LibtechTag',related_name="panchayatTag",blank=True)
  crawlRequirement=models.CharField(max_length=4,choices=CRAWL_CHOICES,default='NONE')
  status=models.CharField(max_length=4,choices=STAT_CHOICES,default='0')
  lastCrawlDate=models.DateTimeField(null=True,blank=True)
  lastCrawlDuration=models.IntegerField(blank=True,null=True)  #This is Duration that last Crawl took in Minutes
  accuracyIndex=models.IntegerField(blank=True,null=True)  #This is Accuracy Index of Last Financial Year
  accuracyIndexAverage=models.IntegerField(blank=True,null=True)
  jobcardCrawlDate=models.DateTimeField(null=True,blank=True,default=datetime.datetime.now)
  jobcardProcessDate=models.DateTimeField(null=True,blank=True,default=datetime.datetime.now)
  applicationRegisterCrawlDate=models.DateTimeField(null=True,blank=True)
  applicationRegisterProcessDate=models.DateTimeField(null=True,blank=True)
  musterCrawlDate=models.DateTimeField(null=True,blank=True,default=datetime.datetime.now)
  statsCrawlDate=models.DateTimeField(null=True,blank=True)
  statsProcessDate=models.DateTimeField(null=True,blank=True)
  jobcardRegisterFile=models.FileField(null=True, blank=True,upload_to=get_panchayat_upload_path,max_length=512)
  isDataAccurate=models.BooleanField(default=False)


  def __str__(self):
    return "%s-%s-%s-%s" % (self.block.district.state.name,self.block.district.name,self.block.name,self.name)

class PanchayatCrawlQueue(models.Model):
  CRAWL_STAGES = (
        ('0', 'No Data'),
        ('1', 'STATSDownloaded'),
        ('2', 'JobcardRegisterCrawledProcessed'),
        ('3', 'MustersDownloadedProcessed'),
        ('4', 'WagelistDownloadedProcessed'),
        ('5', 'FTODownloadedProcessed'),
        ('6', 'StatsComputed'),
        ('7', 'ReportsGenerated'),
    )
 
  panchayat=models.ForeignKey('panchayat',on_delete=models.CASCADE)
  priority=models.PositiveSmallIntegerField(default=0)
  startFinYear=models.CharField(max_length=2,default='16')
  progress=models.PositiveSmallIntegerField(default=0)
  downloadAttemptCount=models.PositiveSmallIntegerField(default=0)
  crawlStartDate=models.DateTimeField(null=True,blank=True)
  crawlAttemptDate=models.DateTimeField(null=True,blank=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  isComplete=models.BooleanField(default=False)
  isError=models.BooleanField(default=False)
  status=models.CharField(max_length=4,choices=CRAWL_STAGES,default='0')
  error=models.CharField(max_length=1024,blank=True,null=True)
  def __str__(self):
    return "%s-%s-%s-%s" % (self.panchayat.block.district.state.name,self.panchayat.block.district.name,self.panchayat.block.name,self.panchayat.name)
   
   
class LibtechTag(models.Model):
  name=models.CharField(max_length=256,default='NONE')
  slug=models.SlugField(blank=True) 
 
  def __str__(self):
    return self.name

class Village(models.Model):
  panchayat=models.ForeignKey('Panchayat',on_delete=models.CASCADE,null=True,blank=True)
  slug=models.SlugField(blank=True) 
  name=models.CharField(max_length=256,null=True,blank=True)
  tcode=models.CharField(max_length=12,null=True,blank=True)
  code=models.CharField(max_length=12,null=True,blank=True)  #Field only for compatibility with otherlocations not used for TElangana

  def __str__(self):
    return self.name

class VillageReport(models.Model):
  village=models.ForeignKey('Village',on_delete=models.CASCADE)
  reportFile=models.FileField(null=True, blank=True,upload_to=get_villagereport_upload_path,max_length=512)
  reportType=models.CharField(max_length=256)
  finyear=models.CharField(max_length=2)
  updateDate=models.DateTimeField(auto_now=True)
  class Meta:
        unique_together = ('village', 'reportType','finyear')  
  def __str__(self):
    return self.village.name+"-"+self.reportType

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

  def __str__(self):
    return self.panchayat.name+"-"+self.panchayat.block.name

class TelanganaSSSGroup(models.Model):
  village=models.ForeignKey('Village',on_delete=models.CASCADE)
  groupName=models.CharField(max_length=512,null=True,blank=True)
  groupCode=models.CharField(max_length=16,null=True,blank=True)
  groupReport=models.FileField(null=True, blank=True,upload_to=get_sssreport_upload_path,max_length=512)
  def __str__(self):
    return self.groupName

class Jobcard(models.Model):
  panchayat=models.ForeignKey('Panchayat',db_index=True,on_delete=models.CASCADE,blank=True,null=True)
  village=models.ForeignKey('Village',blank=True,null=True)
  libtechTag=models.ManyToManyField('LibtechTag',related_name="jobcardTag",blank=True)
  group=models.ForeignKey('TelanganaSSSGroup',on_delete=models.CASCADE,blank=True,null=True)
  tjobcard=models.CharField(max_length=18,null=True,blank=True,db_index=True)
  jobcard=models.CharField(max_length=256,db_index=True,null=True,blank=True)
  jcNo=models.BigIntegerField(blank=True,null=True)
  headOfHousehold=models.CharField(max_length=512,blank=True,null=True)
  surname=models.CharField(max_length=512,blank=True,null=True)
  caste=models.CharField(max_length=64,blank=True,null=True)
  issueDate=models.DateField(null=True,blank=True,auto_now_add=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  jobcardFile=models.FileField(null=True, blank=True,upload_to=get_telanganajobcard_upload_path,max_length=512)
  isRequired=models.BooleanField(default=False)
  isDownloaded=models.BooleanField(default=False)
  isProcessed=models.BooleanField(default=False)
  isBaselineSurvey=models.BooleanField(default=False)
  isBaselineReplacement=models.BooleanField(default=False)
  allApplicantFound=models.BooleanField(default=False)
  downloadAttemptDate=models.DateTimeField(null=True,blank=True)
  downloadDate=models.DateTimeField(null=True,blank=True)
  downloadAttemptCount=models.PositiveSmallIntegerField(default=0)
  downloadCount=models.PositiveSmallIntegerField(default=0)
  downloadError=models.CharField(max_length=64,blank=True,null=True)
  def __str__(self):
    return self.jobcard

class SurveyJobcard(models.Model):
  jobcard=models.ForeignKey('Jobcard',on_delete=models.CASCADE,blank=True,null=True)
  isBaselineSurvey=models.BooleanField(default=False)
  isBaselineReplacement=models.BooleanField(default=False)
  isMainSurveyDone=models.BooleanField(default=False)
  mainSurveyIndex=models.PositiveSmallIntegerField(null=True,blank=True)
  mainTimeStamp=models.DateTimeField(null=True,blank=True)
  isQ5SurveyDone=models.BooleanField(default=False)
  q5SurveyIndex=models.PositiveSmallIntegerField(null=True,blank=True)
  q5TimeStamp=models.DateTimeField(null=True,blank=True)
  def __str__(self):
    return self.jobcard.jobcard

class Worker(models.Model):
  name=models.CharField(max_length=512)
  jobcard=models.ForeignKey('Jobcard',db_index=True,on_delete=models.CASCADE,blank=True,null=True)
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
   
  class Meta:
        unique_together = ('jobcard', 'name')  
  def __str__(self):
    return self.name+"-"+str(self.id)

 
class Stat(models.Model):
  STAT_OPTIONS = (
        ('TWD', 'TotalWorkDays'),
        ('TWA', 'TotalWageAmount'),
    )
  panchayat=models.ForeignKey('panchayat',on_delete=models.CASCADE,blank=True,null=True)
  jobcard=models.ForeignKey('Jobcard',on_delete=models.CASCADE,blank=True,null=True)
  statType=models.CharField(max_length=4,choices=STAT_OPTIONS,null=True,blank=True)
  finyear=models.CharField(max_length=2)
  value=models.DecimalField(max_digits=20,decimal_places=4,null=True,blank=True)
 
class Applicant(models.Model):
  panchayat=models.ForeignKey('Panchayat',on_delete=models.CASCADE)
  name=models.CharField(max_length=512)
  jobcard=models.ForeignKey('Jobcard',on_delete=models.CASCADE,blank=True,null=True)
  jobcard1=models.CharField(max_length=256,db_index=True)
  applicantNo=models.PositiveSmallIntegerField()
  jcNo=models.BigIntegerField(blank=True,null=True)
  village=models.CharField(max_length=256,blank=True,null=True)
  headOfHousehold=models.CharField(max_length=512,blank=True,null=True)
  fatherHusbandName=models.CharField(max_length=512,blank=True,null=True)
  caste=models.CharField(max_length=64,blank=True,null=True)
  relationship=models.CharField(max_length=64,blank=True,null=True)
  gender=models.CharField(max_length=256,blank=True,null=True)
  age=models.PositiveIntegerField(blank=True,null=True)
  accountNo=models.CharField(max_length=256,blank=True,null=True)
  bankCode=models.CharField(max_length=32,blank=True,null=True)
  bankName=models.CharField(max_length=256,blank=True,null=True)
  bankBranchCode=models.CharField(max_length=256,blank=True,null=True)
  bankBranchName=models.CharField(max_length=512,blank=True,null=True)
  ifscCode=models.CharField(max_length=32,blank=True,null=True)
  micrCode=models.CharField(max_length=32,blank=True,null=True)
  poCode=models.CharField(max_length=64,blank=True,null=True)
  poName=models.CharField(max_length=256,blank=True,null=True)
  poAddress=models.CharField(max_length=512,blank=True,null=True)
  poAccountName=models.CharField(max_length=512,blank=True,null=True)
  accountFrozen=models.CharField(max_length=4,blank=True,null=True)
  uid=models.CharField(max_length=128,blank=True,null=True)
  source=models.CharField(max_length=8,blank=True,null=True,default='nic')
   
  class Meta:
        unique_together = ('jobcard', 'applicantNo')  
  def __str__(self):
    return self.name
  #     [srno,pname,village,jobcard,applicantNo,name,headOfHousehold,faterHusbandName,caste,gender,age] = cols[0:11]
  #     [bankCode,bankName,bankBranchCode,bankBranchName,ifscCode,micrCode,poCode,poName,poAddress,accountNo,poAccountName]=cols[12:23]
  #     [accountFrozen,uid] = cols[26:28]

class FTO(models.Model):
  block=models.ForeignKey('block',on_delete=models.CASCADE)
  ftoNo=models.CharField(max_length=256)
  finyear=models.CharField(max_length=2)
  ftofinyear=models.CharField(max_length=2,blank=True,null=True)
  ftoFile=models.FileField(null=True, blank=True,upload_to=get_fto_upload_path,max_length=512)
  isDownloaded=models.BooleanField(default=False)
  isProcessed=models.BooleanField(default=False)
  isComplete=models.BooleanField(default=False)
  allApplicantFound=models.BooleanField(default=False)
  allWDFound=models.BooleanField(default=False)
  downloadAttemptDate=models.DateTimeField(null=True,blank=True)
  downloadError=models.CharField(max_length=64,blank=True,null=True)
  remarks=models.CharField(max_length=4096,blank=True,null=True)
  class Meta:
        unique_together = ('ftoNo', 'block', 'finyear')  
  def __str__(self):
    return self.ftoNo

class Wagelist(models.Model):
  block=models.ForeignKey('block',on_delete=models.CASCADE)
  wagelistNo=models.CharField(max_length=256)
  finyear=models.CharField(max_length=2)
  wagelistFile=models.FileField(null=True, blank=True,upload_to=get_wagelist_upload_path,max_length=512)
  isDownloaded=models.BooleanField(default=False)
  isProcessed=models.BooleanField(default=False)
  isComplete=models.BooleanField(default=False)
  downloadAttemptDate=models.DateTimeField(null=True,blank=True)
  downloadError=models.CharField(max_length=64,blank=True,null=True)
  class Meta:
        unique_together = ('wagelistNo', 'block', 'finyear')  
  def __str__(self):
    return self.wagelistNo
    
class Muster(models.Model):
  panchayat=models.ForeignKey('Panchayat',on_delete=models.CASCADE,blank=True,null=True)
  block=models.ForeignKey('block',on_delete=models.CASCADE)
  musterNo=models.CharField(max_length=64)
  finyear=models.CharField(max_length=2)
  musterType=models.CharField(max_length=4)
  workCode=models.CharField(max_length=128)
  workName=models.CharField(max_length=2046)
  dateFrom=models.DateField(default=datetime.date.today)
  dateTo=models.DateField(default=datetime.date.today)
  paymentDate=models.DateField(blank=True,null=True)
  musterURL=models.CharField(max_length=1024)
  musterFile=models.FileField(null=True, blank=True,upload_to=get_muster_upload_path,max_length=512)
  isDownloaded=models.BooleanField(default=False)
  isProcessed=models.BooleanField(default=False)
  isComplete=models.BooleanField(default=False)
  isDownloadError=models.BooleanField(default=False)
  allApplicantFound=models.BooleanField(default=False)
  allWorkerFound=models.BooleanField(default=False)
  isPanchayatNull=models.BooleanField(default=False)
  musterDownloadAttemptDate=models.DateTimeField(null=True,blank=True)
  downloadAttemptCount=models.PositiveSmallIntegerField(default=0)
  downloadCount=models.PositiveSmallIntegerField(default=0)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  downloadError=models.CharField(max_length=64,blank=True,null=True)
  musterDownloadDate=models.DateTimeField(null=True,blank=True)
  isRequired=models.BooleanField(default=False)
  class Meta:
        unique_together = ('musterNo', 'block', 'finyear')  
  def __str__(self):
    return self.musterNo

class WorkDetail(models.Model):  
  applicant=models.ForeignKey('Applicant',on_delete=models.CASCADE,null=True,blank=True)  #OutDaed please do not use this field
  worker=models.ForeignKey('Worker',on_delete=models.CASCADE,db_index=True,null=True,blank=True)
  muster=models.ForeignKey('Muster',on_delete=models.CASCADE)
#  wagelist=models.ForeignKey('Wagelist',on_delete=models.CASCADE,null=True,blank=True)
  wagelist=models.ManyToManyField('Wagelist',related_name="wdWagelist",blank=True)
  musterIndex=models.PositiveSmallIntegerField()
  zname=models.CharField(max_length=512,null=True,blank=True)
  zjobcard=models.CharField(max_length=256,null=True,blank=True)
  zvilCode=models.CharField(max_length=32,null=True,blank=True)
  zjcNo=models.BigIntegerField(blank=True,null=True)
  zaccountNo=models.CharField(max_length=256,blank=True,null=True)
  daysWorked=models.PositiveSmallIntegerField(null=True,blank=True)
  dayWage=models.DecimalField(max_digits=10,decimal_places=4,null=True,blank=True)
  totalWage=models.DecimalField(max_digits=10,decimal_places=4,null=True,blank=True)
  musterStatus=models.CharField(max_length=64,null=True,blank=True)
  creditedDate=models.DateField(null=True,blank=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  class Meta:
        unique_together = ('muster', 'musterIndex')  
  def __str__(self):
    return self.muster.musterNo+" "+str(self.musterIndex)
  
class PaymentDetail(models.Model):
  applicant=models.ForeignKey('Applicant',on_delete=models.CASCADE,null=True,blank=True) #OutDated please do no use this field
  worker=models.ForeignKey('Worker',on_delete=models.CASCADE,db_index=True,null=True,blank=True)
  workDetail=models.ForeignKey('WorkDetail',on_delete=models.CASCADE,null=True,blank=True)
  fto=models.ForeignKey('FTO',on_delete=models.CASCADE,null=True,blank=True)
  payorderNo=models.CharField(max_length=256,null=True,blank=True)
  epayorderNo=models.CharField(max_length=256,null=True,blank=True)
  referenceNo=models.CharField(max_length=256,null=True,blank=True)
  transactionDate=models.DateField(null=True,blank=True)
  processDate=models.DateField(null=True,blank=True)
  status=models.CharField(max_length=256,null=True,blank=True)
  rejectionReason=models.CharField(max_length=256,null=True,blank=True)
  creditedAmount=models.DecimalField(max_digits=10,decimal_places=4,null=True,blank=True)
  daysWorked=models.DecimalField(null=True,blank=True,max_digits=21,decimal_places=2)
  disbursedAmount=models.DecimalField(max_digits=10,decimal_places=4,null=True,blank=True)
  disbursedDate=models.DateField(null=True,blank=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  class Meta:
        unique_together = ('fto', 'referenceNo')  
  def __str__(self):
    return self.referenceNo

class PendingPostalPayment(models.Model):
  jobcard=models.ForeignKey('Jobcard',db_index=True,on_delete=models.CASCADE,blank=True,null=True)
  name=models.CharField(max_length=512)
  balance=models.DecimalField(max_digits=10,decimal_places=4)  # Pending Amount
  worker=models.ForeignKey('Worker',null=True,blank=True)
  statusDate=models.DateField(null=True,blank=True) #Date on which the money was pending
  lastTransactionDate=models.DateField(null=True,blank=True) #Last Transaction as Per Postal Data
  libtechTag=models.ForeignKey('LibtechTag',null=True,blank=True)
  tableName=models.CharField(max_length=256,null=True,blank=True)
  
  class Meta:
        unique_together = ('jobcard','name','lastTransactionDate','balance')  
  def __str__(self):
    return self.jobcard.tjobcard+"-"+str(self.balance)

##Modesl for Broadcast
class Partner(models.Model):
  name=models.CharField(max_length=512)
  slug=models.SlugField(blank=True)
 
  def __str__(self):
    return self.name 
  
class Phonebook(models.Model):
  phone=models.CharField(max_length=10,unique=True)
  partner=models.ForeignKey('Partner',on_delete=models.CASCADE)
  panchayat=models.ForeignKey('Panchayat',null=True,blank=True)
  worker=models.ForeignKey('Worker',null=True,blank=True)
  fpsVillage=models.ForeignKey('FPSVillage',null=True,blank=True)
  def _str__(self):
    return self.phone
   
class Broadcast(models.Model):
  BROADCAST_TYPE_CHOICES = (
        ('GRUP', 'Group'),
        ('LBLK', 'Block'),
        ('LPAN', 'Panchayat'),
        ('BFPS', 'BiharFPS'),
    )
  name=models.CharField(max_length=256)
  slug=models.SlugField(blank=True) 
  partner=models.ForeignKey('Partner')
  broadcastType=models.CharField(max_length=4,choices=BROADCAST_TYPE_CHOICES,default='NONE')
  fpsVillage=models.ForeignKey('FPSVillage',null=True,blank=True)
  minhour=models.PositiveSmallIntegerField(default='8')
  maxhour=models.PositiveSmallIntegerField(default='20')
  startDate=models.DateTimeField()
  endDate=models.DateTimeField()
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  modified=models.DateTimeField(null=True,blank=True,auto_now=True)
  oldbid=models.IntegerField(blank=True,null=True)
  
  def __str__(self):
    return self.name

class AudioLibrary(models.Model):
  partner=models.ForeignKey('Partner')
  audioFile=models.FileField(null=True, blank=True,upload_to=get_broadcast_audio_upload_path,max_length=512)
 
   
def createslug(instance):
  myslug=slugify(instance.name)[:50]
  if myslug == '':
    if hasattr(instance, 'code'):
      myslug="%s-%s" % (instance.__class__.__name__ , str(instance.code))
    else:
      myslug="%s-%s" % (instance.__class__.__name__ , str(instance.id))
  return myslug


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
post_save.connect(location_post_save_receiver,sender=FPSShop)
post_save.connect(location_post_save_receiver,sender=FPSVillage)
post_save.connect(location_post_save_receiver,sender=Village)
post_save.connect(location_post_save_receiver,sender=LibtechTag)
post_save.connect(location_post_save_receiver,sender=Partner)
post_save.connect(location_post_save_receiver,sender=Broadcast)
#def state_post_save_receiver(sender,instance,*args,**kwargs):
#  if not instance.slug:
#    instance.slug = "some-slug"

#post_save.connect(state_post_save_receiver,sender=state)
