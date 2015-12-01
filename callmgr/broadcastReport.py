import MySQLdb
import math
import datetime
import os
import time
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token
import requests
import xml.etree.ElementTree as ET
import sys
import libtechFunctions
import globalSettings
from libtechFunctions import gethtmlheader 
from libtechFunctions import gethtmlfooter 
from libtechFunctions import singleRowQuery,arrayToHTMLLine,writecsv 
from globalSettings import broadcastsReportFile,broadcastReportFilePath

def updateBroadcastTable(cur,bid):
  query="select count(*) from callSummary where status='success' and bid="+str(bid)
  success=singleRowQuery(cur,query)
  query="select count(*) from callSummary where status='failMaxRetry' and bid="+str(bid)
  failMaxRetry=singleRowQuery(cur,query)
  query="select count(*) from callSummary where status='expired' and bid="+str(bid)
  expired=singleRowQuery(cur,query)
  query="select count(*) from callSummary where status='pending' and bid="+str(bid)
  pending=singleRowQuery(cur,query)  
  query="select sum(cost) from callLogs where bid="+str(bid)
  cost=singleRowQuery(cur,query)
  if cost == None:
    cost = 0
  else:
    cost = cost/100
  total=success+expired+failMaxRetry+pending
  successPercentage=0
  if (total > 0):
    successPercentage=math.trunc(success*100/total)
  print str(success)+"  "+str(failMaxRetry)+"  "+str(expired)+"  "+str(pending)+"  "+str(total)+"  "+str(cost)
  isComplete=0
  if(pending == 0):
   isComplete=1
  query="update broadcasts set successP='"+str(successPercentage)+"',completed="+str(isComplete)+",success="+str(success)+",cost="+str(cost)+",fail="+str(failMaxRetry)+",expired="+str(expired)+",pending="+str(pending)+",total="+str(total)+" where bid="+str(bid) 
  print query
  cur.execute(query)


def main():
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="select bid,completed,name from broadcasts where bid>1000 and error=0 and approved=1 order by bid DESC "
  print query
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=str(row[0])
    completed=str(row[1])
    name=row[2]
    print bid+"  "+name+"  "+completed
    query="select a.district,a.block,a.panchayat,c.phone,DATE_FORMAT(c.callStartTime,'%d-%M-%Y') callTime,c.status,c.attempts,c.duration,f.feedback,c.sid from addressbook a,callSummary c left join callFeedback f on c.sid=f.sid where c.phone=a.phone and bid="+str(bid)
    if(completed == '0'):
      csvname=broadcastReportFilePath+str(bid)+"_"+name.replace(' ',"")+".csv"
      print csvname
      writecsv(cur,query,csvname)
      updateBroadcastTable(cur,bid) 
# print "Printing Broadcast reports"
# myhtml=gethtmlheader()
# myhtml+="<h1>Summary of Broadcasts</h1>"
# myhtml+="<table>"
# tableArray=['Broadcast ID', 'Broadcast Name','Start Date','retry','Total','Pending','Success','Fail','Expired','Success %','Cost','Detail Report'] 
# myhtml+=arrayToHTMLLine('th',tableArray)
# print myhtml
# query="select bid,completed from broadcasts where bid>1000 and error=0 order by bid DESC"
# print query
# cur.execute(query)
# results = cur.fetchall()
# for row in results:
#   bid=row[0]
#   completed=row[1]
#   print "Current Bid is"+str(bid)
#   updateBroadcastTable(cur,bid)
#   minretry = ''
#   if (completed == 0):
#     query="select max(retry) from callQueue where bid="+str(bid)
#     cur.execute(query)
#     row1=cur.fetchone()
#     minretry=row1[0]
#   query="select name,DATE_FORMAT(startDate,'%d-%M-%Y'),total,pending,success,fail,expired,cost from broadcasts where bid="+str(bid)
#   cur.execute(query)
#   row1=cur.fetchone()
#   name=row1[0]
#   startDate=str(row1[1])
#   total=row1[2]
#   pending=str(row1[3])
#   success=row1[4]
#   fail=str(row1[5])
#   expired=str(row1[6])
#   cost=str(row1[7])
#   successPercentage=0
#   if (total > 0):
#     successPercentage=math.trunc(success*100/total)
#   reportLink='<a href="./'+str(bid)+'_'+name.strip()+'.csv">Download</a>'
#   tableArray=[bid,name,startDate,minretry,total,pending,success,fail,expired,successPercentage,cost,reportLink] 
#   myhtml+=arrayToHTMLLine('td',tableArray)
#   #write csv report
#   csvname=broadcastReportFilePath+str(bid)+"_"+name.strip()+".csv"
#   query="select phone,DATE_FORMAT(callStartTime,'%d-%M-%Y') callTime,status,attempts,duration from callSummary where bid="+str(bid)
#   query="select a.district,a.block,a.panchayat,c.phone,DATE_FORMAT(c.callStartTime,'%d-%M-%Y') callTime,c.status,c.attempts,c.duration,f.feedback,c.sid from addressbook a,callSummary c left join callFeedback f on c.sid=f.sid where c.phone=a.phone and bid="+str(bid)
#   if(completed == 0):
#     writecsv(cur,query,csvname)
# myhtml+="</table>"
# myhtml+=gethtmlfooter()
# filename="./ui/html/broadcastReports.html"
# f=open(broadcastsReportFile,"w")
# f.write(myhtml.encode("UTF-8"))


if __name__ == '__main__':
  main()
