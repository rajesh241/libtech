from django.contrib import admin
from django.db.models import F,Q,Sum,Count
from django.utils.safestring import mark_safe

import time
# Register your models here.
from .models import State,District,Block,Panchayat,Muster,Wagelist,FTO,CrawlQueue,WorkDetail,PaymentInfo,Report,Jobcard,LibtechTag,Worker,CrawlState,DownloadManager,GenericReport,Task,APWorkPayment,LibtechProcess
from .actions import download_reports_zip,setisError,setisProcessedFalse,setisActiveFalse,setisActiveTrue,removeTags,setIsSampleFalse
from libtech.settings import serverName

class stateModelAdmin(admin.ModelAdmin):
  list_display = ["name","stateShortCode","code","crawlIP"]
  class Meta:
    model=State

class districtModelAdmin(admin.ModelAdmin):
  list_display = ["name","code"]
  list_display_links=["name"]
  list_filter=["state"]
  search_fields=["name","code"]
  class Meta:
    model=District

class blockModelAdmin(admin.ModelAdmin):
  list_display = ["name","code","get_crawlRequest_link"]
  list_display_links=["name"]
  list_filter=["district__state"]
  search_fields=["name","code"]
  
  def get_crawlRequest_link(self,obj):
    url="http://%s/api/crawldatarequest/?code=%s" % (serverName,obj.code)
    myhtml='<a href="%s">Crawl</a>' % url
    return mark_safe(myhtml)
  get_crawlRequest_link.allow_tags = True
  get_crawlRequest_link.description='Download'

  class Meta:
    model=Block


class panchayatModelAdmin(admin.ModelAdmin):
  list_display = ["__str__","name","code","get_crawlRequest_link"]
  list_filter=["block__district__state"]
  search_fields=["name","code"]
  readonly_fields=["block","name","remarks","code"]
  def get_crawlRequest_link(self,obj):
    url="http://%s/api/crawldatarequest/?code=%s" % (serverName,obj.code)
    myhtml='<a href="%s">Crawl</a>' % url
    return mark_safe(myhtml)
  get_crawlRequest_link.allow_tags = True
  get_crawlRequest_link.description='Download'

class crawlStateModelAdmin(admin.ModelAdmin):
  actions = [setisActiveTrue,setisActiveFalse]
  list_display=["name","sequence","isActive","crawlType","needsQueueManager","nicHourRestriction"]
  list_filter=["isActive"]


class crawlQueueModelAdmin(admin.ModelAdmin):
  list_display = ["__str__","crawlState","crawlAttemptDate","pending","priority"]
  readonly_fields=["panchayat","block","startFinYear","progress"]
# def get_queryset(self, request):
#   qs = super(panchayatModelAdmin, self).get_queryset(request)
#   if request.user.is_superuser:
class musterModelAdmin(admin.ModelAdmin):
  actions = [setisError,setisProcessedFalse]
  list_display = ["id","musterNo","finyear","block","panchayat","modified","workCode","workName"]
  readonly_fields=["block","panchayat","downloadManager"]
  list_filter=["downloadManager__isDownloaded","downloadManager__downloadAttemptCount","downloadManager__isProcessed","downloadManager__isError"]
  search_fields=["id","musterNo","block__code","panchayat__code","workCode"]
#  list_filter=["isPanchayatNull","panchayat__crawlRequirement","finyear","allWorkerFound","isDownloaded","isProcessed","allApplicantFound","block__district__state"]
class wagelistModelAdmin(admin.ModelAdmin):
  list_display=["id","wagelistNo","block"]
  readonly_fields=["block"]
  search_fields=["wagelistNo"]
  list_filter=["downloadManager__isDownloaded","downloadManager__downloadAttemptCount","downloadManager__isProcessed"]


class FTOModelAdmin(admin.ModelAdmin):
  list_display=["id","ftoNo","block"]
  readonly_fields=["block"]
  search_fields=["ftoNo"]
  list_filter=["downloadManager__isDownloaded","downloadManager__downloadAttemptCount","downloadManager__isProcessed","downloadManager__isError"]

class workDetailModelAdmin(admin.ModelAdmin):
  list_display=["id"]

class paymentInfoModelAdmin(admin.ModelAdmin):
  list_display=["id"]

class libtechTagModelAdmin(admin.ModelAdmin):
  list_display=["id","name"]

class jobcardModelAdmin(admin.ModelAdmin):
  list_display=["id","__str__"]
  readonly_fields=["panchayat","downloadManager"]
  list_filter=["isVillageInfoMissing","isWorkerTableMissing","isPaymentTableMissing","downloadManager__isDownloaded","downloadManager__isProcessed"]
  search_fields=["panchayat__block__code","panchayat__code","tjobcard"]
class workerModelAdmin(admin.ModelAdmin):
  actions = [removeTags,setIsSampleFalse]
  list_display=["id","jobcard","name","applicantNo"]
  readonly_fields=["jobcard"]
  search_fields=["jobcard__id","jobcard__jobcard","jobcard__panchayat__code","jobcard__tjobcard"]
  list_filter=["is15Days","isSample","libtechTag"]
class downloadManagerModelAdmin(admin.ModelAdmin):
  list_display=["id"]

class genericReportModelAdmin(admin.ModelAdmin):
  actions = [download_reports_zip]
  list_display=["__str__","get_reportFile","updateDate"]
  list_filter=["libtechTag"]
  readonly_fields=["panchayat"]
  def get_reportFile(self,obj):
    return mark_safe("<a href='%s'>Download</a>" % obj.reportFile.url)
  get_reportFile.allow_tags = True
  get_reportFile.description='Download'

class taskModelAdmin(admin.ModelAdmin):
  list_display=["id","crawlQueue","crawlState","objID","modified","isComplete"]
  list_filter=["isComplete"]
class libtechProcessModelAdmin(admin.ModelAdmin):
  list_display=['pid','modified']
  readonly_fields=['pid']

class reportModelAdmin(admin.ModelAdmin):
  actions = [download_reports_zip]
  list_display=["__str__","get_reportFile","finyear","modified","get_block"]
  readonly_fields=["panchayat","finyear","reportType","reportFile"]
  list_filter=["finyear","reportType"]
  search_fields=["panchayat__name","panchayat__block__name","panchayat__code"]
  def get_block(self, obj):
    if obj.block is None:
      return obj.panchayat.block.name
    else:
      return obj.block.name
  def get_reportFile(self,obj):
    return mark_safe("<a href='%s'>Download</a>" % obj.reportFile.url)
  get_reportFile.allow_tags = True
  get_reportFile.description='Download'

class apWorkPaymentModelAdmin(admin.ModelAdmin):
  actions = [setisError,setisProcessedFalse]
  list_display=["id","jobcard"]
  readonly_fields=["jobcard","worker"]

admin.site.register(State,stateModelAdmin)
admin.site.register(District,districtModelAdmin)
admin.site.register(Block,blockModelAdmin)
admin.site.register(Panchayat,panchayatModelAdmin)
admin.site.register(Muster,musterModelAdmin)
admin.site.register(Wagelist,wagelistModelAdmin)
admin.site.register(FTO,FTOModelAdmin)
admin.site.register(WorkDetail,workDetailModelAdmin)
admin.site.register(PaymentInfo,paymentInfoModelAdmin)
admin.site.register(CrawlQueue,crawlQueueModelAdmin)
admin.site.register(CrawlState,crawlStateModelAdmin)
admin.site.register(Report,reportModelAdmin)
admin.site.register(Jobcard,jobcardModelAdmin)
admin.site.register(LibtechTag,libtechTagModelAdmin)
admin.site.register(Worker,workerModelAdmin)
admin.site.register(DownloadManager,downloadManagerModelAdmin)
admin.site.register(GenericReport,genericReportModelAdmin)
admin.site.register(Task,taskModelAdmin)
admin.site.register(APWorkPayment,apWorkPaymentModelAdmin)
admin.site.register(LibtechProcess,libtechProcessModelAdmin)
