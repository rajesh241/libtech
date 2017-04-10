import re
from bs4 import BeautifulSoup
import os


def getFullFinYear(shortFinYear):
  shortFinYear_1 = int(shortFinYear) -1
  fullFinYear="20%s-20%s" % (str(shortFinYear_1), str(shortFinYear))
  return fullFinYear

def NICToSQLDate(dateString):
  dateFormat="%d/%m/%Y"
  if dateString is not None:
    if (dateString == '') or ("NA" in dateString):
      outDate="Null"
    else:
      outDate="STR_TO_DATE('%s', '%s')" % (dateString,dateFormat)
  else:
    outDate="Null"
  return outDate
def getjcNumber(jobcard):
  jobcardArray=jobcard.split('/')
  jcNumber=re.sub("[^0-9]", "", jobcardArray[1])
  return jcNumber

def formatName(name):
  formatName=re.sub(r"[^A-Za-z]+", '', name).lower()
  return formatName

def alterHTMLTables(inhtml,title,tableIDs=None):
  outhtml=''
  if tableIDs is None:
    outhtml+=rewriteAllTables(inhtml,title)
  else:
    htmlsoup=BeautifulSoup(inhtml,"html.parser")
    for eachID in tableIDs:
      tables=htmlsoup.findAll('table',id=eachID)
      for table in tables:
        outhtml+=stripTableAttributes(table,eachID)
    outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
  return outhtml

def rewriteAllTables(inhtml,title):
  htmlsoup=BeautifulSoup(inhtml,"html.parser")
  i=0
  myhtml=''
  tables=htmlsoup.findAll('table')
  for table in tables:
    tableID="libtechTable%s" % str(i)
    myhtml+=  getCenterAligned('<h3 style="color:green"> %s</h3>' %tableID )
    myhtml+=stripTableAttributes(table,tableID)
    i=i+1
  myhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=myhtml)
  return myhtml

def getCenterAligned(text):
  return '<div align="center">%s</div>' % text


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
def genHTMLHeader(headerLabels,headerValues):
  tableHTML=''
  classAtt='id = "basic" class = " table table-striped"'
  tableHTML+='<table %s">' % classAtt
  i=0
  for eachHeaderItem in headerValues:
    tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %(headerLabels[i],eachHeaderItem.upper())
    i=i+1
  tableHTML+='</table>'
  return tableHTML


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
    <link rel="stylesheet" href="/css/bootstrap.min.css">

    <!-- Optional theme -->
    <link rel="stylesheet" href="/css/bootstrap-theme.min.css">

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

def writeFileGCS(filename,filedata):
  try:
    if not os.path.exists(os.path.dirname(filename)):
      os.makedirs(os.path.dirname(filename))
    myfile = open(filename, "wb")
    myfile.write(filedata.encode("UTF-8"))
    myfile.close()
    error=0
  except:
    error=1
  return error



def writeFile(filename,filedata):
  if not os.path.exists(os.path.dirname(filename)):
    os.makedirs(os.path.dirname(filename))
  myfile = open(filename, "wb")
  myfile.write(filedata.encode("UTF-8"))
  myfile.close()

def tabletUIQueryToHTMLTable(cur, query, staticLinkPath=None,field_names=None, extra=None,extraLabel=None,hiddenNames=None,hiddenValues=None):
  cur.execute(query)
  results = cur.fetchall()


  if field_names == None:
    field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)
  
  table_html='''
<div class="container col-xs-6">
  <div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr class="info">
      '''
  i=0
  for field_name in field_names:
    if i==0:
      table_html += "<th >" + field_name.strip() + "</th>"
    i=i+1 
  if extra != None:
    table_html += "<th >" + extraLabel + "</th>"

  table_html += '''
      </tr>
    </thead>
    <tbody>
      '''
  
  for row in results:
    inputs=''
    table_html += "<tr class='success'>"

    i = 0
    while i < num_fields:
      if i==0:
        rowstripped=row[0].replace(" ","")
        if staticLinkPath != None:
          rowvalue='<a href="./%s/%s.html"> %s </a>' % (staticLinkPath,rowstripped.upper(),row[0])
        else:
          rowvalue='<a href="./%s/%s.html"> %s </a>' % (rowstripped.upper(),rowstripped.upper(),row[0])
       # rowvalue=linkValue.replace("linktext",row[i])
        table_html += "<td>" + getString(rowvalue) + "</td>"
      else:
        table_html += "<td>" + getString(row[i]) + "</td>"
      i += 1


    table_html += "</tr>"

  table_html += '''
    </tbody>
  </table>
  </div>
</div>
  '''
  return table_html

def getString(inString):
  return str(inString)

def tabletUIReportTable(cur, query, staticLinkPath=None,field_names=None, extra=None,extraLabel=None,hiddenNames=None,hiddenValues=None):

  cur.execute(query)
  results = cur.fetchall()


  if field_names == None:
    field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)
  
  table_html='''
<div class="container col-xs-6">
  <div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr class="info">
      '''
  i=0
  for field_name in field_names:
    table_html += "<th >" + field_name.strip() + "</th>"
    i=i+1 
  table_html += "<th colspan=3>View HTML</th>"
  table_html += "<th > | </th>"
  table_html += "<th colspan=3>Download CSV</th>"
  if extra != None:
    table_html += "<th >" + extraLabel + "</th>"

  table_html += '''
      </tr>
    </thead>
    <tbody>
      '''
  
  for row in results:
    inputs=''
    table_html += "<tr class='success'>"

    i = 0
    while i < num_fields:
      if i==1:
        rowstripped=row[1].replace(" ","")
        if staticLinkPath != None:
          targetLink="./%s/%s.html" % (staticLinkPath,rowstripped)
          targetcsv="./%s/%s.csv" % (staticLinkPath,rowstripped)
          targetLink16="./%s/%s.html" % (staticLinkPath+'16',rowstripped)
          targetcsv16="./%s/%s.csv" % (staticLinkPath+'16',rowstripped)
          targetLink17="./%s/%s.html" % (staticLinkPath+'17',rowstripped)
          targetcsv17="./%s/%s.csv" % (staticLinkPath+'17',rowstripped)
          rowvalue='<a href="./%s/%s.html"> %s </a>' % (staticLinkPath+"17",rowstripped,row[1])
        else:
          rowvalue='<a href="./%s/%s.html"> %s </a>' % (rowstripped.upper(),rowstripped.upper(),row[1])
       # rowvalue=linkValue.replace("linktext",row[i])
        table_html += "<td>" + getString(rowvalue) + "</td>"
      else:
        table_html += "<td>" + getString(row[i]) + "</td>"
      i += 1

    myForm=getButtonV3(targetLink,'viewHTML','All')
    myForm=myForm.replace("extrainputs","")
  #  table_html += "<td>  " + myForm + "</td>"
    table_html += "<td>     </td>"
    myForm=getButtonV3(targetLink16,'viewHTML','FY16')
    myForm=myForm.replace("extrainputs","")
    table_html += "<td>     </td>"
   # table_html += "<td>" + myForm + "</td>"
    myForm=getButtonV3(targetLink17,'viewHTML','FY17')
    myForm=myForm.replace("extrainputs","")
    table_html += "<td>" + myForm + "</td>"

    table_html += "<td > | </td>"
    myForm=getButtonV3(targetcsv,'viewCSV','All')
    myForm=myForm.replace("extrainputs","")
    table_html += "<td>     </td>"
  #  table_html += "<td>" + myForm + "</td>"
    myForm=getButtonV3(targetcsv16,'viewCSV','FY16')
    myForm=myForm.replace("extrainputs","")
    table_html += "<td>     </td>"
  #  table_html += "<td>" + myForm + "</td>"
    myForm=getButtonV3(targetcsv17,'viewCSV','FY17')
    myForm=myForm.replace("extrainputs","")
    table_html += "<td>" + myForm + "</td>"

    table_html += "</tr>"

  table_html += '''
    </tbody>
  </table>
  </div>
</div>
  '''
  return table_html

def getButtonV3(action_text, form_type, button_text):


  form_html = '''
  <form action="action_text" method="POST" enctype="multipart/form-data" >
    form_text
  </form>
'''
  form_html = form_html.replace('action_text', action_text)

  form_text = '''
        <div class="input-group">
          <input name="formType" value="form_type" type="hidden">
          extrainputs 
          <button type="submit" class="btn btn-default">button_text</button>
        </div>
''' 
#  form_text = form_text.replace('jobcard_value', str(jobcard))
  form_text = form_text.replace('form_type', form_type)
  form_text = form_text.replace('button_text', button_text)

  return form_html.replace('form_text', form_text)


