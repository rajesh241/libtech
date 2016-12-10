import re
from bs4 import BeautifulSoup
import os
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
      table=htmlsoup.find('table',id=eachID)
      if table is not None:
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



def writeFile(filename,filedata):
  if not os.path.exists(os.path.dirname(filename)):
    os.makedirs(os.path.dirname(filename))
  myfile = open(filename, "wb")
  myfile.write(filedata.encode("UTF-8"))
  myfile.close()
 
