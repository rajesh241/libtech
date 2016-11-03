from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
sys.path.insert(0, fileDir+'/../scripts/')
from globalSettings import datadir,nregaDataDir,reportsDir,nregaDir
from crawlFunctions import getDistrictParams
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery,writecsv,getFullFinYear,writeFile
from globalSettings import datadir,nregaDataDir,reportsDir,nregaStaticReportsDir
from nregaSettings import nregaStaticWebDir,nregaRawDataDir,tempDir 
from nregaUIFunctions import htmlWrapperLocalRelativeCSS,tabletUIQuery2HTML,getCenterAligned

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='HouseKeeping Script for SurGUJA Database')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)
  parser.add_argument('-rid', '--reportID', help='Report ID for the report to be generated', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)

  args = vars(parser.parse_args())
  return args

def queryGen(cur,logger,rid,finyear=None,blockCode=None,panchayatCode=None,jobcard=None,htmlDir=None):
  query="select title,type,selectClause,whereClause,orderClause,dbname,groupClause,linkIndex,linkType,limitResults,finyearFilter,jobcardFilter from dashboardQueries where id=%s"  % (str(rid)) 
  logger.info(query)
  cur.execute(query)
  queryResults=cur.fetchall()
  for queryRow in queryResults:
    title=queryRow[0]
    queryType=queryRow[1]
    selectClause=queryRow[2]
    whereClause=queryRow[3]
    orderClause=queryRow[4]
    groupClause=queryRow[6]
    limit=queryRow[9]
    limitString=" limit 200 "
    if limit ==0:
      limitString=''

    finyearFilter=queryRow[10]
    jobcardFilter=queryRow[11]
    
    if jobcardFilter is not None:
      jobcardFilterQuery=jobcardFilter.replace("myjobcard",jobcard)
   
    if finyear is not None:
      if finyear == 'all':
        finyearFilterQuery=""
      else:
        finyearFilterQuery=finyearFilter.replace("myfinyear",finyear)

    groupString=''
    if groupClause is not None:
      groupString= " group by %s " % groupClause
    
    if queryType=="location":
      whereClause+= finyearFilterQuery
      whereClause+= " and b.blockCode='%s' " % (blockCode)
      isBlock=1
      if panchayatCode is not None:
        whereClause += " and p.panchayatCode='%s' " % (panchayatCode)
        isBlock=0
    elif queryType=="jobcard":
      whereClause+= jobcardFilterQuery
      isBlock=0

    query="%s where %s %s order by %s %s " % (selectClause,whereClause,groupString,orderClause,limitString)
    logger.info(query)
    #queryWithoutLimit=query.replace("limit 50"," ")
    if queryRow[7] is not None: 
      linkIndex=queryRow[7].split(',')
      linkType=queryRow[8].split(',')
      queryTable=tabletUIQuery2HTML(cur,query,hiddenValues=linkIndex,hiddenNames=linkType,htmlDir=htmlDir,isBlock=isBlock)
    else:
      queryTable=tabletUIQuery2HTML(cur,query,htmlDir=htmlDir,isBlock=isBlock)

    return query,queryTable


def genAllReports(cur,logger,reportIDFilter,finyear,districtName,blockCode=None,blockName=None,panchayatCode=None,panchayatName=None,jobcard=None,htmlDir=None):
  query="select id,title,type from dashboardQueries where type='location' and isRequired=1 %s" % (reportIDFilter)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rid=str(row[0])
    title=row[1]
    queryType=row[2]
    reportQuery,reportTable=queryGen(cur,logger,rid,finyear=finyear,blockCode=blockCode,panchayatCode=panchayatCode,jobcard=jobcard,htmlDir=htmlDir)
    myhtml=''
    
    relativeCSSPath='../../../'

    if panchayatCode is None:
      relativeCSSPath='../../'
      pdir=''
      queryTitle="Block Name: %s" % (blockName.upper())
      navigation=' <a href="../../../%s.html"> %s </a> - <a href="../../%s.html">%s </a> ' % (districtName.upper(),districtName.upper(),blockName.upper(),blockName.upper())
    else:
      pdir=panchayatName.upper()
      queryTitle="Block Name: %s    Panchayat Name: %s" % (blockName.upper(),panchayatName.upper())
      navigation=' <a href="../../../%s.html"> %s </a> - <a href="../../%s.html">%s </a> - <a href="../%s.html">%s</a> ' % (districtName.upper(),districtName.upper(),blockName.upper(),blockName.upper(),panchayatName.upper(),panchayatName.upper())


    if finyear == 'all':
      reportsDir="REPORTS"
    else:
      reportsDir="REPORTS%s" % (finyear)
    reportTable=reportTable.replace("query_text",queryTitle)
    myhtml+=  getCenterAligned("<h2>%s</h2>" %navigation)
    myhtml+="</br></br>"
    myhtml+=reportTable
    curhtmlfile="%s/%s/%s/%s/%s.html" % (htmlDir,blockName.upper(),pdir,reportsDir,title.replace(' ',''))
    curcsvfile="%s/%s/%s/%s/%s.csv" % (htmlDir,blockName.upper(),pdir,reportsDir,title.replace(' ',''))
    logger.info(curhtmlfile)
    myhtml=htmlWrapperLocalRelativeCSS(relativeCSSPath=relativeCSSPath,title=title, head='<h1 aling="center">%s</h1>' %(title), body=myhtml)
    writeFile(curhtmlfile,myhtml)
    reportQuery=reportQuery.replace("limit 200 ","")
    logger.info("ReportQulery: %s " % reportQuery)
    writecsv(cur,reportQuery,curcsvfile)
    #curcsvfile="/home/libtech/webroot/nreganic.libtech.info/temp/a/%s_%s.csv" % (panchayatName.upper(),title.replace(' ',''))
    #writecsv(cur,reportQuery,curcsvfile)

def genJobcardReports(cur,logger,districtName,blockCode,blockName,panchayatCode,panchayatName,htmlDir):
  query="select jobcard from jobcardRegister where blockCode='"+blockCode+"' and panchayatCode='"+panchayatCode+"' " 
  cur.execute(query)
  results1=cur.fetchall()
  relativeCSSPath='../../../'
  for row1 in results1:
    jobcard=row1[0]
    logger.info(jobcard)
    jcReportFileName=htmlDir+"/"+blockName.upper()+"/"+panchayatName.upper()+"/jobcardRegister/"+jobcard.replace("/","_")+".html"
    logger.info(jcReportFileName)

    myhtml=''
    navigation=' <a href="../../../%s.html"> %s </a> - <a href="../../%s.html">%s </a> - <a href="../%s.html">%s</a> ' % (districtName.upper(),districtName.upper(),blockName.upper(),blockName.upper(),panchayatName.upper(),panchayatName.upper())
    myhtml+=  getCenterAligned("<h2>%s</h2>" %navigation)
    myhtml+="</br></br>"
    curhtmlfile=htmlDir+"/"+blockName.upper()+"/"+panchayatName.upper()+"/jobcardRegister/"+jobcard.replace("/","_")+".html"
    logger.info(jcReportFileName)
    query="select id,title,type from dashboardQueries where isRequired=1 and type='jobcard'"
    cur.execute(query)
    results=cur.fetchall()
    for row in results:
      rid=str(row[0])
      title=row[1]
      queryType=row[2]
      reportQuery,reportTable=queryGen(cur,logger,rid,blockCode=blockCode,panchayatCode=panchayatCode,jobcard=jobcard,htmlDir=htmlDir)
      reportTable=reportTable.replace("query_text",title)
      myhtml+=reportTable
      myhtml+="</br></br></br>"
   
    myhtml=htmlWrapperLocalRelativeCSS(relativeCSSPath=relativeCSSPath,title=title, head='<h1 aling="center">%s</h1>' %(jobcard), body=myhtml)
    writeFile(curhtmlfile,myhtml)

    #Generate the jobcard Reports
    

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  if args['district']:
    districtName=args['district'].lower()
  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString="  "
  if args['reportID']:
    reportIDFilter= " and id = %s " % args['reportID']
  else:
    reportIDFilter= " "
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)

  htmlDir=nregaStaticWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
  finyear='17'
    
  query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode  and p.isRequired=1 %s" % limitString
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    panchayatName=row[2]
    panchayatCode=row[3]
    genJobcardReports(cur,logger,districtName,blockCode,blockName,panchayatCode,panchayatName,htmlDir)
    genAllReports(cur,logger,reportIDFilter,'17',districtName,blockCode=blockCode,blockName=blockName,panchayatCode=panchayatCode,panchayatName=panchayatName,htmlDir=htmlDir)
#    genAllReports(cur,logger,reportIDFilter,'16',districtName,blockCode=blockCode,blockName=blockName,panchayatCode=panchayatCode,panchayatName=panchayatName,htmlDir=htmlDir)
 #   genAllReports(cur,logger,reportIDFilter,'all',districtName,blockCode=blockCode,blockName=blockName,panchayatCode=panchayatCode,panchayatName=panchayatName,htmlDir=htmlDir)
 
  #block Reports
  query="select b.name,b.blockCode from blocks b where b.isRequired=1 %s" % limitString
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    genAllReports(cur,logger,reportIDFilter,'17',districtName,blockCode=blockCode,blockName=blockName,htmlDir=htmlDir)
  #  genAllReports(cur,logger,reportIDFilter,'16',districtName,blockCode=blockCode,blockName=blockName,htmlDir=htmlDir)
  #  genAllReports(cur,logger,reportIDFilter,'all',districtName,blockCode=blockCode,blockName=blockName,htmlDir=htmlDir)

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()

#def genReport(cur,logger,isBlock,htmlDir,finyear,districtName,blockCode,blockName,panchayatCode,panchayatName,reportIDFilter):
#Generate Block Filter Query

# blockFilterQuery=" and b.blockCode="+str(blockCode)
# panchayatFilterQuery=" and p.panchayatCode="+str(panchayatCode)
#
# panchayatNameOnlyLetters=re.sub(r"[^A-Za-z]+", '', panchayatName)
# pdir=panchayatNameOnlyLetters.upper()+'/'
# relativeCSSPath='../../../'
#
#
# if isBlock == 1:
#   panchayatFilterQuery=''
#   panchayatCode=''
#   panchayatName=''
#   pdir=''
#   relativeCSSPath='../../'
#
# logger.info("Processing"+blockName+panchayatName) 
# query="select title,dbname,selectClause,whereClause,orderClause,dbname,groupClause,linkIndex,linkType,limitResults,finyearFilter from dashboardQueries where isRequired=1 %s"  % (reportIDFilter) 
# cur.execute(query)
# queryResults=cur.fetchall()
# for queryRow in queryResults:
#   title=queryRow[0]
#   dbname=queryRow[1]
#   selectClause=queryRow[2]
#   whereClause=queryRow[3]
#   orderClause=queryRow[4]
#   groupClause=queryRow[6]
#   limit=queryRow[9]
#   limitString=" limit 200 "
#   if limit ==0:
#     limitString=''
#   finyearFilter=queryRow[10]
#   if finyear == 'all':
#     rdir="REPORTS"
#     finyearFilterQuery=""
#   else:
#     finyearFilterQuery=finyearFilter.replace("myfinyear",finyear)
#     rdir="REPORTS"+finyear
#   if groupClause is None:
#     query=selectClause+" where "+whereClause+blockFilterQuery+panchayatFilterQuery+finyearFilterQuery+"  order by  "+orderClause+limitString
#   else: 
#     query=selectClause+" where "+whereClause+blockFilterQuery+panchayatFilterQuery+finyearFilterQuery+" group by "+groupClause+"  order by  "+orderClause+limitString
#   #queryWithoutLimit=query.replace("limit 50"," ")
#   if queryRow[7] and queryRow[8]:
#     linkIndex=queryRow[7].split(',')
#     linkType=queryRow[8].split(',')
#     logger.info(query)
#     queryTable=tabletUIQuery2HTML(cur,query,hiddenValues=linkIndex,hiddenNames=linkType,districtName=districtName,blockName=blockName,panchayatName=panchayatName,isBlock=isBlock)
#   else:
#     queryTable=tabletUIQuery2HTML(cur,query)
#   queryTable=queryTable.replace('query_text',query) 
#   myhtml=''
#   myhtml+=  getCenterAligned('<h2 style="color:blue"> %s</h2>' % (title))
#   myhtml+=  getCenterAligned('<h3 style="color:green"> %s-%s</h3>' % (blockName.upper(),panchayatName.upper()))
#   
#   myhtml+= queryTable
# 
#   curhtmlfile=htmlDir+"/"+blockName.upper()+"/"+pdir+rdir+"/"+title.replace(' ','')+".html"
#   logger.info(curhtmlfile)
#   myhtml=htmlWrapperLocalRelativeCSS(relativeCSSPath=relativeCSSPath,title=title, head='<h1 aling="center">Reports Page</h1>', body=myhtml)
#   if not os.path.exists(os.path.dirname(curhtmlfile)):
#     os.makedirs(os.path.dirname(curhtmlfile))
#   f=open(curhtmlfile,'w')
#   f.write(myhtml.encode("UTF-8"))
#   query=selectClause+" where "+whereClause+blockFilterQuery+panchayatFilterQuery+finyearFilterQuery+"  order by  "+orderClause
#   logger.info(query)
#   curcsvfile=htmlDir+"/"+blockName.upper()+"/"+pdir+rdir+"/"+title.replace(' ','')+".csv"
#   writecsv(cur,query,curcsvfile)
#
