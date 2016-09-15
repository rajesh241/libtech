from bs4 import BeautifulSoup
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable

def getDistrictParams(cur,districtName):
  query="select crawlIP,state,stateCode,stateShortCode,districtCode from crawlDistricts.districts where name='%s'" % (districtName.upper())
  cur.execute(query)
  row=cur.fetchone()
  crawlIP=row[0]
  stateName=row[1]
  stateCode=row[2]
  stateShortCode=row[3]
  districtCode=row[4]
  return crawlIP,stateName,stateCode,stateShortCode,districtCode
def NICToSQLDate(dateString):
  dateFormat="%d/%m/%Y"
  if dateString == '':
    outDate="Null"
  else:
    outDate="STR_TO_DATE('%s', '%s')" % (dateString,dateFormat)
  return outDate
def alterMISHTML(inhtml):
  htmlsoup=BeautifulSoup(inhtml,"html.parser")
  tableID="Details"
  outcsv=''
  try:
    table=htmlsoup.find('table',align="center")
    errorflag=0
  except:
    errorflag=1
  if errorflag==0:
    outcsv+=tableToCSV(table,tableID)
  return errorflag,outcsv

def tableToCSV(inhtml,tableID):
  mycsv=''
  rows=inhtml.findAll('tr')
  for eachRow in rows:
    thCols=eachRow.findAll('th')
    if len(thCols) > 1:
     for eachTD in thCols:
       mycsv+='%s,' % eachTD.text
     mycsv+='\n'

    tdCols=eachRow.findAll('td')
    if len(tdCols) > 1:
      for eachTD in tdCols:
       mycsv+='%s,' % eachTD.text
      mycsv+='\n'

  return mycsv

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

def alterFTOHTML(inhtml):
  htmlsoup=BeautifulSoup(inhtml,"html.parser")
  tableID="ftoDetails"
  outhtml=''
  try:
    table=htmlsoup.find('table',align="center")
    errorflag=0
  except:
    errorflag=1
  if errorflag==0:
    outhtml+=stripTableAttributes(table,tableID)
  return errorflag,outhtml

def getMusterPaymentDate(inhtml):
  htmlsoup=BeautifulSoup(inhtml,"html.parser")
  try:
    paymentTD=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lblPayDate")
    paymentDate=paymentTD.text
    sanctionTD=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lblSanctionno")
    sanctionNo=sanctionTD.text
    sanctionTD=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lblSanctionDate")
    sanctionDate=sanctionTD.text
    #print "There is not ERROR here"
  except:
    paymentDate=''
    sanctionNo=''
    sanctionDate=''
  return paymentDate,sanctionNo,sanctionDate

  
def alterMusterHTML(inhtml):
  htmlsoup=BeautifulSoup(inhtml,"html.parser")
  outhtml=''
  try:
    table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
    rows = table.findAll('tr')
    errorflag=0
    #print "There is not ERROR here"
  except:
    errorflag=1
    #print "Cannot find the table"
  if errorflag==0:
    outhtml=rewriteTable(htmlsoup,"Muster Details","ctl00_ContentPlaceHolder1_grdShowRecords")
    
  return errorflag,outhtml

def rewriteTable(htmlSoup,title,tableID):
  myhtml=''
  myhtml+=  getCenterAligned('<h3 style="color:green"> %s</h3>' %title )
  tables=htmlSoup.findAll('table',{"id" : tableID})
  for table in tables:
    myhtml+=stripTableAttributes(table,tableID)
  return myhtml
  
def stripTableAttributes(inhtml,tableID):
  tableHTML=''
  classAtt='id = "%s" border=1 class = " table table-striped"' % tableID
  tableHTML+='<table %s">' % classAtt
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




