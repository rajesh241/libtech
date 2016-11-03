import re
import os
import sys
import datetime
import time
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
sys.path.insert(0, fileDir+'/../scripts/')
from nregaSettings import nregaStaticWebDir,nregaRawDataDir 



def getFullFinYear(shortFinYear):
  shortFinYear_1 = int(shortFinYear) -1
  fullFinYear="20%s-20%s" % (str(shortFinYear_1), str(shortFinYear))
  return fullFinYear



def getString1(a):
  if a is None:
    return ' '
  elif isinstance(a, datetime.date):
    return str(a)
  else:
    try:
      value = int(a)
      return str(a)
    except:
      return a

def getCenterAligned(text):
  return '<div align="center">%s</div>' % text
def htmlWrapperLocalRelativeCSS(relativeCSSPath= None,title = None, head = None, body = None):
  if relativeCSSPath==None:
    relativeCSSPath='/'
  
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
    <link rel="stylesheet" href="css_path/css/bootstrap.min.css">

    <!-- Optional theme -->
    <link rel="stylesheet" href="css_path/css/bootstrap-theme.min.css">

    <div align="center">head_text</div>

  </head>
  <body>

  generate_date  
    body_text
    
    <!-- jQuery (necessary for Bootstrap"s JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->

    <!-- Latest compiled and minified JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>

  </body>
</html>
'''
  today = datetime.datetime.today()
  reportGenerateDate=today.strftime('%d-%b-%Y  %H:%M:%S')
  reportGenerationDateString= getCenterAligned('<h3 style="color:green"> Report Generated On: %s</h3>' % (reportGenerateDate))
  html_text = html_text.replace('title_text', title)
  html_text = html_text.replace('css_path', relativeCSSPath)
  html_text = html_text.replace('head_text', head)
  html_text = html_text.replace('body_text', body)
  html_text = html_text.replace('generate_date', reportGenerationDateString)

  return html_text



def tabletUIQuery2HTML(cur, query, query_caption=None, htmlDir=None,field_names=None, extra=None,extraLabel=None,hiddenNames=None,hiddenValues=None,isBlock=None):
  if isBlock==1:
    relativeBasePath='../../'
  else:
    relativeBasePath='../../../'
  cur.execute(query)
  results = cur.fetchall()

  if query_caption == None:
    query_caption = "Query:"

  if field_names == None:
    field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)

 
  table_html='''
<div class="container">
  <pre>    query_text</pre>
  <table class="table table-striped">
    <thead>
      <tr>
      '''

  if isBlock == 1:
    i=2 #Start with Panchayat
  else:
    i=3 #Start after Panchayat
  while i < num_fields:
    table_html += "<th>" + field_names[i].strip() + "</th>"
    i=i+1


  table_html += '''
      </tr>
    </thead>
    <tbody>
      '''
  
  for row in results:
    inputs=''
    i=0
    finyear=row[0]
    blockName=row[1]
    panchayatName=row[2]
    table_html += "<tr>"

    if isBlock == 1:
      i=2 #Start with Panchayat
    else:
      i=3 #Start after Panchayat

    while i < num_fields:
      rowvalue=row[i]
      if rowvalue is not None:
        if hiddenNames != None:
          if str(i) in hiddenValues:
            j=hiddenValues.index(str(i))
            linktype=hiddenNames[j]
            if linktype == 'jobcard':
              baseLinkPath='%s/%s/%s/jobcardRegister/' % (relativeBasePath,blockName.upper(),panchayatName.upper())
              filePath="%s/%s/%s/jobcardRegister/%s.html" % (htmlDir,blockName.upper(),panchayatName.upper(),rowvalue.replace("/","_"))
              baseLinkTarget=baseLinkPath+rowvalue.replace("/","_")+'.html'
            if linktype == 'muster':
              baseLinkPath='%s/%s/%s/MUSTERS/%s/' % (relativeBasePath,blockName.upper(),panchayatName.upper(),getFullFinYear(row[0]))
              filePath="%s/%s/%s/MUSTERS/%s/%s.html" % (htmlDir,blockName.upper(),panchayatName.upper(),getFullFinYear(row[0]),rowvalue.replace("/","_"))
              #print rowvalue
              baseLinkTarget=baseLinkPath+rowvalue+'.html'
            if linktype == 'fto':
              baseLinkPath='%s/%s/FTO/%s/' % (relativeBasePath,blockName.upper(),getFullFinYear(row[0]))
              baseLinkTarget=baseLinkPath+rowvalue.replace("/","_")+'.html'
              filePath="%s/%s/FTO/%s/%s.html" % (htmlDir,blockName.upper(),getFullFinYear(row[0]),rowvalue.replace("/","_"))
            if os.path.isfile(filePath):
              rowvalue='<a href="%s">%s</a>'%(baseLinkTarget,rowvalue)
      table_html += "<td>" + getString1(rowvalue) + "</td>"
      #table_html += "<td>" + rowvalue + "</td>"
      i += 1

    if extra != None:
      table_html += "<td>" + extra.replace('extrainputs',inputs) + "</td>"

    table_html += "</tr>"

  table_html += '''
    </tbody>
  </table>
</div>
  '''
  return table_html


