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
from libtechFunctions import writecsv

def main():
  districtName='KOREA'
  datadir='/home/libtech/webroot/chaupalDataDashboard/reports/general/chattisgarhNregaAssets/%s/' % districtName
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db="korea",charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)

  query="select stateCode,districtCode,blockCode,name from blocks"
#  query="select stateCode,districtCode,blockCode,name from blocks where blockCode='005'"
# cur.execute(query)
# results=cur.fetchall()
# for row in results:
#   fullBlockCode=row[0]+row[1]+row[2]
#   blockCode=row[2]
#   blockName=row[3]
#   print fullBlockCode+blockName
  finYears=['2012-2013','2013-2014','2014-2015','2015-2016']
 #     finYears=['2012-2013']
  for finyear in finYears:
    filename=datadir+districtName+"_"+finyear+".csv"
    print filename
    query="select * from assets where fullfinyear='%s'" % finyear
    print query
    writecsv(cur,query,filename)
    

if __name__ == '__main__':
  main()
