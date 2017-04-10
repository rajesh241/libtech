from bs4 import BeautifulSoup
import multiprocessing, time
import requests
import MySQLdb
import os
import os.path
import time
import re
import sys
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
from MySQLdb import OperationalError
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
import datetime
from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from crawlSettings import nregaDB 
from crawlSettings import nregaWebDir,nregaRawDataDir,tempDir
from crawlFunctions import alterHTMLTables,writeFile,getjcNumber,NICToSQLDate,getFullFinYear,htmlWrapperLocal,genHTMLHeader,stripTableAttributes,getCenterAligned

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing Jobcards')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-fps', '--fullPanchayatCode', help='Full Panchayat Code', required=False)
 
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args
def getWorkerList(cur,logger,stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode):
  httplib2.debuglevel = 1
  h = httplib2.Http('.cache')
  url = "http://164.100.129.6/netnrega/dynamic_account_details.aspx"
  print("URL %s " % url)
  try:
#   response = urlopen(url)
#   html_source = response.read()
#   bs = BeautifulSoup(html_source, "html.parser")
#   state = bs.find(id='__VIEWSTATE').get('value')
#   validation = bs.find(id='__EVENTVALIDATION').get('value')

    data = {
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE':'xMRyJilS+VNjCXZcVplUW9nHKiJq+WS+8Q8rvHUQE7xeHgvw45so1RcENj8zVOmvgU3VfNwiCl729Ar2qW++IzGFEP/re8Q8eNlc2PBG5JEINOkC+3nD9kf59AmwAeEpSnpOLRBlEIAzXHbyqg2iuyiKvgqi2EIq2Qb0tCw7EdCLRq5DYs20O+zP4r3tUbHhivV97JuBvEBnko/Ub0kEPjRzTV/ppYQXisc+3kxuDTf3TfPC+XCFqtU83ja+/sn32Bgx//2mjcBhZEiVzH9lpIPfA1rfrGkV7rmuWg3o2r5fYpArxaiGRPJrjgZOC0VPeqWlyKomrdo2WD9NrCSFhSmB5w+UQ4IK4mobFl7QikChWn3SuoywO2JnjzHbugpC75YoHAAIOEOYKSErRYBEIhTHo0+UeaW3OK/UDXvU82ebSyYr94IxVfN1g+TUa5uo7Knt/KKIK3FALQS64JwR+baKTkxeu7Z4OGhb3Gy2Fq+TXIQBx8EYzIXHORnVg6OuqlKM0GHmRi7LtibN3+mvjQeBqtx3gL/aGFseGGxTVpxpgJWATyUkpGi7AwB6yIbFqzlylPzved7o7g5M8+lEAqcj9Lu3X0vjO1ilQ1uoNoAKsYBqQlJHDp+sV/knltY13+pRdgRWeIBbYeF9eXJl7ITCQcejLjW+vuIjxCkRrvvDqxRtSsy3JOs5CPFuUqMkyspsgSqVn7JVf7l3skvCOJP56gphEChpIy+l87etskdLW/6t7jMqOmZ84reHc8lka8XlXVvJSknYrlSBIIyZ3xu5+QKoQ0W9NTZBCr9rQLw4aODHGp3Enc+4xJu9WUzSeJa4raP8I9StZvvd1WpmtjiWUU4gVkEPqN9c208ihyzjqufXYGT3ZIPpxPERX4VtSqhm7w+QtOPGkycKSQPJ7GNWOueSc4Jy3Lq2c72XyiO2enjssM2cuPbIZnd2JwgC3Njg++F3KNFpiwiyhDamLTVS6tfBmOObN785j3X7ueq/Mblfo8lqXVWjoBySer+S3Yne8vY7r6LIyrI9HaFgAPav0dys1X5n9/nNoc+Axv947s0/s1KM0lCSdOv/eD+L2mrEAwflm2iWqusNODTmhD3gha3sHmVZlAcMCFIzHy+/6n1uOGRxbVIJQa+dwecM3IiUshhHlrVGStkx+8g40NfZFwirasBGuWEDE1kz7mDm5PIpzfoH273fxNoBWSe9AK9HsY7eG2o7VW/BdI7AmlNk+eqcdOxNCgkuhhIRmShBmf1caUyMEyeL2wUAib+CJuFdHeSRu21NNvYzHL8ewYZh9TA5DLo6c/c/b2W9WT60P5H5fcO8u+NStl/fX3mAzDaVrRoANUzHPPlR1YgJNtyZJuulL6JDsBbYB8VILnImFi2/HgcvV7szZkUlrYfEYK9zi3vaDdHUO3CUEVgnxrjHErYZIVSu25Vk7gjRM7tAOYLYU+7ZSDEqRsu/iYCyKYxVFGnywnEdHzpxInm47b7q5ic5O0XxDNSM1rJImqz+2KhOpLDU4KEc0sWna/b1V/NJfnPYyMM3tqyIGUPx0RzNrVyCjux2Xk9m29GPnvoH62dCW7NdTujY7CNqt5/hAzEtULLYhSFkdhScdCBVx0/KDMllWAA4TXtOL//3+GCYKpoyMQGWBrzL3l/9deqqk7qlabykRvD3nhdQvOh2+JY0M9XTG5kllcs8JXqWhcgZFy5I2BbZB3ur98ZA5bEwM2ub7cMZZISRXK1FaTZssFFM33CFk48aBA3aa2jLlndAswtRHvteZKjBfhtO6L3m2kCw8S7M/2lOFtbjm7pIIxQ1/6mV90aZJrg3OKBD7/ceQl+LxbF3Ph8h7SI/xyQiONlx/jDvEMqB2N0RgH0FJ2bSJFbIeh74lafrCP7FzKQ8gYulXrQpnGsPTFdL9yB0z3aatX9p/VqbHj48laHVY3atI0ahSZwoAG2VkIbBHoxYm2llMBfy9JnILOCFJX63zQrKuEhiTqcyzW1Bxf58LpkO0k/7UwUw0wmf3aqR6sE8PySCdx8y0D58jljzkbOzLTVqa4b0rzOjx+DzXuMLyeJDHkfMpNWUzrNmlWS52b0FqbQFj6jsVsTtIPpekwMQX7ya2bDd5sG2rSH7cnWrkKBW9sD/Oe1IwKiaNzOUsLBjgm6cZmlvznt4xuZJAAnTyyCM6mT6U5cvJgdwVNVkzX3I1O5LvUbwB07VWPxTls0LXrmQ79E8R3tvEhhux5q9ppHqYgZ+D2eSvr2o2fu3t+e0SSgLACWizGwH6wqmQ1GNLZ69qdvOqLjpcadJbshZTmGPa0NaNnoWXmxA8Yis5jZn8Lx/ndpbETGN7rw6WVOExCHAHjitkN6jxJcWwOEluFV+AEn99A5JugXk/MMCvbCplWj0SKlpaAj5gB6prTzK6gv0v7N1R3uiC9d7G+bMuF0Zp7welKmJj8ty57bmdONFByRtw/Dwck5258i9aq336PbHPNKSqFpK+n4x0yYmXF57uBjm5UDp/Tmm7VQRfAKLOao=',
'__VIEWSTATEENCRYPTED':'',
'__EVENTVALIDATION':'St2U2KrBF1ia+uJiPvI+DgdWANwBZ5oXXBPbs4ewCixqadwvCY+6SIISDMl/5zyKDamrL/oUMwb6jfLnaE5SbDdO8pYpgozDp/z5KM6C8RFDQQRF6+JN/SwfHmX7131NuWrBdTzmLRkMExzJMwhCljQAlvZ8WVNHVB6SP8Rd8jChyMgL3MSxAZ1qHit+XAFtZP4yYFYPfxCCc/VFmqyuD5dCO1hLPxOq+ShdA0dKVcr36ekUpgF5hoob8Akzoh0zFxmh0Fp/H2NQrm9qGF8/2qne9YUgrZ/4soWh3CsMcAVPidEX5oQ7+URkm8d0Yix6d6hfxMqaz36YG8VI2Rqlheyo1wSMLSNs+XXbr8XNJTv3e/6jnpf6EmsPL/T95oGK4kg0t2qL9Oy95LKZvRPjxUo2BzTV2jKBKtXHqwLKC3hCLjw2vXfV46PDBxF7LtUCYtxqzrzhjLJp9NVkn/un9PP5UbL6EVV6EFJBtFxy7et5GN+Im7BYju3vkZJADugMlWIaSRK+smkqSxHkt2CykOGUCpWpQxjTOhJmx1m8j6RRSpeYQpVwx/nVoihq255FVPwC3vbI4YuuwoH0dKXV+S9c5txK+qwPFWm8dVF+QvfGQmE3aj9DTwtWfHeYOltjEQ8I6nB0auqfUlkjNW1lm16N5yiGA2CPXYV+tYuh6BW+FOlNJiDQ3RNMbXEt1Lf27+xW5Q6gj/2FdSauXrOWe7uFTUutuXIJJQlqUevOWPFbjpZ6fOJ3yniY5/+XrcIe9+7/5iFk7VRnxiEpwQPeWlovH7s0zaNyvUMSBy50gMX5Fwwgvn6vdX9GzEhtAOXqpVY3bo3uKRZvM3chqTjwJPhhwZk15+R2uA0UidUkneM9gAisyILZ7h1gSFOIW+tuLu5EOPbfTIcJGoC4B4kFh2bN5aPMRvsJB58P+BRSzZeNNYs10yb3rCa56xmR83mVj77YBiJLQXPSKK5IsgOXR9nFC7V/4oo4MxFLElKluh1tLqGi',
'ctl00$ContentPlaceHolder1$ddl_state': stateCode,
'ctl00$ContentPlaceHolder1$ddl_dist': fullDistrictCode,
'ctl00$ContentPlaceHolder1$ddl_blk': fullBlockCode,
'ctl00$ContentPlaceHolder1$ddl_pan': fullPanchayatCode,
'ctl00$ContentPlaceHolder1$ddlactive':'ALL',
'ctl00$ContentPlaceHolder1$ddlfreez':'ALL',
'ctl00$ContentPlaceHolder1$ddltype':'All',
'ctl00$ContentPlaceHolder1$ddlgender':'ALL',
'ctl00$ContentPlaceHolder1$ddlage':'ALL',
'ctl00$ContentPlaceHolder1$ddlcast':'ALL',
'ctl00$ContentPlaceHolder1$DdID':'ALL',
'ctl00$ContentPlaceHolder1$ddlvulnerable':'ALL',
'ctl00$ContentPlaceHolder1$ddlworkers':'ALL',
'ctl00$ContentPlaceHolder1$Button1':'submit',
    }
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
  except:
    response={'status': '404'}
    content=''

  return response,content


def alterWorkerList(cur,logger,inhtml,stateName,districtName,blockName,panchayatName):
  status=0
  outhtml=''
  splitHTML=inhtml.split(b"MGNREGA Worker Details") 
  if len(splitHTML) == 2:
    status=1
    logger.info("File Downloaded seeds to be correct")
    m = re.findall ( b'<table(.*?)table>', splitHTML[1], re.DOTALL)
   # logger.info(m)
    myhtml=b"<html><table"+m[0]+b"table></html>"
    htmlsoup = BeautifulSoup(myhtml, "lxml")
    tables=htmlsoup.findAll('table')
    title="MNREGA Worker List : %s-%s-%s-%s" % (stateName.upper(),districtName.upper(),blockName.upper(),panchayatName.upper())
    #outhtml+=getCenterAligned('<h3 style="color:blue"> %s</h3>' %title )
    for table in tables:
      outhtml+=stripTableAttributes(table,"libtechDetails")
    outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center" style="color:blue">'+title+'</h1>', body=outhtml)
  return status,outhtml

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  limitString=''
  if args['limit']:
    limitString=" limit %s " % args['limit']
  additionalFilters=''
  if args['district']:
    additionalFilters+= " and p.districtName='%s' " % args['district']
  if args['fullPanchayatCode']:
    additionalFilters= " and p.fullPanchayatCode='%s' " % args['fullPanchayatCode']
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  

  query="select p.stateCode,p.districtCode,p.blockCode,p.panchayatCode,p.stateName,p.districtName,p.rawBlockName,p.panchayatName,p.fullPanchayatCode,p.stateShortCode,p.crawlIP,p.fullBlockCode from panchayats p,panchayatStatus ps where p.fullPanchayatCode=ps.fullPanchayatCode and p.isRequired=1 and ( (TIMESTAMPDIFF(DAY, ps.jobcardCrawlDate, now()) > 7) or ps.jobcardCrawlDate is NULL)  %s order by ps.jobcardCrawlDate,fullPanchayatCode %s" % (additionalFilters,limitString)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [stateCode,districtCode,blockCode,panchayatCode,stateName,districtName,blockName,panchayatName,fullPanchayatCode,stateShortCode,crawlIP,fullBlockCode]=row
    logger.info("Processing statName: %s, districtName: %s, blockName: %s, panchayatName : %s " % (stateName,districtName,blockName,panchayatName))
    filepath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
    filename=filepath+blockName.upper()+"/%s/%s_MISjobcardRegister.html" % (panchayatName.upper(),panchayatName.upper())
    fullDistrictCode=stateCode+districtCode
    htmlresponse,myhtml=getWorkerList(cur,logger,stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode)
    
    if htmlresponse['status'] == '200':
      logger.info("File Downloaded SuccessFully")
      
      status,outhtml=alterWorkerList(cur,logger,myhtml,stateName,districtName,blockName,panchayatName)
      if status == 1:
        if not os.path.exists(os.path.dirname(filename)):
          os.makedirs(os.path.dirname(filename))
        myfile = open(filename, "wb")
        myfile.write(outhtml.encode("UTF-8"))
        query="update panchayatStatus set jobcardCrawlDate=NOW() where fullPanchayatCode='%s' " % fullPanchayatCode
        cur.execute(query)
        #myfile.write(outhtml)
    else:
      logger.info("Not Downloaded")
    logger.info(filename)
 
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
