from __future__ import division
from reportFunctions import genBroadcastReport 
from reportFunctions import arrayToHTMLLine 

import MySQLdb
import datetime
import os
import math
def main():
  todaydate=datetime.date.today().strftime("%d%B%Y")
  db = MySQLdb.connect(host="localhost", user="root", passwd="ccmpProject**", db="libtech",charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  bid=165
  broadcastTable="""
     <html>
     <head>
     <style>
    table, th, td {
    border: 2px solid #097054;
    border-collapse: collapse;
    }
    table {
     margin-bottom: 20px
   }

    </style>
    </head>
     <body>
     <h1>Broadcast Reports</h1>
     <h3> <a href="/index.html">Go Back Home</a></h3>
     <table>
     <tr>
       <th>Broadcast ID</th>
       <th>Name</th>
       <th>Status</th>
       <th>startDate</th>
       <th>endDate</th>
       <th>TotalCalls</th>
       <th>Pending</th>
       <th>Success</th>
       <th>Failed</th>
       <th>Expired</th>
       <th>SuccessRate</th>
       <th>HitRate</th>
       <th>ReportLink</th>
      </tr>
      """
  #genBroadcastReport(cur,bid)
  #We need to get all the Broadcasts where processed=1 and Completed=0
  query="select bid,name,completed,DATE_FORMAT(startDate,'%d-%M-%Y'),DATE_FORMAT(endDate,'%d-%M-%Y') from Broadcasts where processed=1 order by bid desc"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=row[0]
    name=row[1]
    completed=row[2]
    startDate=row[3]
    endDate=row[4]
    query="select cid from ToCall where bid="+str(bid)
    cur.execute(query)
    pending=cur.rowcount
    query="select ccid from CompletedCalls where  bid="+str(bid)
    cur.execute(query)
    attempts=cur.rowcount
    query="select id from callStatus where success=1 and bid="+str(bid)
    cur.execute(query)
    success=cur.rowcount
    query="select id from callStatus where expired=1 and bid="+str(bid)
    cur.execute(query)
    expired=cur.rowcount
    query="select id from callStatus where maxRetryFail=1 and bid="+str(bid)
    cur.execute(query)
    maxRetryFail=cur.rowcount
    total=pending+success+expired+maxRetryFail
    successPercentage=0
    if(total >0):
      successPercentage=math.trunc(success*100/total)
    hitPercentage=0
    if(attempts >0):
      hitPercentage=math.trunc(success*100/attempts)
    reportLink='<a href="./'+str(bid)+'_'+name+'.csv">Report</a>'
    status="Incomplete"
    if(pending==0):
      status="Complete"
    tableArray=[bid,name,status,startDate,endDate,total,pending,success,maxRetryFail,expired,successPercentage,hitPercentage,reportLink]
    broadcastTable+=arrayToHTMLLine(tableArray)
 
    if (completed==0):
      genBroadcastReport(cur,bid,name)
      query="select cid from ToCall where bid="+str(bid)
      cur.execute(query)
      if(cur.rowcount == 0):
      #This means that there are no pending calls for this Broadcast 
        query="update Broadcasts set completed=1 where bid="+str(bid)
        cur.execute(query)
  #We need to get all the Broadcasts where processed=1 and Completed=0
   
  broadcastTable+="""
    </table></body></html>
  """
  htmlFile=open("/home/libtech/libtechweb/reports/broadcasts/index.html",'w')
  htmlFile.write(broadcastTable)

if __name__ == '__main__':
  main()
