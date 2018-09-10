class State(models.Model):
  name=models.CharField(max_length=256)
  code=models.CharField(max_length=2,unique=True)
  slug=models.SlugField(blank=True) 
  crawlIP=models.CharField(max_length=256,null=True,blank=True)
  stateShortCode=models.CharField(max_length=2)
  isNIC=models.BooleanField(default=True)
  def __str__(self):
    return self.name

class District(models.Model):
  state=models.ForeignKey('state',on_delete=models.CASCADE)
  name=models.CharField(max_length=256)
  code=models.CharField(max_length=4,unique=True)
  slug=models.SlugField(blank=True) 
  tcode=models.CharField(max_length=8,blank=True,null=True)
  def __str__(self):
    return self.name

class Block(models.Model):
  district=models.ForeignKey('district',on_delete=models.CASCADE)
  name=models.CharField(max_length=256)
  code=models.CharField(max_length=7,unique=True)
  slug=models.SlugField(blank=True) 
  tcode=models.CharField(max_length=7,unique=True,null=True,blank=True)
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
  jobcardRegisterFile=models.FileField(null=True, blank=True,upload_to=get_panchayat_upload_path,max_length=512)
  isDataAccurate=models.BooleanField(default=False)
  def __str__(self):
    return "%s-%s-%s-%s" % (self.block.district.state.name,self.block.district.name,self.block.name,self.name)

class Village(models.Model):
  panchayat=models.ForeignKey('Panchayat',on_delete=models.CASCADE,null=True,blank=True)
  name=models.CharField(max_length=256,null=True,blank=True)
  code=models.CharField(max_length=12,null=True,blank=True)  #Field only for compatibility with otherlocations not used for TElangana
  slug=models.SlugField(blank=True) 
  tcode=models.CharField(max_length=12,null=True,blank=True)

  def __str__(self):
    return self.name


#Models for Reports
#The below Model is used to uploading generic reports like on the fly zip of existing reports etc etc
class genericReport(models.Model):
  reportFile=models.FileField(null=True, blank=True,upload_to=get_genericreport_upload_path,max_length=512)
  updateDate=models.DateTimeField(auto_now=True)
  created=models.DateTimeField(null=True,blank=True,auto_now_add=True)
  def __str__(self):
    return self.reportFile.url

#The below Model is used to store block and panchayat level reports
class Report(models.Model):
  block=models.ForeignKey('Block',on_delete=models.CASCADE,null=True,blank=True)
  panchayat=models.ForeignKey('Panchayat',on_delete=models.CASCADE,null=True,blank=True)
  reportFile=models.FileField(null=True, blank=True,upload_to=get_report_upload_path,max_length=512)
  reportType=models.CharField(max_length=256)
  created=models.DateTimeField(auto_now_add=True)
  modified=models.DateTimeField(auto_now=True)
  class Meta:
        unique_together = ('block', 'panchayat','reportType','finyear')  
  def __str__(self):
    if self.block is not None:
      return self.block.name+"-"+self.reportType
    elif self.panchayat is not None:
      return self.panchayat.name+"-"+self.reportType
    else:
      return reportType
  


def get_report_upload_path(instance, filename):
  if instance.panchayat is not None:
    return os.path.join("nrega",instance.panchayat.block.district.state.slug,instance.panchayat.block.district.slug,instance.panchayat.block.slug,instance.panchayat.slug,"DATA","NICREPORTS",filename)
  elif instance.block is not None:
    return os.path.join( "nrega",instance.block.district.state.slug,instance.block.district.slug,instance.block.slug,"DATA","NICREPORTS",filename)
  else:
    return os.path.join( "misc",filename)


