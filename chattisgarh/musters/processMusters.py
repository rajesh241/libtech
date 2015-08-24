import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
import os.path
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token
from globalSettings import datadir

#It has two </td> Tags in HTML 
regex=re.compile(r'</td></font></td>',re.DOTALL)
#Error File Defination
errorfile = open('/tmp/processMusters.log', 'a')
testfile = open('/tmp/f.html', 'w')
#File Path where all the Downloaded FTOs would be placed
districtName="SURGUJA"
musterfilepath=datadir+"/CHATTISGARH/"+districtName+"/"
#Connect to MySQL Database
db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db="surguja",charset='utf8')
cur=db.cursor()
db.autocommit(True)
#Query to set up Database to read Hindi Characters
query="SET NAMES utf8"
cur.execute(query)

#inblock=sys.argv[1]
#print inblock
#Query to get the Musters 
query=" select m.id,m.finyear,m.musterNo,p.name,b.name,m.workCode from musters m,blocks b,panchayats p where m.isDownloaded=1 and m.isProcessed=0 and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and m.blockCode='002' limit 1;"
query=" select m.id,m.finyear,m.musterNo,p.name,b.name,m.workCode,m.blockCode,p.panchayatCode from musters m,blocks b,panchayats p where m.isError=0 and m.isDownloaded=1 and m.isProcessed=0  and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and m.finyear='16' ;"
#query=" select m.id,m.finyear,m.musterNo,p.name,b.name,m.workCode from musters m,blocks b,panchayats p where m.isDownloaded=1 and m.isProcessed=0  and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and m.finyear='16' and m.musterNo=1296"
cur.execute(query)
if cur.rowcount:
  results = cur.fetchall()
  for row in results:
    musterID=row[0]
    musterNo=row[2]
    blockName=row[4]
    panchayatName=row[3].upper()
    finyear=row[1]
    workCode=row[5]
    blockCode=row[6]
    panchayatCode=row[7]
    if finyear=='16':
      fullfinyear='2015-2016'
    elif finyear=='15':
      fullfinyear='2014-2015'
    else:
      fullfinyear='2013-2014'
    print str(musterID)+"  "+fullfinyear+"  "+musterNo+"  "+blockName+"  "+panchayatName
    musterfilename=musterfilepath+blockName+"/"+panchayatName+"/MUSTERS/"+fullfinyear+"/"+musterNo+".html"
    print musterfilename 
    if (os.path.isfile(musterfilename)): 
      musterhtml1=open(musterfilename,'r').read()
      musterhtml=re.sub(regex,"</font></td>",musterhtml1)
    else:
      musterhtml="Timeout expired"
    #testfile.write(musterhtml)
    if "Timeout expired" in musterhtml:
      print "This is time out expired file"
      errorflag=1
      query="update musters set isError=1 where id="+str(musterID)
      cur.execute(query)
    else:
      htmlsoup=BeautifulSoup(musterhtml)
      try:
        table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
        rows = table.findAll('tr')
        errorflag=0
      except:
        errorflag=1
        query="update musters set isError=1 where id="+str(musterID)
        cur.execute(query)
    if errorflag==0:
      for tr in rows:
        #print "Looking at rows will look for th now"
        cols = tr.findAll('th')
        #print "the length of columns is "+str(len(cols))
        if len(cols) > 7:
          i=0
          while i < len(cols):
            value="".join(cols[i].text.split())
            if "Status" in value:
              statusindex=i
              #print "Status Index is "+str(statusindex) 
            i=i+1
      iscomplete=1
      for tr in rows:
        #print "Looking at rows will look for td now"
        cols = tr.findAll('td')
        #print "the length of columns is "+str(len(cols))
        if len(cols) > 7:
          musterIndex="".join(cols[0].text.split())
          nameandjobcard="".join(cols[1].text.split())
          if nameandjobcard!='':
            totalWage="".join(cols[statusindex-6].text.split())
            dayWage="".join(cols[statusindex-10].text.split())
            status="".join(cols[statusindex].text.split())
            accountNo="".join(cols[statusindex-5].text.split())
            daysWorked="".join(cols[statusindex-11].text.split())
            bankNameOrPOName="".join(cols[statusindex-4].text.split())
            branchNameOrPOAddress="".join(cols[statusindex-3].text.split())
            branchCodeOrPOCode="".join(cols[statusindex-2].text.split())
            wagelistNo="".join(cols[statusindex-1].text.split())
            creditedDatestring="".join(cols[statusindex+1].text.split())
            nameandjobcardarray=re.match(r'(.*)CH-05-(.*)',nameandjobcard)
            name=nameandjobcardarray.groups()[0]
            jobcard='CH-05-'+nameandjobcardarray.groups()[1]
            #print str(musterIndex)+"  "+name+"  "+jobcard
            print str(musterIndex)+" "+jobcard
            if status != 'Credited':
              iscomplete=0
            if creditedDatestring != '':
              creditedDate = time.strptime(creditedDatestring, '%d/%m/%Y')
              creditedDate = time.strftime('%Y-%m-%d %H:%M:%S', creditedDate)
              query="insert into musterTransactionDetails (musterNo,finyear,workCode,musterIndex,name,jobcard,daysWorked,dayWage,totalWage,accountNo,bankNameOrPOName,branchNameOrPOAddress,branchCodeOrPOCode,wagelistNo,status,creditedDate) values ('"+musterNo+"','"+finyear+"','"+workCode+"',"+str(musterIndex)+",'"+name+"','"+jobcard+"',"+str(daysWorked)+","+str(dayWage)+","+str(totalWage)+",'"+str(accountNo)+"','"+bankNameOrPOName+"','"+branchNameOrPOAddress+"','"+branchCodeOrPOCode+"','"+wagelistNo+"','"+status+"','"+creditedDate+"')"
              creditedDateQueryString="creditedDate='%s'" %creditedDate
            else:
              query="insert into musterTransactionDetails (musterNo,finyear,workCode,musterIndex,name,jobcard,daysWorked,dayWage,totalWage,accountNo,bankNameOrPOName,branchNameOrPOAddress,branchCodeOrPOCode,wagelistNo,status,creditedDate) values ('"+musterNo+"','"+finyear+"','"+workCode+"',"+str(musterIndex)+",'"+name+"','"+jobcard+"',"+str(daysWorked)+","+str(dayWage)+","+str(totalWage)+",'"+str(accountNo)+"','"+bankNameOrPOName+"','"+branchNameOrPOAddress+"','"+branchCodeOrPOCode+"','"+wagelistNo+"','"+status+"',NULL)"
              creditedDateQueryString="creditedDate=NULL"

            query1="update musterTransactionDetails set daysWorked=%s,dayWage=%s,totalWage=%s,accountNo='%s',bankNameOrPOName='%s',branchNameOrPOAddress='%s',branchCodeOrPOCode='%s',wagelistNo='%s',status='%s',blockCode='%s',panchayatCode='%s',%s where  musterNo=%s and jobcard='%s' and musterIndex=%s and finyear='%s'" %(str(daysWorked),str(dayWage),str(totalWage),str(accountNo),bankNameOrPOName,branchNameOrPOAddress,branchCodeOrPOCode,wagelistNo,status,blockCode,panchayatCode,creditedDateQueryString,str(musterNo),jobcard,str(musterIndex),finyear )
            #print query.encode("UTF-8")
            try:
              cur.execute(query)
            except MySQLdb.IntegrityError,e:
              errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
              errorfile.write(errormessage)
            #print query1 
            cur.execute(query1)
      curtime = time.strftime('%Y-%m-%d %H:%M:%S')
      query="update musters set isProcessed=1,isComplete="+str(iscomplete)+",lastProcessDate='"+curtime+"' where id="+str(musterID);
      #print query
      cur.execute(query)
