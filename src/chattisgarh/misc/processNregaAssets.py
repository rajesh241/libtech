import csv
from bs4 import BeautifulSoup
import requests
import os
import time
import re
import sys
import urllib2
import MySQLdb
import time
import re
import os
import sys
import os.path
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token


  #Getting the block code
  #inblock=sys.argv[1]
  #print inblock
  #Connect to MySQL Database
def main():
  datadir='/home/libtech/webroot/chaupalDataDashboard/reports/general/chattisgarhNregaAssets/KOREA/'
  workCodes=['AV','SK','CA','DP','FR','FP','FG','LD','IC','OP','PG','WH','RC','DW','RS','WC','IF']
  workNames=['anganwadi','bharatNirmanRajeevGandhiSewaKendra','costalAreas','droughtProofing','fisheries','floodControlProtection','foodGrains','landDevelopment','microIrrigationWorks','otherWorks','playGround','renovationTraditionalWaterBodies','ruralConnectivity','ruralDrinkingWater','ruralSanitation','waterConservationWaterHarvesting','worksIndividualLand']

  finYears=['2012-2013','2013-2014','2014-2015','2015-2016']
  blockNames=['AMBIKAPUR','BATAULI','LAKHANPUR','LUNDRA','MAINPAT','SITAPUR','UDAIPUR']
  blockCodes=['3305001','3305007','3305002','3305005','3305008','3305006','3305003']

  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db="korea",charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)

         
  query="select stateCode,districtCode,blockCode,name from blocks"
#  query="select stateCode,districtCode,blockCode,name from blocks where blockCode='005'"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    fullBlockCode=row[0]+row[1]+row[2]
    blockCode=row[2]
    blockName=row[3]
    print fullBlockCode+blockName

    query="select workCode,description from workCodes where workCode='DP'"
    query="select workCode,description from workCodes "
    cur.execute(query)
    results1=cur.fetchall()
    for row1 in results1:
      workDescription=row1[1]
      
      finYears=['2012-2013','2013-2014','2014-2015','2015-2016']
 #     finYears=['2012-2013']
      for finyear in finYears:
        assetfilename=datadir+blockName+"/"+finyear+"/"+workDescription+".html"
        print assetfilename
        if (os.path.isfile(assetfilename)): 
          assethtml=open(assetfilename,'r').read()
     #     assethtml=re.sub(regex,"</font></td>",assethtml1)
        else:
          assethtml="Timeout expired"

        htmlsoup=BeautifulSoup(assethtml)
        try:
          foundtable=htmlsoup.find('table',id="Table2")
          table = foundtable.findNext('table')
          rows = table.findAll('tr')
          errorflag=0
        except:
          errorflag=1

        if errorflag==0:
          i=0
          for tr in rows:
            cols = tr.findAll('td')
            print "Length of Columns ="+str(len(cols))
            if len(cols) == 11:
              block="".join(cols[2].text.split())
              panchayat="".join(cols[3].text.split())
              worknameworkcode=cols[4].text
              print worknameworkcode.encode("UTF-8")
              executingLevel="".join(cols[5].text.split())
              completionDateString="".join(cols[6].text.split())
              laborComponent="".join(cols[7].text.split())
              materialComponent="".join(cols[8].text.split())
              actualLaborExpense="".join(cols[9].text.split())
              actualMaterialExpense="".join(cols[10].text.split())
              if completionDateString != '':
                completionDate = time.strptime(completionDateString, '%d/%m/%Y')
                completionDate = time.strftime('%Y-%m-%d %H:%M:%S', completionDate)
              else:
                completionDate=''

              worknameworkcodearray=re.match(r'(.*)\(3306(.*)\)',worknameworkcode)
              if worknameworkcodearray:
                workName=worknameworkcodearray.groups()[0]
                workCode='3306'+worknameworkcodearray.groups()[1]
                
                query="insert into assets (blockCode,block,panchayat,fullfinyear,executingLevel,workCode,workName,completionDate,laborComponent,materialComponent,actualLaborExpense,actualMaterialExpense) values ('%s','%s','%s','%s','%s','%s','%s','%s',%s,%s,%s,%s) " % (blockCode,blockName,panchayat,finyear,executingLevel,workCode,workName,completionDate,str(laborComponent),str(materialComponent),str(actualLaborExpense),str(actualMaterialExpense))
                #print query.encode("UTF-8")
                try:
                  cur.execute(query)
                except MySQLdb.IntegrityError,e:
                  errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
                  continue
                  cur.execute(query)
               
                i=i+1
                #print str(i)+block+panchayat+workCode.encode("UTF-8")
  
 
if __name__ == '__main__':
  main()
