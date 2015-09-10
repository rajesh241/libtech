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
from libtechFunctions import singleRowQuery

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
  filelist=rawlist.rstrip(',')
  filelistArray=filelist.split(',')
  audio=''
  for audioFileID in filelistArray:
    query="select count(*) from audioLibrary where id="+audioFileID
    audioExists=singleRowQuery(cur,query)
    if (audioExists == 1):
      query="select filename from audioLibrary where id="+audioFileID
#      print query
      audio+=singleRowQuery(cur,query)
    else:
      error=1
    audio+=','
  audio=audio.rstrip(',')
  return audio,error

def scheduleGeneralBroadcastCall(cur,bid,phone=None,requestedVendor=None,priority=None):
  query="use libtech"
  cur.execute(query)
  query="select bid,type,minhour,maxhour,tfileid,fileid,groups,vendor,district,blocks,panchayats,priority,fileid2,template from broadcasts where bid=%s" %(bid)
  cur.execute(query)
  row = cur.fetchone()
  minhour=str(row[2])
  maxhour=str(row[3])
  tringoaudio=gettringoaudio(row[4])
  audio,error=getaudio(cur,row[5])
  if requestedVendor is None:
    requestedVendor=row[7]
  if priority is None:
    priority=row[11]
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


  print "Printing Debug Information"+str(bid)
  print "Broadcast ID"+str(bid)
  print "Tringo audio is "+tringoaudio;
  print "audiolist"+audio
  print "Broadcast Type "+broadcastType
  print "QueryMatchString "+queryMatchString
  print "Vendor "+requestedVendor
            
      
 
  query="select phone,exophone,dnd from addressbook where "+queryMatchString+" "
  print query
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
    print "phone "+phone+" skip"+str(skip)+"vendor "+vendor
    if len(phone) == 10 and phone.isdigit() and skip == 0:
      query="insert into callSummary (bid,phone) values ("+bid+",'"+phone+"');"
      print query
      cur.execute(query)
      callid=str(cur.lastrowid)
      query="insert into callQueue (callid,priority,template,vendor,bid,minhour,maxhour,phone,audio,audio1,tringoaudio,exophone) values ("+callid+","+str(priority)+",'"+template+"','"+vendor+"',"+bid+","+minhour+","+maxhour+",'"+phone+"','"+audio+"','"+audio+"','"+tringoaudio+"','"+exophone+"');"
      print query
      cur.execute(query)
            
     
