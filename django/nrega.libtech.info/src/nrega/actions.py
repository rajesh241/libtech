import unicodecsv
from django.http import HttpResponse
import time
import datetime
import os
from django.http import HttpResponseRedirect
from django.conf import settings
#from mysite.settings import AWS_ACCESS_KEY, AWS_SECRET_KEY, S3_BUCKET, REGION_NAME
from libtech_settings import LIBTECH_AWS_ACCESS_KEY_ID,LIBTECH_AWS_SECRET_ACCESS_KEY
from libtech.settings import AWS_STORAGE_BUCKET_NAME,AWS_S3_REGION_NAME,MEDIA_URL,S3_URL
import boto3
from boto3.session import Session
from botocore.client import Config

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

def get_panchayat_dump(modeladmin,request,queryset):
    curTimeStamp=str(int(time.time()))
    dateString=datetime.date.today().strftime("%B_%d_%Y_%I_%M")
    baseDir="/tmp/genericReports/"
    filename="/tmp/genericReports/panchayatDump.csv"
    s=''
    s+="panchayatID,panchayatCode,panchayatName,blockID,blockCode,blockName,districtID,districtCode,districtName,stateID,stateCode,stateName\n"
    for obj in queryset:
      eachLine="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (str(obj.id),obj.code,obj.name,str(obj.block.id),obj.block.code,obj.block.name,str(obj.block.district.id),obj.block.district.code,obj.block.district.name,str(obj.block.district.state.id),obj.block.district.state.code,obj.block.district.state.name)
      s+=eachLine 
    with open(filename,"w") as f:
      f.write(s)
    cloudFilename="media/temp/panchayatDump.csv"
    session = boto3.session.Session(aws_access_key_id=LIBTECH_AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=LIBTECH_AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3',config=Config(signature_version='s3v4'))
    s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(ACL='public-read',Key=cloudFilename, Body=s)
    baseURL="https://s3.ap-south-1.amazonaws.com/libtech-nrega"
    publicURL="%s/%s" % (baseURL,cloudFilename)
#    with open("/tmp/test.csv","w") as f:
#      f.write(s)
    return HttpResponseRedirect(publicURL)
 

 
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
    cmd="cd %s && zip -r %s.zip *" % (baseDir,baseDir)
    os.system(cmd)
    in_file = open("%s.zip" % baseDir, "rb") # opening for [r]eading as [b]inary
    zipdata = in_file.read() # if you only wanted to read 512 bytes, do .read(512)
    in_file.close()


    cloudFilename="media/temp/%s_%s.zip" % (dateString,curTimeStamp)
    session = boto3.session.Session(aws_access_key_id=LIBTECH_AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=LIBTECH_AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3',config=Config(signature_version='s3v4'))
    s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(ACL='public-read',Key=cloudFilename, Body=zipdata)
    baseURL="https://s3.ap-south-1.amazonaws.com/libtech-nrega"
    publicURL="%s/%s" % (baseURL,cloudFilename)
#    with open("/tmp/test.csv","w") as f:
#      f.write(s)
    return HttpResponseRedirect(publicURL)
    
download_reports_zip.short_description = "Download Selected Reports as Zip" 
get_panchayat_dump.short_description="Get PanchayatDump"
