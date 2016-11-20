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
from libtechFunctions import singleRowQuery,checkLocalDND,getNumberString,getOnlyDigits,getjcNumber,addPhoneAddressBook

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

def scheduleGeneralBroadcastCall(cur,bid,phone=None,requestedVendor=None,isTest=None,sid=None):
  query="use libtech"
  cur.execute(query)
  query="select bid,type,minhour,maxhour,tfileid,fileid,groups,vendor,district,blocks,panchayats,priority,fileid2,template,inQuery,region from broadcasts where bid=%s" %(bid)
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
  preference='10000'
  if isTest is None:
    priority=str(row[11])
    minhour=str(row[2])
    maxhour=str(row[3])
    preference='40'
  template=row[13]
  inQuery=row[14]
  region=row[15]
  broadcastType=row[1]
  if phone is None:
#If phone is Null then we would need to schedule Broadcast for the entire group or location
    if (broadcastType == "group"):
      queryMatchString=getGroupQueryMatchString(cur,row[6]) 
      phoneQuery="select phone  from addressbook where "+queryMatchString+" "
    elif (broadcastType == "location"):
      queryMatchString=getLocationQueryMatchString(row[8],row[9],row[10])
      phoneQuery="select phone  from addressbook where "+queryMatchString+" "
    elif (broadcastType == "queryBased"):
      phoneQuery=inQuery
    elif (broadcastType == "transactional"):
      queryMatchString='phone is NULL'  #We dont want any calls to be Added to Call Queue
      phoneQuery="select phone  from addressbook where "+queryMatchString+" "
    else:
      error=1
  else:
    query="select id from addressbook where phone='"+phone+"'"
    cur.execute(query)
    if (cur.rowcount == 0):
      query="insert into addressbook (phone,exophone,dnd) values ('%s','08033545179','no')" % (phone)
      cur.execute(query)
    queryMatchString="phone='%s'" % phone
    phoneQuery="select phone  from addressbook where "+queryMatchString+" "


  print("Printing Debug Information"+str(bid))
  print("Broadcast ID"+str(bid))
  print("Tringo audio is "+tringoaudio)
  print("audiolist"+audio)
  print("Broadcast Type "+broadcastType)
  print("Query "+phoneQuery)
  print("Vendor "+requestedVendor)
            
      
  if sid is not None:
    phone=phone[-10:]
    addPhoneAddressBook(cur,phone,'','','')
  
  #query="select phone,exophone,dnd from addressbook where "+queryMatchString+" "
  print(phoneQuery)
  cur.execute(phoneQuery)
  results1 = cur.fetchall()
  dnd="no"
  for r in results1:
    phone=r[0]
    query="select exophone from regions where region='%s' " % region
    cur.execute(query)
    rowdnd=cur.fetchone()
    exophone=rowdnd[0]
    
    if exophone is None:
      exophone="08033545179"
    if sid is not None:
      exophone="08033545179"
      dnd="no"
      
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
    skip =0
    if len(phone) == 10 and phone.isdigit() and skip == 0:
      #query="insert into callSummary (bid,phone,callRequestTime) values ("+bid+",'"+phone+"',NOW());"
      query="insert into callSummary (bid,phone,callRequestTime,template,audio,audio1,region) values (%s,'%s',NOW(),'%s','%s','%s','%s');" % (bid,phone,template,audio,audio1,region)
      print(query)
      cur.execute(query)
      callid=str(cur.lastrowid)
      if sid is not None:
        query="insert into callQueue (callid,priority,preference,template,vendor,bid,minhour,maxhour,phone,audio,audio1,tringoaudio,exophone,inprogress,callRequestTime,curVendor,isTest,sid) values ("+str(callid)+","+str(priority)+","+str(preference)+",'"+template+"','exotel',"+bid+","+minhour+","+maxhour+",'"+phone+"','"+audio+"','"+audio1+"','"+tringoaudio+"','"+exophone+"',1,NOW(),'exotel',1,'"+sid+"');"
      else:
        query="insert into callQueue (callid,priority,preference,template,vendor,bid,minhour,maxhour,phone,audio,audio1,tringoaudio,exophone) values ("+str(callid)+","+str(priority)+","+str(preference)+",'"+template+"','"+vendor+"',"+bid+","+minhour+","+maxhour+",'"+phone+"','"+audio+"','"+audio1+"','"+tringoaudio+"','"+exophone+"');"
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
def updateBroadcastStats(cur,logger,bid):
  query="select count(*) from callSummary where status='success' and bid="+str(bid)
  success=singleRowQuery(cur,query)
  query="select count(*) from callSummary where status='failMaxRetry' and bid="+str(bid)
  failMaxRetry=singleRowQuery(cur,query)
  query="select count(*) from callSummary where status='expired' and bid="+str(bid)
  expired=singleRowQuery(cur,query)
  query="select count(*) from callSummary where status='pending' and bid="+str(bid)
  pending=singleRowQuery(cur,query)  
  query="select sum(cost) from callLogs where bid="+str(bid)
  cost=singleRowQuery(cur,query)
  query="select TIMESTAMPDIFF(DAY, endDate, now()) from broadcasts where bid="+str(bid)
  timediff=singleRowQuery(cur,query)
  if cost == None:
    cost = 0
  else:
    cost = cost/100
  total=success+expired+failMaxRetry+pending
  successPercentage=0
  if (total > 0):
    successPercentage=math.trunc(success*100/total)
  logger.info(str(success)+"  "+str(failMaxRetry)+"  "+str(expired)+"  "+str(pending)+"  "+str(total)+"  "+str(cost))
  isComplete=0
  if((pending == 0) and (timediff > 2)):
   isComplete=1
  query="update broadcasts set successP='"+str(successPercentage)+"',completed="+str(isComplete)+",success="+str(success)+",cost="+str(cost)+",fail="+str(failMaxRetry)+",expired="+str(expired)+",pending="+str(pending)+",total="+str(total)+" where bid="+str(bid) 
  logger.info(query)
  cur.execute(query)


def updateBroadcastStatus(cur,logger):
  query="select bid from broadcasts where error=0 and processed=1 and status != 'complete'"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    bid=str(row[0])
    logger.info("Processing BID %s " % bid)
    query="select count(*) from callSummary where bid=%s and status='pending'" % (bid)
    count=singleRowQuery(cur,query)
    updateBroadcastStats(cur,logger,bid)
    logger.info("Pending calls for bid: %s is %s " % (bid,str(count)))
    if count == 0:
      query="update broadcasts set status='complete' where bid=%s" % bid
      cur.execute(query) 
    
