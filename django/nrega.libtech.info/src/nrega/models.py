from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save,post_save
from django.utils.text import slugify
import datetime
import os
from django.utils import timezone

def getFullFinYear(shortFinYear):
  shortFinYear_1 = int(shortFinYear) -1
  fullFinYear="20%s-20%s" % (str(shortFinYear_1), str(shortFinYear))
  return fullFinYear

def get_muster_upload_path(instance, filename):
  fullfinyear=getFullFinYear(instance.finyear)
  return os.path.join(
    "nrega",instance.block.district.state.slug,instance.block.district.slug,instance.block.slug,"DATA","MUSTERS",fullfinyear,filename)
def get_panchayatreport_upload_path(instance, filename):
  return os.path.join(
    "nrega",instance.panchayat.block.district.state.slug,instance.panchayat.block.district.slug,instance.panchayat.block.slug,instance.panchayat.slug,"DATA","NICREPORTS",filename)
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
  crawlRequirement=models.CharField(max_length=4,choices=CRAWL_CHOICES,default='NONE')
  isRequired=models.BooleanField(default=False)
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
  
class PanchayatReport(models.Model):
  panchayat=models.ForeignKey('panchayat',on_delete=models.CASCADE)
  reportFile=models.FileField(null=True, blank=True,upload_to=get_panchayatreport_upload_path,max_length=512)
  reportType=models.CharField(max_length=256)
  finyear=models.CharField(max_length=2)
  updateDate=models.DateTimeField(auto_now=True)
  class Meta:
        unique_together = ('panchayat', 'reportType','finyear')  
  def __str__(self):
    return self.panchayat.name+"-"+self.reportType
    
class Panchayat(models.Model):
  CRAWL_CHOICES = (
        ('FULL', 'Full Data'),
        ('NONE', 'No Crawl'),
        ('STAT', 'Only Statistics'),
    )
  block=models.ForeignKey('block',on_delete=models.CASCADE)
  name=models.CharField(max_length=256)
  code=models.CharField(max_length=10,unique=True)
  slug=models.SlugField(blank=True) 
  crawlRequirement=models.CharField(max_length=4,choices=CRAWL_CHOICES,default='NONE')
  jobcardCrawlDate=models.DateTimeField(null=True,blank=True,default=datetime.datetime.now)
  jobcardProcessDate=models.DateTimeField(null=True,blank=True,default=datetime.datetime.now)
  musterCrawlDate=models.DateTimeField(null=True,blank=True,default=datetime.datetime.now)
  statsCrawlDate=models.DateTimeField(null=True,blank=True)
  jobcardRegisterFile=models.FileField(null=True, blank=True,upload_to=get_panchayat_upload_path,max_length=512)


  def blockName(self):
    return self.block.name
  def districtName(self):
    return self.block.district.name
  def stateName(self):
    return self.block.district.state.name
  def __str__(self):
    return self.name

class PanchayatStat(models.Model):
  panchayat=models.ForeignKey('panchayat',on_delete=models.CASCADE)
  finyear=models.CharField(max_length=2)
  nicWorkDays=models.IntegerField(blank=True,null=True)
  libtechWorkDays=models.IntegerField(blank=True,null=True)

  def __str__(self):
    return self.panchayat.name+"-"+self.finyear
  
class Applicant(models.Model):
  panchayat=models.ForeignKey('Panchayat',on_delete=models.CASCADE)
  name=models.CharField(max_length=512)
  jobcard=models.CharField(max_length=256,db_index=True)
  applicantNo=models.PositiveSmallIntegerField()
  jcNo=models.IntegerField(blank=True,null=True)
  village=models.CharField(max_length=256,blank=True,null=True)
  headOfHousehold=models.CharField(max_length=512,blank=True,null=True)
  fatherHusbandName=models.CharField(max_length=512,blank=True,null=True)
  caste=models.CharField(max_length=64,blank=True,null=True)
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
   
  class Meta:
        unique_together = ('jobcard', 'applicantNo')  
  def __str__(self):
    return self.name
  #     [srno,pname,village,jobcard,applicantNo,name,headOfHousehold,faterHusbandName,caste,gender,age] = cols[0:11]
  #     [bankCode,bankName,bankBranchCode,bankBranchName,ifscCode,micrCode,poCode,poName,poAddress,accountNo,poAccountName]=cols[12:23]
  #     [accountFrozen,uid] = cols[26:28]

class Wagelist(models.Model):
  block=models.ForeignKey('block',on_delete=models.CASCADE)
  wagelistNo=models.CharField(max_length=256)
  finyear=models.CharField(max_length=2)
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
  musterDownloadAttemptDate=models.DateTimeField(null=True,blank=True)
  downloadError=models.CharField(max_length=64,blank=True,null=True)
  musterDownloadDate=models.DateTimeField(null=True,blank=True)
  isRequired=models.BooleanField(default=False)
  class Meta:
        unique_together = ('musterNo', 'block', 'finyear')  
  def __str__(self):
    return self.musterNo

class WorkDetail(models.Model):  
  applicant=models.ForeignKey('Applicant',on_delete=models.CASCADE,null=True,blank=True)
  muster=models.ForeignKey('Muster',on_delete=models.CASCADE)
  wagelist=models.ForeignKey('Wagelist',on_delete=models.CASCADE,null=True,blank=True)
  musterIndex=models.PositiveSmallIntegerField()
  zname=models.CharField(max_length=512,null=True,blank=True)
  zjobcard=models.CharField(max_length=256,null=True,blank=True)
  zaccountNo=models.CharField(max_length=256,blank=True,null=True)
  daysWorked=models.PositiveSmallIntegerField(null=True,blank=True)
  dayWage=models.DecimalField(max_digits=10,decimal_places=4,null=True,blank=True)
  totalWage=models.DecimalField(max_digits=10,decimal_places=4,null=True,blank=True)
  musterStatus=models.CharField(max_length=64,null=True,blank=True)
  creditedDate=models.DateField(null=True,blank=True)
  class Meta:
        unique_together = ('muster', 'musterIndex')  
  def __str__(self):
    return self.muster.musterNo+" "+str(self.musterIndex)
  

def createslug(instance):
  myslug=slugify(instance.name)
  if myslug == '':
    myslug="%s-%s" % (instance.__class__.__name__ , str(instance.code))
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
#def state_post_save_receiver(sender,instance,*args,**kwargs):
#  if not instance.slug:
#    instance.slug = "some-slug"

#post_save.connect(state_post_save_receiver,sender=state)
