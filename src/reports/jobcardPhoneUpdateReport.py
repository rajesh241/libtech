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
  db = MySQLdb.connect(host="localhost", user="root", passwd="ccmpProject**", db="surguja",charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  districtName="SURGUJA"
  #Query to get all the blocks
  query="select stateCode,districtCode,blockCode,name from blocks where isActive=1"
  #query="select stateCode,districtCode,blockCode,name from blocks where blockCode='005'"
  #query="select stateCode,districtCode,blockCode,name from blocks where blockCode='003'"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    blockName=row[3]
    query="select name,panchayatCode,id from panchayats where Survey=1 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' limit 1"
    query="select name,panchayatCode,id,isSurvey from panchayats where isSurvey=1 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
    cur.execute(query)
    panchresults = cur.fetchall()
    myhtml=gethtmlheader()
    myhtml+="<table>"
    tableArray=['Block Name','Panchayat Name','Total Jobcards','Total Workers','Update Numbers']
    myhtml+=arrayToHTMLLineTh(tableArray)
    for panchrow in panchresults:
      panchayatName=panchrow[0]
      panchayatCode=panchrow[1]
      fullPanchayatCode=stateCode+districtCode+blockCode+panchayatCode
      panchID=panchrow[2]
      isSurvey=panchrow[3]
      print blockName+"  "+panchayatName
      count=getcountquery(cur,"select count(*) c from jobcardRegister where blockCode='"+str(blockCode)+"' and panchayatCode='"+str(panchayatCode)+"';")
      countApplicants=getcountquery(cur,"select count(*) c from jobcardDetails jd,jobcardRegister j where j.jobcard=jd.jobcard and j.blockCode='"+str(blockCode)+"' and j.panchayatCode='"+str(panchayatCode)+"';")
      panchhtmlname=panchayatName.lower()+"_phoneEntry.html"
      reportLink='<a href="./'+panchhtmlname+'">View Detail</a>'
      tableArray=[blockName,panchayatName,str(count),str(countApplicants),reportLink]
      myhtml+=arrayToHTMLLine(tableArray)
      panchhtml=gethtmlheader()
      panchhtml+="<h1> Block:"+blockName+"  Panchayat: "+panchayatName+"</h1>"
      panchhtml+="<table>"
      tableArray=["Job Card","Update","Head of Family","Father Husband Name","All Names"]
      panchhtml+=arrayToHTMLLineTh(tableArray)
      query="select jobcard,headOfFamily,fatherHusbandName from jobcardRegister where blockCode='"+str(blockCode)+"' and panchayatCode='"+str(panchayatCode)+"';"
      cur.execute(query)
      jcresults = cur.fetchall()
      for jc in jcresults:
        jobcard=jc[0]
        headOfFamily=jc[1]
        relationName=jc[2]
        allFamily=''
        allFamily=getcountquery(cur,"select GROUP_CONCAT(applicantName SEPARATOR '    ') from jobcardDetails  where jobcard='"+jobcard+"' ;")
        #headOfFamily=''
        #relationName=''
        updateURL="../../../phpscripts/phoneUpdate.php?block="+blockName.lower()+"&panchayat="+panchayatName.lower()+"&jobcard="+jobcard
        updateLink='<a href="'+updateURL+'"> Update Phone Number</a>'
        tableArray=[jobcard,updateLink,headOfFamily,relationName,allFamily]
        panchhtml+=arrayToHTMLLine(tableArray)


      panchhtml+="</table>"
      panchhtml+=gethtmlfooter()
      filename="/home/libtech/libtechweb/chattisgarh/chaupalrsync/html/surguja/"+blockName.lower()+"/reports/"+panchhtmlname
      f=open(filename,"w")
      f.write(panchhtml.encode("UTF-8"))
      f.close()

    myhtml+="</table>"
    myhtml+=gethtmlfooter()
    filename="/home/libtech/libtechweb/chattisgarh/surguja/"+blockName.lower()+".html"
    filename="/home/libtech/libtechweb/chattisgarh/chaupalrsync/html/surguja/"+blockName.lower()+"/reports/allPanchayats.html"
    f=open(filename,"w")
    f.write(myhtml.encode("UTF-8"))
    f.close()
if __name__ == '__main__':
  main()
