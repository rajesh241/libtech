from bs4 import BeautifulSoup
import multiprocessing, time
import requests
import MySQLdb
import os
import os.path
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
import datetime
from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from crawlSettings import nregaDB 
from crawlSettings import nregaWebDir,nregaRawDataDir
from crawlFunctions import alterHTMLTables,writeFile,getjcNumber,NICToSQLDate,getFullFinYear
regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
regex1=re.compile(r'</td></font></td>',re.DOTALL)
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-b', '--blockCode', help='BlockCode for  which you need to Download', required=False)
  parser.add_argument('-p', '--panchayatCode', help='panchayatCode for  which you need to Download', required=False)
  parser.add_argument('-mid', '--musterID', help='Muster Id that needs to be downloaded', required=False)
  parser.add_argument('-n', '--maxProcess', help='No of Simultaneous Process to Run', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args

class musterProcess(multiprocessing.Process):
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.pyConn = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
        #self.pyConn.set_isolation_level(0)
        self.pyConn.autocommit(True)


    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                self.task_queue.task_done()
                dbFinalize(self.pyConn) # Make sure you put this if there are other exit paths or errors
                break            
            answer = next_task(connection=self.pyConn)
            self.task_queue.task_done()
            self.result_queue.put(answer)
        return

class Task(object):
  def __init__(self, a):
    self.a = a
  def __call__(self,connection=None):
    pyConn = connection
    pyCursor1 = pyConn.cursor()
    myLog = downloadMuster(pyCursor1,self.a)
    return myLog

def updatePaymentDate(cur,mid,orightml):
  htmlsoup=BeautifulSoup(orightml,"html.parser")
  
  paymentTD=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lblPayDate")
  paymentDateString=paymentTD.text
  paymentDate=NICToSQLDate(paymentDateString)
  query="update musters set paymentDate=%s where id=%s " % (paymentDate,str(mid))
  myLog="Update Payment Date QUery %s \n" %query
  cur.execute(query)
  return myLog
def getWDID(cur,finyear,fullBlockCode,musterNo,musterIndex,isAltered):
  wdID=None
  myLog=''
  doInsert=0
  whereClause="where finyear='%s' and fullBlockCode='%s' and musterNo='%s' and musterIndex='%s' and isArchive=0" % (finyear,fullBlockCode,musterNo,musterIndex)
  query="select id from workDetails %s " % whereClause
  cur.execute(query)
  if cur.rowcount == 0:
    doInsert=1
  elif (isAltered == 1):
    doInsert=1
    query="update workDetails set isArchive=1 %s " %whereClause
    cur.execute(query)
  if doInsert == 1:
    query="insert into workDetails (finyear,fullBlockCode,musterNo,musterIndex) values ('%s','%s','%s','%s')" % (finyear,fullBlockCode,musterNo,musterIndex)
    myLog+="Insert Query %s \n" % query 
    cur.execute(query)
    query="select id from workDetails %s " % whereClause
    cur.execute(query)
    row=cur.fetchone()
    wdID=row[0]
    myLog+="New work Details ID : %s \n" % str(wdID) 
  return wdID,myLog


def updateWageLists(cur,wagelistArray,stateCode,districtCode,blockCode,finyear):
  fullBlockCode=stateCode+districtCode+blockCode
  for wagelistNo in set(wagelistArray):
    whereClause="where finyear='%s' and fullBlockCode='%s' and wagelistNo='%s'" % (finyear,fullBlockCode,wagelistNo)
    query="select * from wagelists %s " % whereClause
    cur.execute(query)
    if cur.rowcount == 0:
      query="insert into wagelists (finyear,fullBlockCode,wagelistNo,stateCode,districtCode,blockCode) values ('%s','%s','%s','%s','%s','%s')" % (finyear,fullBlockCode,wagelistNo,stateCode,districtCode,blockCode)
      cur.execute(query)


def updateWorkDetails(cur,mid,myhtml,updateMode,diffArray):
  myLog=''
  query="select p.stateName,p.districtName,p.blockName,p.panchayatName,p.stateCode,p.districtCode,p.blockCode,p.panchayatCode,p.stateShortCode,m.fullBlockCode,m.musterNo,m.workName,DATE_FORMAT(m.dateFrom,'%d/%m/%Y'),DATE_FORMAT(m.dateTo,'%d/%m/%Y'),workCode,m.finyear,DATE_FORMAT(m.paymentDate,'%d/%m/%Y') from musters m,panchayats p where m.stateCode=p.stateCode and p.districtCode=m.districtCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and m.id= "+ str(mid)
  cur.execute(query)
  row=cur.fetchone()
  [stateName,districtName,blockName,panchayatName,stateCode,districtCode,blockCode,panchayatCode,stateShortCode,fullBlockCode,musterNo,workName,dateFromString,dateToString,workCode,finyear,paymentDateString] = row

  reMatchString="%s-%s-" % (stateShortCode,districtCode)
  wagelistArray=[]
  bs1 = BeautifulSoup(myhtml, "html.parser")
  mytable=bs1.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
  tr_list = mytable.findAll('tr')
  if updateMode=="create":
    for i in range(len(tr_list)):
      diffArray.append(i)
  myLog+="diffAray is %s "% str(diffArray)
  for tr in tr_list: #This loop is to find staus Index
    cols = tr.findAll('th')
    if len(cols) > 7:
      i=0
      while i < len(cols):
        value="".join(cols[i].text.split())
        if "Status" in value:
          statusindex=i
        i=i+1
  isComplete=1
  for i in range(len(tr_list)):
    cols=tr_list[i].findAll("td")
    if len(cols) > 7:
      nameandjobcard=cols[1].text.lstrip().rstrip()
      if stateShortCode in nameandjobcard:
        status=cols[statusindex].text.lstrip().rstrip()
        if status != 'Credited':
          isComplete=0      
        if i in diffArray:
          musterIndex=cols[0].text.lstrip().rstrip()
          nameandjobcard=cols[1].text.lstrip().rstrip()
          aadharNo=cols[2].text.strip().lstrip().rstrip()
          nameandjobcard=nameandjobcard.replace('\n',' ')
          nameandjobcard=nameandjobcard.replace("\\","")
          nameandjobcardarray=re.match(r'(.*)'+reMatchString+'(.*)',nameandjobcard)
          name=nameandjobcardarray.groups()[0]
          jobcard=reMatchString+nameandjobcardarray.groups()[1]
          jcNumber=getjcNumber(jobcard)
          totalWage=cols[statusindex-6].text.lstrip().rstrip()
          dayWage=cols[statusindex-10].text.lstrip().rstrip()
          accountNo=cols[statusindex-5].text.lstrip().rstrip()
          daysWorked=cols[statusindex-11].text.lstrip().rstrip()
          bankNamePostOffice=cols[statusindex-4].text.lstrip().rstrip()
          branchNamePostOfficeCode=cols[statusindex-3].text.lstrip().rstrip()
          branchCodePostOfficeAddress=cols[statusindex-2].text.lstrip().rstrip()
          wagelistNo=cols[statusindex-1].text.lstrip().rstrip()
          wagelistArray.append(wagelistNo)
          creditedDateString=cols[statusindex+1].text.lstrip().rstrip()
          creditedDate=NICToSQLDate(creditedDateString)
          dateFrom=NICToSQLDate(dateFromString)
          dateTo=NICToSQLDate(dateToString)
          paymentDate=NICToSQLDate(paymentDateString)
          if i in diffArray:
            isAltered=1
          else:
            isAltered=0 
          #Here we need to reate a record if it does not exists
          wdID,wdIDLog=getWDID(cur,finyear,fullBlockCode,musterNo,musterIndex,isAltered)
          myLog+=wdIDLog
          if wdID is not None:
            query="update workDetails set updateDate=NOW(),stateCode='%s',districtCode='%s',blockCode='%s',panchayatCode='%s',stateName='%s',districtName='%s',blockName='%s',panchayatName='%s',workCode='%s',workName='%s',name='%s',aadharNo='%s',jobcard='%s',jcNumber='%s',daysWorked='%s',dayWage='%s',totalWage='%s',accountNo='%s',wagelistNo='%s',musterStatus='%s',bankNamePostOffice='%s',branchNamePostOfficeCode='%s',branchCodePostOfficeAddress='%s',dateFrom=%s,dateTo=%s,paymentDate=%s,creditedDate=%s where id=%s" % (stateCode,districtCode,blockCode,panchayatCode,stateName,districtName,blockName,panchayatName,workCode,workName,name,aadharNo,jobcard,str(jcNumber),str(daysWorked),str(dayWage),str(totalWage),accountNo,wagelistNo,status,bankNamePostOffice,branchNamePostOfficeCode,branchCodePostOfficeAddress,dateFrom,dateTo,paymentDate,creditedDate,str(wdID))
            cur.execute(query)

  updateWageLists(cur,wagelistArray,stateCode,districtCode,blockCode,finyear)
  query="update musters set isDownloaded=1,downloadDate=NOW(),wdProcessed=1,wdComplete=%s where id=%s " % (str(isComplete),str(mid))
  myLog+="Muster Update Query %s \n" %query
  cur.execute(query)
  return myLog

def getDiff(html1,html2):
  myLog="Starting to do the Difference"
  bs1 = BeautifulSoup(html1.replace('\r',''), "html.parser")
  bs2 = BeautifulSoup(html2.decode("UTF-8").replace('\r',''), "html.parser")
  table1=bs1.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
  table2=bs2.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
  tr_list1 = table1.findAll('tr')
  tr_list2 = table2.findAll('tr')
  diffArray=[]
  s1=''
  s2=''
  print("The length of array is %s " % str(len(tr_list1)))
  for i in range(len(tr_list1)):
    print("value of is is %d" % i)
    tr1 = tr_list1[i]
    tr2 = tr_list2[i]
    if (tr1 != tr2 ):
      s1+=str(tr1)
      s2+=str(tr2)
      myLog+="NOT SAME row[%d] " %(i)
      diffArray.append(i)
    else:
      myLog+="same row[%d]" %(i)
  with open('/tmp/s1.txt', 'wb') as outfile:
    outfile.write(s1.encode("UTF-8"))
  with open('/tmp/s2.txt', 'wb') as outfile:
    outfile.write(s2.encode("UTF-8"))
  return diffArray,myLog

def downloadMuster(cur,mid):
  myLog=''
  myLog+="Download Muster ID %s \n" % str(mid)
  query="select fullBlockCode,panchayatCode,musterNo,workName,DATE_FORMAT(dateFrom,'%d/%m/%Y'),DATE_FORMAT(dateTo,'%d/%m/%Y'),workCode,finyear from musters where id="+str(mid)
  cur.execute(query)
  row=cur.fetchone()
  fullPanchayatCode=row[0]+row[1]
  fullBlockCode=row[0]
  panchayatCode=row[1]
  musterNo=str(row[2])
  workName=row[3].replace(" ","+")
  dateFrom=str(row[4])
  dateTo=str(row[5])
  workCode=row[6]
  fullFinYear=getFullFinYear(row[7]) 
  query="select crawlIP,stateName,rawDistrictName,rawBlockName,rawPanchayatName,stateShortCode,stateCode,districtCode,blockCode,panchayatName from panchayats where fullPanchayatCode='%s'" % (fullPanchayatCode)
  print(query)
  cur.execute(query)
  row=cur.fetchone()
  crawlIP=row[0]
  stateName=row[1]
  districtName=row[2]
  blockName=row[3]
  panchayatName=row[4] 
  stateShortCode=row[5]
  stateCode=row[6]
  districtCode=row[7]
  blockCode=row[8]
  panchayatNameAltered=row[9]
  jobcardPrefix="%s-%s-%s" % (stateShortCode,districtCode,blockCode)

  musterURL="http://%s/netnrega/citizen_html/musternew.aspx?state_name=%s&district_name=%s&block_name=%s&panchayat_name=%s&workcode=%s&panchayat_code=%s&msrno=%s&finyear=%s&dtfrm=%s&dtto=%s&wn=%s&id=1" % (crawlIP,stateName.upper(),districtName.upper(),blockName.upper(),panchayatName,workCode,fullPanchayatCode,musterNo,fullFinYear,dateFrom,dateTo,workName)
  myLog+="%s\n" % musterURL
  try:
    r=requests.get(musterURL)
    #Irrespective of result of download lets set downloadAttemptDate
    query="update musters set downloadAttemptDate=NOW() where id="+str(mid)
    cur.execute(query)
    
    mustersource=r.text
    myhtml=mustersource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    
    myhtml=re.sub(regex,"",myhtml)
    myhtml=re.sub(regex1,"</font></td>",myhtml)
    downloadError=0
    myLog+="Muster Downloaded SuccessFully\n"
  except:
    downloadError=1
  if (downloadError==0) and (jobcardPrefix in myhtml):
    myLog+="Muster Detail table found in Muster HTML\n"
    title="Muster No : %s,  %s-%s-%s " % (str(musterNo),districtName,blockName,panchayatName)
    orightml=myhtml
    tableIDs=["ctl00_ContentPlaceHolder1_grdShowRecords"]
    myhtml=alterHTMLTables(myhtml,title,tableIDs)
    modifiedMusterFilePath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
    fileName=modifiedMusterFilePath+blockName.upper()+"/MUSTERS/"+fullFinYear+"/"+musterNo+".html"
    archiveMusterFilePath=nregaRawDataDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
    curDate=time.strftime("%d%b%Y")
    archiveFileName=archiveMusterFilePath+blockName.upper()+"/MUSTERS/"+fullFinYear+"/"+musterNo+"_"+curDate+"_orig.html"
    archiveFileNameModified=archiveMusterFilePath+blockName.upper()+"/MUSTERS/"+fullFinYear+"/"+musterNo+"_"+curDate+".html"
    myLog+="fileName %s \n" % fileName
    fileExists=0
    updateMode="create"
    if (os.path.isfile(fileName)):
      fileExists=1
      updateMode="edit"

    #Here we will see if we do need to write the New File or Not
    if fileExists==0:
      doFileWrite=1
      diffArray=[]
    else:
      #Here we will read the old html and see if anything has changed
      f=open(fileName,"rb")
      oldhtml=f.read()
      f.close()
      diffArray,diffLog=getDiff(myhtml,oldhtml)
      myLog+=diffLog
      if len(diffArray) == 0:
        doFileWrite=0
      else:
        doFileWrite=1
    myLog+="Value of File Write is  %s \n" % str(doFileWrite)
    if doFileWrite == 1:
      try:
        writeFile(archiveFileName,orightml) 
        writeFile(archiveFileNameModified,myhtml)
        error=0
      except:
        error=1
        myLog+="Unable to Write File"
      if error==0:
        myLog+="Write File SuccessFul"
        myLog+=updatePaymentDate(cur,mid,orightml)
        updateMode="create"
        diffArray=[]
        myLog+=updateWorkDetails(cur,mid,myhtml,updateMode,diffArray)
        writeFile(fileName,myhtml)

    #Here we will see if we do need to write the New File or Not2 
    
  return myLog

def main():
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  args = argsFetch()
  finyear=args['finyear']
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =50000
  if args['musterID']:
    mid=args['musterID']
  else:
    mid=None
  if args['maxProcess']:
    maxProcess=int(args['maxProcess'])
  else:
    maxProcess=1
  additionalFilters=''
  if args['district']:
    additionalFilters+= " and b.districtName='%s' " % args['district']
  fullfinyear=getFullFinYear(finyear)
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")


  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  tasks = multiprocessing.JoinableQueue()
  results = multiprocessing.Queue()
  myProcesses=[musterProcess(tasks, results) for i in range(maxProcess)]
  for eachProcess in myProcesses:
    eachProcess.start()
  if mid is None:
    query="select m.id from musters m,blocks b where m.fullBlockCode=b.fullBlockCode and m.finyear='%s' and (m.isDownloaded=0  or (m.wdComplete=0 and TIMESTAMPDIFF(HOUR, m.downloadAttemptDate, now()) > 48 )) %s order by isDownloaded,m.downloadAttemptDate limit %s" % (finyear,additionalFilters,str(limit))
  else:
    query="select m.id from musters m where m.id=%s " % str(mid)
  logger.info(query) 
  cur.execute(query)
  noOfTasks=cur.rowcount
  results1=cur.fetchall()
  for row in results1:
    musterID=row[0]
    tasks.put(Task(musterID))  
  
  for i in range(maxProcess):
    tasks.put(None)

  while noOfTasks:
    result = results.get()
    logger.info(result)
    noOfTasks -= 1


  dbFinalize(db) # Make sure you put this if there are other exit paths or errors

if __name__ == '__main__':
  main()

