import csv
from bs4 import BeautifulSoup
import requests
import os
import time
import re
import sys
import urllib2
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
  blockNames=['BHAIYATHAN','SURAJPUR','RAMANUJNAGAR','PRATAPPUR']
  blockCodes=['3305012','3305009','3305011','3305015']
  blockNames=['BAIKUNTHPUR','BHARATPUR','KHADGAWANA','MANENDRAGARH','SONHAT']
  blockCodes=['3306001','3306005','3306003','3306004','3306002']
  j=0
  for oneWorkCode in workCodes:
    curWorkName=workNames[j]
    j=j+1
    for oneFinyear in finYears:
      #print oneFinyear
      i=0
      for block in blockNames:
        curBlockCode=blockCodes[i]
        print oneWorkCode+curWorkName+block+blockCodes[i]
        i=i+1

        myURL='http://164.100.112.66/netnrega/citizen_html/assetscreatedblk.aspx?lflag=eng&page=b&f=1&block_code=%s&workstatus=05&project=%s&finyear=%s&state_name=CHHATTISGARH&district_name=SURAJPUR&block_name=%s' %(curBlockCode,oneWorkCode,oneFinyear,block)
        myURL='http://164.100.112.66/netnrega/citizen_html/assetscreatedblk.aspx?lflag=eng&page=b&f=1&block_code=%s&workstatus=05&project=%s&finyear=%s&state_name=CHHATTISGARH&district_name=KOREA&block_name=%s' %(curBlockCode,oneWorkCode,oneFinyear,block)
        print myURL
        response = urllib2.urlopen(myURL)
        myhtml = response.read()
       # r=requests.get(myURL)
       # myhtml=r.text
        #myhtml=myhtml.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
        musterfilename=datadir+block+"/"+oneFinyear+"/"+curWorkName+".html"
        if not os.path.exists(os.path.dirname(musterfilename)):
          os.makedirs(os.path.dirname(musterfilename))
        f = open(musterfilename, 'w')
       # f.write(myhtml.encode("UTF-8"))
        f.write(myhtml)

if __name__ == '__main__':
  main()
