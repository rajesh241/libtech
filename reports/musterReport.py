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
  query="select stateCode,districtCode,blockCode,name from blocks"
  query="select stateCode,districtCode,blockCode,name from blocks where blockCode='003'"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    blockName=row[3]
    query="select name,panchayatCode,id from panchayats where isSurvey=1 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
    #query="select name,panchayatCode,id from panchayats where stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
    cur.execute(query)
    panchresults = cur.fetchall()
    for panchrow in panchresults:
      panchayatName=panchrow[0]
      panchayatCode=panchrow[1]
      fullPanchayatCode=stateCode+districtCode+blockCode+panchayatCode
      panchID=panchrow[2]
      print blockName+"  "+panchayatName
      jobcardlike="CH-05-"+str(blockCode)+"-"+str(panchayatCode)+"-"
      query="select jobcard from musterTransactionDetails where jobcard like '%CH-05-002-033%' group by jobcard limit 1;"
      query="select jobcard from musterTransactionDetails where jobcard like '%"+jobcardlike+"%'group by jobcard "
      query="select jobcard from jobcardRegister where blockCode='"+str(blockCode)+"' and panchayatCode='"+str(panchayatCode)+"';"
      print query
      cur.execute(query)
      jcresults = cur.fetchall()
      for jc in jcresults:
        jobcard=jc[0]
        print jobcard
        myhtml=gethtmlheader()
        #myhtml+="<h2>Jobcard:"+jobcard+"</h2>"
        myhtml+="<h3>Job Card Details</h3>"
        myhtml+="<table>"
        tableArray=['block  ',blockName]
        myhtml+=arrayToHTMLLine(tableArray)
        tableArray=['panchayat  ',panchayatName]
        myhtml+=arrayToHTMLLine(tableArray)
        tableArray=['jobcard  ',jobcard]
        myhtml+=arrayToHTMLLine(tableArray)
        myhtml+="</table>"
       
        query="select headOfFamily,issueDate,fatherHusbandName,caste,village,isBPL,jobcard from jobcardRegister where jobcard='"+jobcard+"'"
        cur.execute(query)
        if(cur.rowcount == 1):
          jobcardrow=cur.fetchone()
          headOfFamily=jobcardrow[0]
          issueDate=str(jobcardrow[1])
          fatherHusbandName=jobcardrow[2]
          caste=jobcardrow[3]
          village=jobcardrow[4]
          BPL=str(jobcardrow[5])
          jobcard1=jobcardrow[6]
          #myhtml+="<h3>"+jobcard1+"</h3>"
          myhtml+="<table>"
          tableArray=['Head Of Family','issue Date','Father Husband Name','caste','village','BPL']
          myhtml+=arrayToHTMLLineTh(tableArray)
          tableArray=[headOfFamily,issueDate,fatherHusbandName,caste,village,BPL]
          myhtml+=arrayToHTMLLine(tableArray)
          myhtml+="</table>"
          myhtml+="<h3>Job Card Applicant Details</h3>"

        query="select applicantNo,applicantName,age,gender,accountNo,bankNameOrPOName from jobcardDetails where jobcard='"+jobcard+"'"
        cur.execute(query)
        if(cur.rowcount != 0):
          myhtml+="<table>"
          tableArray=['Applicant Name','Name','age','gender','accountNo','Bank Name']
          myhtml+=arrayToHTMLLineTh(tableArray)
          jdresults = cur.fetchall()
          for jd in jdresults:
            applicantNo=jd[0]
            applicantName=jd[1]
            age=str(jd[2])
            gender=jd[3]
            accountNo=str(jd[4])
            bankName=str(jd[5])
            tableArray=[applicantNo,applicantName,age,gender,accountNo,bankName]
            myhtml+=arrayToHTMLLine(tableArray)

          myhtml+="</table>"
     
        myhtml+="<h3>Muster Roll Details</h3>"
        myhtml+="<table>"
        tableArray=['MusterNo ','Name','WorkName','dateFrom','dateTo','Days Worked','Wage','accountNo','wagelistNo','status']
        myhtml+=arrayToHTMLLineTh(tableArray)
 
        query="select musterNo,name,daysWorked,totalWage,accountNo,wagelistNo,status from musterTransactionDetails where jobcard='"+jobcard+"' order by finyear,CAST(musterNo as UNSIGNED INTEGER)"
        #print query
        cur.execute(query)
        if(cur.rowcount > 0):
          myhtml+="<h3>Muster Roll Details</h3>"
          myhtml+="<table>"
          tableArray=['MusterNo ','Name','WorkName','dateFrom','dateTo','Days Worked','Wage','accountNo','wagelistNo','status']
          myhtml+=arrayToHTMLLineTh(tableArray)
          mtresults = cur.fetchall()
          for mt in mtresults:
            musterNo=str(mt[0])
            name=mt[1]
            daysWorked=str(mt[2])
            totalWage=str(mt[3])
            accountNo=str(mt[4])
            wagelistNo=str(mt[5])
            status=str(mt[6])
            query="select workName,DATE_FORMAT(dateFrom,'%d-%M-%Y'),DATE_FORMAT(dateTo,'%d-%M-%Y') from musters where musterNo="+musterNo
            cur.execute(query)
            musterrow=cur.fetchone()
            workName=musterrow[0]
            dateFrom=str(musterrow[1])
            dateTo=str(musterrow[2])
            tableArray=[musterNo,name,workName,dateFrom,dateTo,daysWorked,totalWage,accountNo,wagelistNo,status]
            myhtml+=arrayToHTMLLine(tableArray)
          myhtml+="</table>"

        query="select ftoNo,applicantName,primaryAccountHolder,DATE_FORMAT(processedDate,'%d-%M-%Y'),accountNo,creditedAmount,status,rejectionReason,wagelistNo from ftoTransactionDetails where jobcard='"+jobcard+"' order by processedDate";
        cur.execute(query)
        if(cur.rowcount > 0):
          myhtml+="<h3>FTO Transaction Detail</h3>"
          myhtml+="<table>"
          tableArray=['FTONo ','Processed Date','Name','Primary Account Holder','Account No','Amount','status','Rejection Reason','wagelistNo']
          myhtml+=arrayToHTMLLineTh(tableArray)
          ftresults = cur.fetchall()
          for ft in ftresults:
            ftoNo=ft[0]
            name=ft[1]
            primaryAccountHolder=ft[2]
            processedDate=ft[3]
            accountNo=ft[4]
            amount=ft[5]
            status=ft[6]
            rejectionReason=ft[7]
            wagelistNo=ft[8]
            tableArray=[ftoNo,processedDate,name,primaryAccountHolder,accountNo,amount,status,rejectionReason,wagelistNo]
            myhtml+=arrayToHTMLLine(tableArray)
          myhtml+="</table>"

        myhtml+=gethtmlfooter()
        htmlFileName="/home/libtech/libtechweb/chattisgarh/surguja/"+blockName.lower()+"/"+panchayatName.lower()+"/"+jobcard.replace("/","_")+".html"
        if not os.path.exists(os.path.dirname(htmlFileName)):
          os.makedirs(os.path.dirname(htmlFileName))
        f=open(htmlFileName,"w")
        f.write(myhtml.encode("UTF-8"))
        f.close()

if __name__ == '__main__':
  main()
