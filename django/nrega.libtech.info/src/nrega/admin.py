from django.contrib import admin

# Register your models here.
from .models import State,District,Block,Panchayat,Muster,Applicant,PanchayatReport,WorkDetail,Wagelist,PanchayatStat,FTO,FPSShop,PaymentDetail,FPSStatus
from .actions import export_as_csv_action
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

class fpsStatusModelAdmin(admin.ModelAdmin):
  list_display=["id","get_fpsCode","fpsMonth","fpsYear"]
  search_fields=["id","fpsShop__fpsCode"]
  list_filter=["isDownloaded","isProcessed","isComplete"]
  def get_fpsCode(self,obj):
    return obj.fpsShop.fpsCode
  get_fpsCode.description="fpsCode"


class panchayatModelAdmin(admin.ModelAdmin):
  actions = [export_as_csv_action("CSV Export", fields=['name','code','blockName','districtName','stateName','id','remarks'])]
  list_display = ["name","blockName","districtName","stateName","code"]
  list_display_links=["name"]
  list_filter=["crawlRequirement","block__district__state"]
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
class musterModelAdmin(admin.ModelAdmin):
#  actions = [export_as_csv_action("CSV Export", fields=['name','blockName','districtName','stateName'])]
  list_display = ["id","musterNo","finyear","block","panchayat","workCode","workName"]
  search_fields=["id","musterNo","block__code"]
  list_filter=["isRequired","finyear","isDownloaded","isProcessed","allApplicantFound","block__district__state"]
  readonly_fields=["block","panchayat"]

class applicantModelAdmin(admin.ModelAdmin):
  list_display=["jobcard","applicantNo","panchayat","name","age","caste","fatherHusbandName","accountNo"]
  readonly_fields=["jobcard","applicantNo","panchayat","name","age","caste","fatherHusbandName","accountNo"]
  search_fields=["jobcard"]

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
admin.site.register(State,stateModelAdmin)
admin.site.register(District,districtModelAdmin)
admin.site.register(Block,blockModelAdmin)
admin.site.register(Panchayat,panchayatModelAdmin)
admin.site.register(PanchayatReport,panchayatReportModelAdmin)
admin.site.register(Muster,musterModelAdmin)
admin.site.register(Applicant,applicantModelAdmin)
admin.site.register(WorkDetail,workDetailModelAdmin)
admin.site.register(Wagelist,wagelistModelAdmin)
admin.site.register(FTO,ftoModelAdmin)
admin.site.register(PanchayatStat,panchayatStatModelAdmin)
admin.site.register(FPSShop,fpsShopModelAdmin)
admin.site.register(FPSStatus,fpsStatusModelAdmin)
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
 
