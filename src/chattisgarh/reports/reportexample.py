from printexcel import querytoexcel
import MySQLdb


def main():
  print "Printing from main"
  db = MySQLdb.connect(host="localhost", user="root", passwd="golani123", db="surguja",charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  query="use surguja"  
  cur.execute(query)
  query="select name,blockCode from blocks where isActive=1"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    print row[0]
    blockName=row[0]
    blockCode=row[1]
    filepath='/Users/goli/work/stan/chattisgarh/reports/noAccounts_jan2015/'+blockName+"/"
    query="select name,panchayatCode from panchayats where blockCode='"+blockCode+"' ;"
    cur.execute(query)
    results1 = cur.fetchall()
    for row1 in results1:
      panchayatCode=row1[1]
      panchayatName=row1[0]
      filename=panchayatName+".xlsx"
      query="select b.name block,p.name panchayat,jc.village,j.jobcard,jc.headOfFamily,jc.caste,jc.issueDate,j.applicantName,j.gender,j.age from jobcardDetails j,blocks b,jobcardRegister jc,panchayats p where j.jobcard=jc.jobcard and jc.panchayatCode=p.panchayatCode and jc.blockCode=p.blockCode and jc.blockCode=b.blockCode and j.accountNo=0 and jc.panchayatCode='"+panchayatCode+"' and jc.blockCode='"+blockCode+"' "
      querytoexcel(filepath,filename,query,"surguja")


if __name__ == '__main__':
  main()
