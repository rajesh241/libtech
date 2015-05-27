
from reportFunctions import genBroadcastReport 
from reportFunctions import arrayToHTMLLine 
from reportFunctions import arrayToHTMLLineTh 
from reportFunctions import writejobcardcsv 
from reportFunctions import gethtmlfooter 
from reportFunctions import gethtmlheader 
from reportFunctions import gen2colTable 
from reportFunctions import gen2colOptions 
from reportFunctions import getcountquery 

import MySQLdb
import datetime
import os


def main():
  todaydate=datetime.date.today().strftime("%d%B%Y")
  db = MySQLdb.connect(host="localhost", user="root", passwd="ccmpProject**", db="chaupal",charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)

  statushtml=gethtmlheader()
  statushtml+="<h1>Jobcard Applications</h1>"
  total=getcountquery(cur,"select count(*) from jobcardApplications")
  pending=getcountquery(cur,"select count(*) from jobcardApplications where status='pending'")
  accepted=getcountquery(cur,"select count(*) from jobcardApplications where status='accepted'")
  rejected=getcountquery(cur,"select count(*) from jobcardApplications where status='rejected'")
  statushtml+="<h3>Summary</h3>"
  statushtml+="<table>"
  tableArray=['Total','Pending','Accepted','Rejected']
  statushtml+=arrayToHTMLLineTh(tableArray)
  tableArray=[total,pending,accepted,rejected]
  statushtml+=arrayToHTMLLine(tableArray)
  statushtml+="</table>"
  statushtml+="<h3>Details</h3>"
  statushtml+="<table>"
  tableArray=['ID','Block Name','Panchayat Name','Applicant Name','Father Husband Name','Application Date','Remarks','status','update']
  statushtml+=arrayToHTMLLineTh(tableArray)
  query="select id,block,panchayat,applicantName,relationName,DATE_FORMAT(applicationDate,'%d-%M-%Y'),remarks,status from jobcardApplications order by panchayat"
  headers=['id','block','panchayat','applicantName','relationName','ApplicationDate','remarks']
  headerfixed=[1,1,1,1,1,1,0]
  statusOptions=['pending','accepted','rejected','error']
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    id=str(row[0])
    block=row[1]
    panchayat=row[2]
    status=row[7]
    htmlname=block+"_"+panchayat+"_"+id+".html"
    updateLink='<a href="./../jobcardApplications/'+htmlname+'">update</a>'
    print id+" "+block+" "+panchayat
    myhtml=gethtmlheader()
    myhtml+='<form action="./../submit.php" method="POST">'
    myhtml+='<input name="formType" value="newJobcardApplicationUpdate" type="hidden"></input>'
    myhtml+='<input name="id" value="'+id+'" type="hidden"></input>'
    myhtml+="<table>"
    myhtml+=gen2colTable(headers,headerfixed,row)
    myhtml+=gen2colOptions('Change Status','status',statusOptions,status)
    myhtml+='<tr><td colspan="2" align="center"><button type="submit">Submit</button></td></tr>'
    myhtml+="</table>"
    myhtml+=gethtmlfooter()
    filename="/home/libtech/libtechweb/chattisgarh/chaupalrsync/html/jobcardApplications/"+block+"_"+panchayat+"_"+id+".html"
    f=open(filename,"w")
    f.write(myhtml.encode("UTF-8"))
    tableArray=[row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],updateLink]
    statushtml+=arrayToHTMLLine(tableArray)
    query="update jobcardApplications set htmlgen=1 where id="+id
    cur.execute(query)
  statushtml+="</table>"
  statushtml+=gethtmlfooter()
  filename="/home/libtech/libtechweb/chattisgarh/chaupalrsync/html/overview/jobcardApplicationStatus.html"
  f=open(filename,"w")
  f.write(statushtml.encode("UTF-8"))
    
      


if __name__ == '__main__':
  main()
