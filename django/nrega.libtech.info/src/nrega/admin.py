from django.contrib import admin

# Register your models here.
from .models import State,District,Block,Panchayat,Muster,Applicant,PanchayatReport,WorkDetail,Wagelist
from .actions import export_as_csv_action
class stateModelAdmin(admin.ModelAdmin):
  list_display = ["name","stateShortCode","code","crawlIP"]
  class Meta:
    model=State

class districtModelAdmin(admin.ModelAdmin):
 # actions = ['download_csv']
  actions = [export_as_csv_action("CSV Export", fields=['name','stateName'])]
  list_display = ["name","stateName","code"]
  list_display_links=["name"]
  list_filter=["state"]
  search_fields=["name"]
  
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

class panchayatModelAdmin(admin.ModelAdmin):
  actions = [export_as_csv_action("CSV Export", fields=['name','code','blockName','districtName','stateName','id'])]
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

class panchayatReportModelAdmin(admin.ModelAdmin):
  list_display=["__str__","get_reportFile","finyear","updateDate","get_block","get_district","get_state"]
  readonly_fields=["panchayat","finyear","reportType","reportFile"]
  list_filter=["finyear","reportType"]
  search_fields=["panchayat__name","panchayat__block__name"]
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
  list_display = ["musterNo","finyear","block","panchayat","workCode","workName"]
  search_fields=["musterNo","block__code"]
  list_filter=["isRequired","finyear","isDownloaded","block__district__state"]
  readonly_fields=["block","panchayat"]

class applicantModelAdmin(admin.ModelAdmin):
  list_display=["jobcard","applicantNo","panchayat","name","age","caste","fatherHusbandName","accountNo"]
  readonly_fields=["jobcard","applicantNo","panchayat","name","age","caste","fatherHusbandName","accountNo"]
  search_fields=["jobcard"]

class workDetailModelAdmin(admin.ModelAdmin):
  list_display=["muster","musterIndex","wagelist","applicant","zjobcard","zname","zaccountNo","creditedDate","musterStatus"]
  readonly_fields=["muster","applicant"]
class wagelistModelAdmin(admin.ModelAdmin):
  list_display=["wagelistNo","block","finyear"] 
admin.site.register(State,stateModelAdmin)
admin.site.register(District,districtModelAdmin)
admin.site.register(Block,blockModelAdmin)
admin.site.register(Panchayat,panchayatModelAdmin)
admin.site.register(PanchayatReport,panchayatReportModelAdmin)
admin.site.register(Muster,musterModelAdmin)
admin.site.register(Applicant,applicantModelAdmin)
admin.site.register(WorkDetail,workDetailModelAdmin)
admin.site.register(Wagelist,wagelistModelAdmin)
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
 
