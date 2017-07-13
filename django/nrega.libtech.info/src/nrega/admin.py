from django.contrib import admin

# Register your models here.
from .models import State,District,Block,Panchayat,Muster,Applicant,PanchayatReport,VillageReport,WorkDetail,Wagelist,PanchayatStat,FTO,FPSShop,PaymentDetail,FPSStatus,Village,Jobcard,LibtechTag,TelanganaSSSGroup,FPSVillage,Partner,Phonebook,VillageFPSStatus,Broadcast,AudioLibrary

from .actions import export_as_csv_action

class libtechTagModelAdmin(admin.ModelAdmin):
  list_display=["name"]
  class Meta:
    model=LibtechTag

class stateModelAdmin(admin.ModelAdmin):
  list_display = ["name","stateShortCode","code","crawlIP"]
  class Meta:
    model=State

class districtModelAdmin(admin.ModelAdmin):
 # actions = ['download_csv']
  actions = [export_as_csv_action("CSV Export", fields=['name','stateName'])]
  list_display = ["name","stateName","code","fpsCode"]
  list_display_links=["name"]
  list_filter=["state"]
  search_fields=["name","code"]
  
#  list_editable=["description"]

  class Meta:
    model=District

class blockModelAdmin(admin.ModelAdmin):
  actions = [export_as_csv_action("CSV Export", fields=['name','districtName','stateName','code'])]
  list_display = ["name","districtName","stateName","code"]
  list_display_links=["name"]
  list_filter=["district__state"]
  search_fields=["name","code"]
  def get_queryset(self, request):
    qs = super(blockModelAdmin, self).get_queryset(request)
    print("This is getting accesed")
    if request.user.is_superuser:
      return qs
    else:
      myList=[request.user.id]
      return qs.filter(partners__in = myList)
  
  class Meta:
    model=Block

class fpsShopModelAdmin(admin.ModelAdmin):
  list_display=["name","fpsCode","get_block","get_district"]
  search_fields=["name","block__name"]
  def get_block(self,obj):
    return obj.block.name
  get_block.description="block"
  def get_district(self,obj):
    return obj.block.district.name
  get_district.description="district"

class fpsVillageModelAdmin(admin.ModelAdmin):
  list_display=["__str__","fpsShop"]

class villageFPSStatusModelAdmin(admin.ModelAdmin):
  actions = [export_as_csv_action("CSV Export", fields=["__str__","getVillageType","fpsStatus","getFPSBlock","getFPSMonth","getFPSYear","getAAYDeliveryDate","getPHHDeliveryDate"])]
  list_display=["__str__","getVillageType","fpsStatus","getFPSBlock","getFPSMonth","getFPSYear","getAAYDeliveryDate","getPHHDeliveryDate"]
  readonly_fields=["fpsVillage","fpsStatus"]
  def get_queryset(self, request):
    qs = super(villageFPSStatusModelAdmin, self).get_queryset(request)
    return qs.order_by('-fpsStatus__AAYDeliveryDate')

class fpsStatusModelAdmin(admin.ModelAdmin):
  list_display=["id","get_fpsCode","fpsMonth","fpsYear"]
  search_fields=["id","fpsShop__fpsCode"]
  list_filter=["isDownloaded","isProcessed","isComplete"]
  def get_fpsCode(self,obj):
    return obj.fpsShop.fpsCode
  get_fpsCode.description="fpsCode"

class villageModelAdmin(admin.ModelAdmin):
  list_display = ["name","tcode","panchayat"]
  readonly_fields=["panchayat"]
  search_fields=["name","tcode"]

class panchayatModelAdmin(admin.ModelAdmin):
  actions = [export_as_csv_action("CSV Export", fields=['name','id','remarks'])]
  list_display = ["__str__","name","code"]
  list_filter=["crawlRequirement","status","block__district__state"]
  search_fields=["name","code"]

  def get_queryset(self, request):
    qs = super(panchayatModelAdmin, self).get_queryset(request)
    if request.user.is_superuser:
      return qs
    else:
      myList=[request.user.id]
      return qs.filter(block__partners__in = myList,crawlRequirement="FULL")

  class Meta:
    model=Panchayat

class panchayatStatModelAdmin(admin.ModelAdmin):
  actions = [export_as_csv_action("CSV Export", fields=['__str__','finyear','nicWorkDays','libtechWorkDays'])]
  list_display=["get_panchayat","get_block","get_district","finyear","nicWorkDays","libtechWorkDays"]
  search_fields=["panchayat__code","panchayat__name","panchayat__block__name"]
  readonly_fields=["panchayat"]
  def get_panchayat(self,obj):
    return obj.panchayat.name
  get_panchayat.description="panchayat"
  def get_block(self,obj):
    return obj.panchayat.block.name
  get_block.description="block"
  def get_district(self,obj):
    return obj.panchayat.block.district.name
  get_district.description="district"
  def get_state(self,obj):
    return obj.panchayat.block.district.state.name
  get_state.description="state"

class panchayatReportModelAdmin(admin.ModelAdmin):
  list_display=["__str__","get_reportFile","finyear","updateDate","get_block","get_district","get_state"]
  readonly_fields=["panchayat","finyear","reportType","reportFile"]
  list_filter=["finyear","reportType"]
  search_fields=["panchayat__name","panchayat__block__name","panchayat__code"]
  def get_block(self, obj):
    return obj.panchayat.block.name
  def get_district(self, obj):
    return obj.panchayat.block.district.name
  def get_state(self, obj):
    return obj.panchayat.block.district.state.name
  def get_reportFile(self,obj):
    return "<a href='%s'>Download</a>" % obj.reportFile
  get_reportFile.allow_tags = True
  get_reportFile.description='Download'
  get_block.admin_order_field  = 'block'  #Allows column order sorting
  get_block.short_description = 'Block '  #Renames column head
#  get_district.admin_order_field  = 'district'  #Allows column order sorting
  get_district.short_description = 'District '  #Renames column head
#  get_state.admin_order_field  = 'state'  #Allows column order sorting
  get_state.short_description = 'State '  #Renames column head

class villageReportModelAdmin(admin.ModelAdmin):
  list_display=["__str__","finyear","updateDate","get_panchayat","get_block"]
  readonly_fields=["village","finyear","reportType","reportFile"]
  list_filter=["finyear","reportType"]
  search_fields=["village__name","village__panchayat__name","village_code"]
  def get_block(self, obj):
    return obj.village.panchayat.block.name
  def get_panchayat(self, obj):
    return obj.village.panchayat.name
  get_block.admin_order_field  = 'block'  #Allows column order sorting
  get_block.short_description = 'Block '  #Renames column head
#  get_district.admin_order_field  = 'district'  #Allows column order sorting
  get_panchayat.short_description = 'Panchayat '  #Renames column head


class musterModelAdmin(admin.ModelAdmin):
#  actions = [export_as_csv_action("CSV Export", fields=['name','blockName','districtName','stateName'])]
  list_display = ["id","musterNo","downloadAttemptCount","musterDownloadAttemptDate","finyear","block","panchayat","workCode","workName"]
  search_fields=["id","musterNo","block__code","panchayat__code","workCode"]
  list_filter=["isPanchayatNull","finyear","isDownloaded","isProcessed","allApplicantFound","block__district__state"]
  readonly_fields=["block","panchayat"]

class tjobcardModelAdmin(admin.ModelAdmin):
  list_display=["jobcard","tjobcard"]
  search_fields=["tjobcard","jobcard"]
  readonly_fields=["panchayat"]
  list_filter=["isDownloaded","isProcessed"]

class telanganaSSSgroupModelAdmin(admin.ModelAdmin):
  list_display=["groupName","groupCode"]

class applicantModelAdmin(admin.ModelAdmin):
  list_display=["jobcard1","applicantNo","panchayat","name","age","caste","fatherHusbandName","accountNo"]
  readonly_fields=["jobcard","applicantNo","panchayat","name","age","caste","fatherHusbandName","accountNo"]
  search_fields=["jobcard1"]

class workDetailModelAdmin(admin.ModelAdmin):
  list_display=["id","muster","musterIndex","applicant","zjobcard","zname","zaccountNo","creditedDate","musterStatus"]
  readonly_fields=["muster","applicant"]
  search_fields=["id","zjobcard","muster__id"]
#  def get_musterLink(self,obj):
#    return "<a href='%s'>Muster</a>" % obj.muster.
class ftoModelAdmin(admin.ModelAdmin):
  list_display=["id","ftoNo","block","finyear"] 
  list_filter=["finyear","isDownloaded","isProcessed","block__district__state"]
  search_fields=["id","ftoNo"]

class wagelistModelAdmin(admin.ModelAdmin):
  list_display=["id","wagelistNo","block","finyear"] 
  list_filter=["finyear","isDownloaded","isProcessed","isComplete","block__district__state"]
  search_fields=["id","wagelistNo"]


class phonebookModelAdmin(admin.ModelAdmin):
  list_display=["phone","partner"]
  readonly_fields=["phone","fpsVillage","panchayat"]
class partnerModelAdmin(admin.ModelAdmin):
  list_display=["name"]

class broadcastModelAdmin(admin.ModelAdmin):
  list_display=["name","startDate","endDate","minhour","maxhour"]

class audioLibraryModelAdmin(admin.ModelAdmin):
  list_display=["partner","audioFile"]

admin.site.register(Broadcast,broadcastModelAdmin)
admin.site.register(AudioLibrary,audioLibraryModelAdmin)
admin.site.register(Phonebook,phonebookModelAdmin)
admin.site.register(Partner,partnerModelAdmin)
admin.site.register(FPSVillage,fpsVillageModelAdmin)
admin.site.register(VillageFPSStatus,villageFPSStatusModelAdmin)
admin.site.register(State,stateModelAdmin)
admin.site.register(District,districtModelAdmin)
admin.site.register(Block,blockModelAdmin)
admin.site.register(Panchayat,panchayatModelAdmin)
admin.site.register(Village,villageModelAdmin)
admin.site.register(PanchayatReport,panchayatReportModelAdmin)
admin.site.register(VillageReport,villageReportModelAdmin)
admin.site.register(Muster,musterModelAdmin)
admin.site.register(Jobcard,tjobcardModelAdmin)
admin.site.register(Applicant,applicantModelAdmin)
admin.site.register(WorkDetail,workDetailModelAdmin)
admin.site.register(Wagelist,wagelistModelAdmin)
admin.site.register(FTO,ftoModelAdmin)
admin.site.register(PanchayatStat,panchayatStatModelAdmin)
admin.site.register(FPSShop,fpsShopModelAdmin)
admin.site.register(FPSStatus,fpsStatusModelAdmin)
admin.site.register(LibtechTag,libtechTagModelAdmin)
admin.site.register(TelanganaSSSGroup,telanganaSSSgroupModelAdmin)
# Reference Code for Downloading CSV
# def download_csv(self, request, queryset):
#   import csv
#   from django.http import HttpResponse
#   from io import StringIO
#
#
#   f = StringIO()
#   writer = csv.writer(f)
#   writer.writerow(["name", "state", "fullDistrictCode"])
#
#   for s in queryset:
#       writer.writerow([s.name, s.state, s.fullDistrictCode])
#
#   f.seek(0)
#   response = HttpResponse(f, content_type='text/csv')
#   response['Content-Disposition'] = 'attachment; filename=stat-info.csv'
#   return response
# download_csv.short_description = "Download CSV"
 
