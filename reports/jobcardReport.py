from reportFunctions import genBroadcastReport 
from reportFunctions import arrayToHTMLLine 
from reportFunctions import arrayToHTMLLineTh 
from reportFunctions import writejobcardcsv 
from reportFunctions import gethtmlfooter 
from reportFunctions import gethtmlheader 

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
  query="select stateCode,districtCode,blockCode,name from blocks where blockCode='003'"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    blockName=row[3]
    query="select name,panchayatCode,id from panchayats where Survey=1 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' limit 1"
    query="select name,panchayatCode,id,isSurvey from panchayats where stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
    cur.execute(query)
    panchresults = cur.fetchall()
    myhtml=gethtmlheader()
    myhtml+="<table>"
    tableArray=['Block Name','Panchayat Name','Total Jobcards','Total Workers','All Jobcard','Total No Account','Report NoAccount','Is Survey','TotalMusterReject','TotalftoReject','Rejected Payment Report','Download CSV']
    myhtml+=arrayToHTMLLineTh(tableArray)
    for panchrow in panchresults:
      panchayatName=panchrow[0]
      panchayatCode=panchrow[1]
      fullPanchayatCode=stateCode+districtCode+blockCode+panchayatCode
      panchID=panchrow[2]
      isSurvey=panchrow[3]
      query="select count(*) c from jobcardRegister where blockCode='"+str(blockCode)+"' and panchayatCode='"+str(panchayatCode)+"';"
      cur.execute(query)
      countrow=cur.fetchone()
      count=countrow[0]
      query="select count(*) c from jobcardDetails jd,jobcardRegister j where j.jobcard=jd.jobcard and j.blockCode='"+str(blockCode)+"' and j.panchayatCode='"+str(panchayatCode)+"';"
      cur.execute(query)
      countrow=cur.fetchone()
      countApplicants=countrow[0]
      query="select count(*) c from jobcardDetails jd,jobcardRegister j where jd.accountNo=0 and j.jobcard=jd.jobcard and j.blockCode='"+str(blockCode)+"' and j.panchayatCode='"+str(panchayatCode)+"';"
      cur.execute(query)
      countrow=cur.fetchone()
      countNoAccount=countrow[0]
      jobcardlike="CH-05-"+str(blockCode)+"-"+str(panchayatCode)+"-"
      query="select count(*) c from musterTransactionDetails where jobcard like '%"+jobcardlike+"%' and (status='Rejected' or status='InvalidAccount');"
      cur.execute(query)
      countrow=cur.fetchone()
      musterReject=''
      if (isSurvey == 1):
        musterReject=countrow[0]
      query="select count(*) c from ftoTransactionDetails where jobcard like '%"+jobcardlike+"%' and (status='Rejected' or status='InvalidAccount');"
      cur.execute(query)
      countrow=cur.fetchone()
      ftoReject=''
      if (isSurvey == 1):
        ftoReject=countrow[0]
      csvname='/chattisgarh/surguja/'+blockName.lower()+'/'+panchayatName.lower()+'_jobcards.csv'
      reportLink='<a href="'+csvname+'">Download</a>'
      alljobcardlink='<a href="./'+blockName.lower()+'/jc_html/'+panchayatName.lower()+'_jobcards.html">All Jobcards</a>'
      noaccountlink='<a href="./'+blockName.lower()+'/jc_html/'+panchayatName.lower()+'_jobcards_noAccount.html">No account</a>'
      rejectedlink='<a href="./'+blockName.lower()+'/jc_html/'+panchayatName.lower()+'_jobcards_rejected_payments.html">Rejected Payments</a>'
      tableArray=[blockName,panchayatName,str(count),str(countApplicants),alljobcardlink,countNoAccount,noaccountlink,isSurvey,musterReject,ftoReject,rejectedlink,reportLink]
      myhtml+=arrayToHTMLLine(tableArray)
      writejobcardcsv(cur,districtCode,districtName,blockCode,panchayatCode,blockName,panchayatName)
    myhtml+="</table>"
    myhtml+=gethtmlfooter()
    filename="/home/libtech/libtechweb/chattisgarh/surguja/"+blockName.lower()+".html"
    f=open(filename,"w")
    f.write(myhtml.encode("UTF-8"))
    f.close()
      #writejobcardcsv(cur,districtCode,districtName,blockCode,panchayatCode,blockName,panchayatName)
      #select jd.jobcard,j.headOfFamily,j.caste,j.issueDate,j.village,jd.applicantNo,jd.age,jd.applicantName,jd.gender,jd.accountNo from jobcardDetails jd,jobcardRegister j where j.jobcard=jd.jobcard limit 5;
if __name__ == '__main__':
  main()
