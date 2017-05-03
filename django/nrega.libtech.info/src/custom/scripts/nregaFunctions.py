import re
from bs4 import BeautifulSoup
from customSettings import repoDir,djangoDir,djangoSettings
import sys
import os
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from wrappers.logger import loggerFetch
import datetime
import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,PanchayatReport
def getCurrentFinYear():
  now = datetime.datetime.now()
  month=now.month
  if now.month > 3:
    year=now.year+1
  else:
    year=year
  return year% 100

def getFullFinYear(shortFinYear):
  shortFinYear_1 = int(shortFinYear) -1
  fullFinYear="20%s-20%s" % (str(shortFinYear_1), str(shortFinYear))
  return fullFinYear

def savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,filecontent):
  myReport=PanchayatReport.objects.filter(panchayat=eachPanchayat,finyear=finyear,reportType=reportType).first()
  if myReport is None:
    PanchayatReport.objects.create(panchayat=eachPanchayat,finyear=finyear,reportType=reportType)   
    logger.info("Report Created")
  else:
    logger.info("Report Already Exists")
  myReport=PanchayatReport.objects.filter(panchayat=eachPanchayat,finyear=finyear,reportType=reportType).first()
  myReport.reportFile.save(filename, ContentFile(filecontent))
  myReport.save()



def getjcNumber(jobcard):
  jobcardArray=jobcard.split('/')
#  print(jobcardArray[1])
  jcNumber=re.sub("[^0-9]", "", jobcardArray[1])
  return jcNumber


def htmlWrapperLocal(title = None, head = None, body = None):
  html_text = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    
    <title>title_text</title>

    <!-- Bootstrap -->

    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <link rel="stylesheet" href="/libtech-nrega/static/css/bootstrap.min.css">

    <!-- Optional theme -->
    <link rel="stylesheet" href="/libtech-nrega/static/css/bootstrap-theme.min.css">

    <div align="center">head_text</div>

  </head>
    
  <body>

    body_text
    
    <!-- jQuery (necessary for Bootstrap"s JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->

    <!-- Latest compiled and minified JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>

  </body>
</html>
'''
  html_text = html_text.replace('title_text', title)
  html_text = html_text.replace('head_text', head)
  html_text = html_text.replace('body_text', body)

  return html_text
def table2csv(table):
  outcsv=''
  rows=table.findAll('tr')
  for eachRow in rows:
    thCols=eachRow.findAll('th')
    if len(thCols) > 0:
      for eachTD in thCols:
        outcsv+='%s,' % eachTD.text

    tdCols=eachRow.findAll('td')
    if len(tdCols) > 0:
      for eachTD in tdCols:
        outcsv+='%s,' % eachTD.text
    outcsv+='\n'

  return outcsv


    
def stripTableAttributes(inhtml,tableID):
  tableHTML=''
  classAtt='id = "%s" border=1 class = " table table-striped"' % tableID
  tableHTML+='<table %s>' % classAtt
  rows=inhtml.findAll('tr')
  for eachRow in rows:
    thCols=eachRow.findAll('th')
    if len(thCols) > 1:
     tableHTML+='<tr>'
     for eachTD in thCols:
       tableHTML+='<th>%s</th>' % eachTD.text
     tableHTML+='</tr>'

    tdCols=eachRow.findAll('td')
    if len(tdCols) > 1:
      tableHTML+='<tr>'
      for eachTD in tdCols:
        tableHTML+='<td>%s</td>' % eachTD.text
      tableHTML+='</tr>'

  tableHTML+='</table>'
  return tableHTML



