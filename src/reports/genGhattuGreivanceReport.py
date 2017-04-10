import MySQLdb
import datetime
import datetime
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token
import math
import time
from reportFunctions import arrayToHTMLLine 
def main():
  ts=math.trunc(time.time())
  #db = MySQLdb.connect(host="localhost", user="root", passwd="ccmpProject**", db="libtech",charset='utf8')
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
##Setting Table html

  reportTable="""
     <html>
     <head>
     <style>
    table, th, td {
    border: 2px solid #097054;
    border-collapse: collapse;
    padding-left: 5px;
    padding-right: 5px;
    }
    table {
     margin-bottom: 20px
   }
    h1{
    color: #097054
    }

    </style>
    </head>
     <body>
   """
  reportTableClosed=reportTable
  reportTable+="<h1> Ghattu Greivance Management System</h1>"
  reportTable+="<h2> Open Complaints</h2>"
  reportTable+='<h4> For Closed Complaints click <a href="./closed.html">here</a></h4>'
  reportTableClosed+="<h2> Closed Complaints</h2>"
  tableheader="""<table>
     <tr>
       <th>MissedCall ID</th>
       <th>LastUpdateDate</th>
       <th>Panchayat</th>
       <th>Phone</th>
       <th>Jobcard</th>
       <th>currentStep</th>
       <th>complaintNumber</th>
       <th>complaintDate</th>
       <th>Html Link</th>
      </tr>
  """
  reportTable+=tableheader
  reportTableClosed+=tableheader
  query="select max(ts) maxts,missedCallID from ghattuMissedCallsLog group by missedCallID order by missedCallID;"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    maxts=row[0]
    missedCallID=row[1]
    tsstring=datetime.datetime.fromtimestamp(maxts).strftime('%d-%m-%Y')
    query="select phone,jobcard,currentStep,finalStatus,complaintNumber,complaintDate,htmlgen from ghattuMissedCallsLog where missedCallID="+str(missedCallID)+" and ts="+str(maxts)
    cur.execute(query)
    row1=cur.fetchone()
    phone=row1[0]
    jobcard=row1[1]
    currentStep=row1[2]
    finalStatus=row1[3]
    complaintNumber=row1[4]
    complaintDate=row1[5]
    htmlgen=row1[6]
    #Getting the panchayatName
    query="use mahabubnagar"
    cur.execute(query)
    query="select p.name from jobcardRegister j,panchayats p where j.blockCode=p.blockCode and j.panchayatCode=p.panchayatCode and jobcard='%s'" % jobcard
    cur.execute(query)
    panchayat=''
    if (cur.rowcount == 1):
      panchRow=cur.fetchone()
      panchayat=panchRow[0]
    query="use libtech"
    cur.execute(query)
    htmllink='<a href="./'+str(missedCallID)+'_'+phone+'.html">view html</a>'
    tableArray=[missedCallID,tsstring,panchayat,phone,jobcard,currentStep,complaintNumber,str(complaintDate),htmllink]
    if(finalStatus != 'Closed'):
    #if(htmlgen ==1 ):
      reportTable+=arrayToHTMLLine(tableArray)
    else:
      reportTableClosed+=arrayToHTMLLine(tableArray)
    print str(missedCallID)+"  "+str(tsstring)+"  "+panchayat
  
  reportTable+="""
    </table></body></html>
  """
  reportTableClosed+="""
    </table></body></html>
  """
  htmlFile=open("/home/libtech/webroot/ghattuGrievance/ghattu/nrega/html/index.html",'w')
  htmlFile.write(reportTable)
  htmlFile=open("/home/libtech/webroot/ghattuGrievance/ghattu/nrega/html/closed.html",'w')
  htmlFile.write(reportTableClosed)

if __name__ == '__main__':
  main()
