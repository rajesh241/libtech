import os
import csv
import MySQLdb
import re
import string	
import requests
import xml.etree.ElementTree as ET

import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
import libtechFunctions
from libtechFunctions import singleRowQuery,checkLocalDND,getNumberString,getOnlyDigits,getjcNumber

def gettringoaudio(rawlist):
  tringofilelist=rawlist.rstrip(',')
  tringoArray=tringofilelist.split(',')
  noOfFiles=len(tringoArray)
  i=0
  tringoaudio=''
  while(i<20):
    curFileID='27503'
    if(i < noOfFiles):
      curFileID=tringoArray[i]
    i=i+1
    tringoaudio+="&fileid"+str(i)+"="+curFileID
  return tringoaudio
def getGroupQueryMatchString(cur,rawgroup):
  groups=rawgroup.rstrip(',')
  groupArray=groups.split(',')
  queryMatchString='( '
  for group in groupArray:
    query="select name from groups where id="+group
    #print query
    groupName=singleRowQuery(cur,query)
    #print group+groupName
    queryMatchString+="  groups like '%~"+groupName+"~%' or"
    #print '\n'
  queryMatchString=queryMatchString[:-2]
  queryMatchString+=")"
  return queryMatchString
def getLocationQueryMatchString(rawdistrict,rawblock,rawpanchayat):
  district=rawdistrict
  blocks=rawblock
  panchayats=rawpanchayat
  panchayatArray=panchayats.split(',')
  #First we need to check if panchayat name contains all then we dont need to loop through all panchayats
  if 'all' in panchayatArray:
    queryMatchString="district='"+district+"' and block='"+blocks+"' "
  else:
    queryMatchString="district='"+district+"' and block='"+blocks+"' and ("
    for panchayat in panchayatArray:
      if (panchayat != '0'):
        queryMatchString+=" panchayat ='"+panchayat+"' or" 
    queryMatchString=queryMatchString[:-2]
    queryMatchString+=")"
  #print "We are in Location" 
  #print queryMatchString
  return queryMatchString

def getaudio(cur,rawlist):
  error=0
  audio=''
  if rawlist != '':
    filelist=rawlist.rstrip(',')
    filelistArray=filelist.split(',')
    for audioFileID in filelistArray:
      query="select count(*) from audioLibrary where id="+audioFileID
      audioExists=singleRowQuery(cur,query)
      if (audioExists == 1):
        query="select filename from audioLibrary where id="+audioFileID
        #print query
        audio+=singleRowQuery(cur,query)
      else:
        error=1
      audio+=','
    audio=audio.rstrip(',')
  return audio,error

def scheduleGeneralBroadcastCall(cur,bid,phone=None,requestedVendor=None,isTest=None):
  query="use libtech"
  cur.execute(query)
  query="select bid,type,minhour,maxhour,tfileid,fileid,groups,vendor,district,blocks,panchayats,priority,fileid2,template from broadcasts where bid=%s" %(bid)
  cur.execute(query)
  row = cur.fetchone()
  tringoaudio=gettringoaudio(row[4])
  audio,error=getaudio(cur,row[5])
  audio1,error=getaudio(cur,row[12])
  if requestedVendor is None:
    requestedVendor=row[7]

  minhour='1'
  maxhour='23'
  priority='10'
  if isTest is None:
    priority=str(row[11])
    minhour=str(row[2])
    maxhour=str(row[3])
  template=row[13]
  broadcastType=row[1]
  if phone is None:
#If phone is Null then we would need to schedule Broadcast for the entire group or location
    if (broadcastType == "group"):
      queryMatchString=getGroupQueryMatchString(cur,row[6]) 
    elif (broadcastType == "location"):
      queryMatchString=getLocationQueryMatchString(row[8],row[9],row[10])
    elif (broadcastType == "transactional"):
      queryMatchString='phone is NULL'  #We dont want any calls to be Added to Call Queue
    else:
      error=1
  else:
    queryMatchString="phone='%s'" % phone


  print("Printing Debug Information"+str(bid))
  print("Broadcast ID"+str(bid))
  print("Tringo audio is "+tringoaudio)
  print("audiolist"+audio)
  print("Broadcast Type "+broadcastType)
  print("QueryMatchString "+queryMatchString)
  print("Vendor "+requestedVendor)
            
      
 
  query="select phone,exophone,dnd from addressbook where "+queryMatchString+" "
  print(query)
  cur.execute(query)
  results1 = cur.fetchall()
  for r in results1:
    phone=r[0]
    exophone=r[1]
    if exophone is None:
      exophone="08033545179"
    dnd=r[2]
    skip=0
    if(dnd == 'yes'):
      if( (requestedVendor == "any") or (requestedVendor =="tringo")):
        vendor='tringo'
      else:
        vendor="any"
        skip=1 
    else:
      vendor=requestedVendor;
    print("phone "+phone+" skip"+str(skip)+"vendor "+vendor)
    if len(phone) == 10 and phone.isdigit() and skip == 0:
      query="insert into callSummary (bid,phone) values ("+bid+",'"+phone+"');"
      print(query)
      cur.execute(query)
      callid=str(cur.lastrowid)
      query="insert into callQueue (callid,priority,template,vendor,bid,minhour,maxhour,phone,audio,audio1,tringoaudio,exophone) values ("+str(callid)+","+str(priority)+",'"+template+"','"+vendor+"',"+bid+","+minhour+","+maxhour+",'"+phone+"','"+audio+"','"+audio1+"','"+tringoaudio+"','"+exophone+"');"
      print(query)
      cur.execute(query)
            

def getWageBroadcastAudioArray(cur,jobcard,query,dbname):
  query1="use %s" % dbname
  cur.execute(query1)
  cur.execute(query)
  if (cur.rowcount == 0):
    return "error"
  else:
    row=cur.fetchone()
    amount=getNumberString(row[0])
    dateString=(str(row[3])).lstrip("0")
    day=dateString
    date=dateString+","+str(row[2].lower())+","+str(row[1])
    panchayat=row[4].lower()
    jobcardNo='1'
    if(dbname == 'surguja'):
      jobcardNo=getNumberString(getOnlyDigits(getjcNumber(jobcard)))
   # date="25,aug"
   # panchayat="lundra"
    if(dbname == "surguja"):
      baseMessage="chattisgarh_wage_broadcast_static0,panchayat,chattisgarh_wage_broadcast_static1,jobcard,chattisgarh_wage_broadcast_static2,amount,chattisgarh_wage_broadcast_static3,date,chattisgarh_wage_broadcast_static4"
    else:
      baseMessage="wage_broadcast_1,amount,wage_broadcast_2,day,wage_broadcast_3"
    baseMessage=baseMessage.replace('jobcard',jobcardNo)
    baseMessage=baseMessage.replace('date',date)
    baseMessage=baseMessage.replace('amount',amount)
    baseMessage=baseMessage.replace('day',day)
    baseMessage=baseMessage.replace('panchayat',panchayat)
    if(dbname == "surguja"):
      audioMessage=baseMessage+",chattisgarh_wage_broadcast_repeat,"+baseMessage+",chattisgarh_wage_broadcast_thankyou"
    else:
      audioMessage=baseMessage
    print(audioMessage)

    return audioMessage

def scheduleWageBroadcastCall(cur,jobcard,phone,dbname,musterTransactionID=None,isTest=None):
  query="use %s" % dbname
  cur.execute(query)
  callid='ERROR'
  bid='1185'
  if isTest is None:
    minhour='8'
    maxhour='20'
  else:
    minhour='1'
    maxhour='23'
  dnd,exophone=checkLocalDND(cur,phone)
  print(dnd+exophone)
  if (dnd == 'no'):
    if musterTransactionID is None:
      query="select mt.totalWage,DATE_FORMAT(mt.creditedDate,'%Y'),DATE_FORMAT(mt.creditedDate,'%M'),DATE_FORMAT(mt.creditedDate,'%d'),p.name,mt.id from musterTransactionDetails mt,panchayats p where mt.blockCode=p.blockCode and mt.panchayatCode=p.panchayatCode and mt.jobcard='"+jobcard+"' order by mt.creditedDate desc limit 1;"
    else:
      query="select mt.totalWage,DATE_FORMAT(mt.creditedDate,'%Y'),DATE_FORMAT(mt.creditedDate,'%M'),DATE_FORMAT(mt.creditedDate,'%d'),p.name,mt.id from musterTransactionDetails mt,panchayats p where mt.blockCode=p.blockCode and mt.panchayatCode=p.panchayatCode and mt.id="+str(musterTransactionID)
    if(dbname == 'mahabubnagar'):
      query=query.replace('creditedDate','disbursedDate') 
    audio=getWageBroadcastAudioArray(cur,jobcard,query,dbname)
    if (audio == "error"):
      print("There is some error here")
    else:
      query="use libtech" 
      cur.execute(query)
      query="insert into callSummary (bid,phone) values ("+bid+",'"+phone+"');"
      print(query)
      cur.execute(query)
      callid=str(cur.lastrowid)
      print("call Scheduled with Callid"+callid)
      query="insert into callQueue (callid,template,priority,vendor,bid,minhour,maxhour,phone,audio,exophone) values (%s,'wageBroadcast',1,'exotel',%s,%s,%s,'%s','%s','%s');" %(callid,bid,minhour,maxhour,phone,audio,exophone)
      print(query)
      cur.execute(query)
  return callid

