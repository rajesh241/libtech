#This code will get the Oabcgatat Banes
import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
#regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
regex=re.compile(r'<input type="hidden" value="[A-Za-z0-9]+.*?"\s*/>+',re.DOTALL)
searchtext = re.compile(r'MGNREGA Bank Account Details',re.IGNORECASE)
#Connect to MySQL Database
db = MySQLdb.connect(host="localhost", user="root", passwd="golani123", db="surguja",charset='utf8')
cur=db.cursor()
db.autocommit(True)
#Query to set up Database to read Hindi Characters
query="SET NAMES utf8"
cur.execute(query)
#Getting all the blocks
query="select name,blockCode from blocks where isActive=1 "
cur.execute(query)
results = cur.fetchall()
for row in results:
  blockName=row[0]
  blockCode=row[1]
  print blockName+blockCode
  bankFileName='/tmp/bank.html'
  bankFileName='/home/goli/libtech/data/CHATTISGARH/SURGUJA/'+blockName+'/DATA/bankAccountDetails.html'
  bankhtml=open(bankFileName,'r').read()
  bankhtml1=re.sub(regex,"",bankhtml)#Have to do this else the beautiful soup goofs up. Removes the input tag from HTML
  htmlsoup=BeautifulSoup(bankhtml1)
  foundtext = htmlsoup.find('b',text=searchtext) # Find the first <b> tag with the search text which is MNREGA Bank Account Details
  table = foundtext.findNext('table') # Find the first <table> tag that follows it
  rows = table.findAll('tr')
  for tr in rows:
    cols = tr.findAll('td')
    col0="".join(cols[0].text.split())
    col1="".join(cols[1].text.split())
    if 'StateName' in col1:
      print "Ignore the header row"
    else:
      jobcard="".join(cols[5].text.split())
      applicantNo="".join(cols[6].text.split())
      accountNo="".join(cols[12].text.split())
      applicantName="".join(cols[7].text.split())
      bankCode="".join(cols[8].text.split())
      bankName="".join(cols[9].text.split())
      branchCode="".join(cols[10].text.split())
      branchName="".join(cols[11].text.split())
      IFSCCode="".join(cols[13].text.split())
      MICRCode="".join(cols[14].text.split())
      primaryAccountHolder="".join(cols[15].text.split())
      accountFrozen="".join(cols[21].text.split())
      if accountFrozen=='Y':
        accountFrozen=1
      else:
        accountFrozen=0
      if accountNo=='':
        accountNo=0
      #print applicantName
      query="select id from jobcardDetails where jobcard='"+jobcard+"' and accountNo='"+str(accountNo)+"' and applicantName='"+applicantName+"'"
      #print query
      cur.execute(query)
      results1 = cur.fetchall()
      for row1 in results1:
        rowid=str(row1[0])
        print jobcard+"  "+applicantName+"  "+rowid
        query="update jobcardDetails set primaryAccountHolder='"+primaryAccountHolder+"',bankNameOrPOName='"+bankName+"',bankCode='"+bankCode+"',branchNameOrPOAddress='"+branchName+"',branchCodeorPOCode='"+branchCode+"',IFSCCodeOrEMOCode='"+IFSCCode+"',MICRCodeOrSanchayCode='"+MICRCode+"',accountFrozen="+str(accountFrozen)+" where id="+rowid
        #print query
        cur.execute(query)
