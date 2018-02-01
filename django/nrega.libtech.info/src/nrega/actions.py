import unicodecsv
from django.http import HttpResponse
import time
import datetime
import os
def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta
        
        if not fields:
            field_names = [field.name for field in opts.fields]
        else:
            field_names = fields
        filename='%s.csv' % str(opts).replace('.', '_')
      #  response = HttpResponse(contect_type='text/csv')
        response = HttpResponse(filename, content_type='text/csv')
      #  response['Content-Disposition'] = 'attachment; filename=stat-info.csv'
        #response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % str(opts).replace('.', '_')

        writer = unicodecsv.writer(response, encoding='utf-8')
        if header:
            writer.writerow(field_names)
        for obj in queryset:
            row = [getattr(obj, field)() if callable(getattr(obj, field)) else getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    export_as_csv.short_description = description
    return export_as_csv


def download_reports_zip(modeladmin, request, queryset):
    curTimeStamp=str(int(time.time()))
    dateString=datetime.date.today().strftime("%B_%d_%Y_%I_%M")
    baseDir="/tmp/genericReports/%s_%s" % (dateString,curTimeStamp)
    s='' 
    for obj in queryset:
      filepath="%s/%s" % (baseDir,obj.panchayat.slug)
      filename="%s_%s.csv" % (obj,obj.finyear)
      cmd="mkdir -p %s && cd %s && wget -O %s %s " %(filepath,filepath,filename,obj.reportFile.url) 
      os.system(cmd)
      s+=obj.reportFile.url
      s+="\n"
    with open("/tmp/test.csv","w") as f:
      f.write(s)
    
download_reports_zip.short_description = "Download Selected Reports as Zip" 
