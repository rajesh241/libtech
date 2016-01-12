#! /usr/bin/env python

import time
from bs4 import BeautifulSoup
from time import strftime

import os
dirname = os.path.dirname(os.path.realpath(__file__))
interim_dir = os.path.dirname(dirname)
rootdir = os.path.dirname(interim_dir) # Since this file is 2 levels 

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize
from wrappers.db import dbInitialize,dbFinalize

from MySQLdb import IntegrityError

#######################
# Global Declarations
#######################

delay = 0
url="http://khadya.cg.nic.in/pdsonline/cgfsa/Report/FrmRation_Patra_Allot_VerificationDistWise_Aug14.aspx"

month2number = {
  "जनवरी":1, "फरवरी":2, "मार्च":3, "अप्रैल":4, "मई":5, "जून":6, "जुलाई":7, "अगस्त":8, "सितम्बर":9, "अक्टूबर":10, "नवम्बर":11, "दिसम्बर":12
}


#############
# Functions
#############

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Jobcard script for crawling, downloading & parsing')
  parser.add_argument('-c', '--crawl', help='Crawl the pds reports', required=False, action='store_const', const=True)
  parser.add_argument('-r', '--prev', help='Fetch the previous months PDS reports', required=False, action='store_const', const=True)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--timeout', help='Time to wait before a page loads', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-u', '--url', help='Specify the url to crawl', required=False)
  parser.add_argument('-d', '--directory', help='Specify directory to download html file to', required=False)
  parser.add_argument('-p', '--parse', help='Parse the PDS reports downloaded', required=False, action='store_const', const=True)
  parser.add_argument('-m', '--month', help='Specify the month for download', required=False)
  parser.add_argument('-y', '--year', help='Specify the year for download', required=False)
  parser.add_argument('-w', '--work-allocation', help='Download Work Allocation Reports', required=False, action='store_const', const=True)

  args = vars(parser.parse_args())
  return args

def downloadWorkAllocationHTML(driver, db, logger, url=None):
  '''
  Crawl the page for the khadya site and fecth the latest reports
  '''
  query='select b.name, b.blockCode, p.name, p.panchayatCode from blocks b, panchayats p where b.blockCode=p.blockCode and b.blockCode="007"'
  logger.info('query: [%s]', query)
  cur=db.cursor()
  cur.execute(query)
  results = cur.fetchall()
  logger.debug('results: [%s]', str(results))

  for row in results:
    (block_name, block_code, panchayat_name, panchayat_code) = row
    logger.info('Block Name[%s], BlockCode[%s], Panchayat Name[%s], Panchayat Code[%s]' % (block_name, block_code, panchayat_name, panchayat_code))
#    filename = './reports/'+ block_code + '_' + panchayatName + '_' + panchayatCode + '.html'
    filename = './'+ block_code + '_' + panchayat_name + '_' + panchayat_code + '.html'
    
    if os.path.exists(filename):
      logger.info("Skipped [%s] as alread downloaded" % filename)
      continue
#    logger.info('Block Name:[%s] Panchayat Name:[%s] Shop Code:[%s]' % (blockName, panchayat, shopCode))

    if not url:
      url="http://164.100.112.66/netnrega/writereaddata/state_out/work_alloc_report_3305007038_1516.html"
      
    url="http://164.100.112.66/netnrega/IndexFrame.aspx?lflag=eng&District_Code=3305&district_name=SURGUJA&state_name=CHHATTISGARH&state_Code=33&"      
    url += "block_name=%s&block_code=3305%s&fin_year=2015-2016&check=1&Panchayat_name=%s&Panchayat_Code=3305%s" % (block_name, block_code, panchayat_name, block_code+panchayat_code)
    logger.info('URL: [%s]', url)

    driver.get(url)
    time.sleep(delay)

    elem = driver.find_element_by_link_text("Employment Offered")
    elem.click()
    
    time.sleep(delay)
    html_source = driver.page_source
    raw_html=html_source.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    with open(filename, "w") as html_file:
      logger.info("Writing [%s]" % filename)
      html_file.write(raw_html.encode("UTF-8"))
    return

def pdsFetch(logger, driver, db, dir=None):
  '''
  Crawl to the page for the khadya site and fecth the latest reports
  '''
  
  if not dir:
    dir='./reports'
  
  query="select b.pdsBlockCode,b.name,s.shopCode,m.panchayat from pdsShops s,blocks b, shopMapping m where b.blockCode=s.blockCode and s.shopcode = m.shopcode and m.isDownloaded = 0"
  logger.info('query: [%s]', query)
  cur=db.cursor()
  cur.execute(query)
  results = cur.fetchall()
  logger.debug('results: [%s]', str(results))

  for row in results:
    (pdsBlockCode, blockName, shopCode, panchayat) = row
    logger.info('pdsBlockCode[%s], blockName[%s], shopCode[%s], panchayat[%s]' % (pdsBlockCode, blockName, shopCode, panchayat))
    filename = dir + '/' + blockName + '_' + panchayat + '_' + shopCode + '.html'
    logger.info('File Name:[%s]' % filename)
    
    if os.path.exists(filename):
      logger.info("Skipped [%s] as alread downloaded" % filename)
      continue

    url="http://khadya.cg.nic.in/pdsonline/cgfsa/Report/FrmRation_Patra_Allot_VerificationDistWise_Aug14.aspx"
    logger.info('URL: [%s]', url)
    
    driver.get(url)
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='drpdist']/option[@value='39']").click()
    driver.find_element_by_xpath("//select[@id='ddlUrban_Rural']/option[@value='R']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='ddlNNN_Block']/option[@value='"+pdsBlockCode+"']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='ddlShopName']/option[@value='"+shopCode+"']").click()
    time.sleep(delay)
    elem=driver.find_element_by_name("btnShowDetails")
    elem.click()
    time.sleep(delay)
    html_source = driver.page_source
    raw_html=html_source.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    with open(filename, "wb") as html_file:
      logger.info("Writing [%s]" % filename)
      html_file.write(raw_html.encode("UTF-8"))

    query='update shopMapping set downloadDate="%s", isDownloaded=1, isProcessed=0 where shopCode="%s"' % (strftime('%Y-%m-%d %H:%M:%S'), shopCode)
    logger.info('query: [%s]', query)
    cur=db.cursor()
    cur.execute(query)


def pdsReportParse(logger, db, dir=None):
  '''
  Parse the HTML Reports and populate the data in to the Surguja Database
  '''

  if not dir:
    dir = './reports'

  query="select b.pdsBlockCode,b.name,s.shopCode,m.panchayat from pdsShops s,blocks b, shopMapping m where b.blockCode=s.blockCode and s.shopcode = m.shopcode and m.isProcessed = 0"
  logger.info('query: [%s]', query)
  cur=db.cursor()
  cur.execute(query)
  results = cur.fetchall()
  logger.debug('results: [%s]', str(results))

  for row in results:
    (pdsBlockCode, blockName, shopCode, panchayat) = row
    logger.info('pdsBlockCode[%s], blockName[%s], shopCode[%s], panchayat[%s]' % (pdsBlockCode, blockName, shopCode, panchayat))
    filename = dir + '/'+ blockName + '_' + panchayat + '_' + shopCode + '.html'
    
    if not os.path.exists(filename):
      logger.info("Skipped [%s] as the file is missing!" % filename)
      continue

    with open(filename, 'r') as html_file:
      logger.info("Reading [%s]" % filename)
      html_source = html_file.read()

    bs = BeautifulSoup(html_source, "html.parser")

    span = bs.find('span', id='lblhead')
    hack = False
    if not span:
      span = bs.find('span', id='Label7')
      hack = True
      
    date_str = span.text.strip()
    logger.info("date_str[%s]" % date_str)

    year_index = date_str.find("201")
    year = date_str[year_index:year_index+4]
    logger.debug("year[%s]", year)
    maah_index = date_str.find("माह")
    if hack:
      month = date_str[:year_index].strip("माह").strip()
    else:
      month = date_str[:maah_index].strip()
    
    logger.debug("month[%s]", month)
    month_number = month2number[month]
    logger.debug("month_number[%d]", month_number)
    date_of_issue = year + "-%02d-" % month_number + "01"  # 1st of the Month - Date of the Report 
    logger.info("date_of_issue[%s]", date_of_issue)

    # Mynk To Add in future when cron is ready
    '''
    if date_of_issue is not now():
      logger.error("Something Amiss!")
    '''

    if hack:
      table = bs.find('table', id='GridView1')
    else:
      table = bs.find('table', id='grdPendingforRenewalDetails')

    row = table.find('tr')   # The row with headings 'th' skip this

    delimiter = "%" * 30
    logger.info("%s %s [%s] %s" % (delimiter, "Begin of File", filename, delimiter))
    
    while True:
      row = row.findNext('tr')
      logger.debug("row[%s]" % row)
      if not row:
        break
              
      delimiter = "$" * 30
      logger.info("%s %s %s" % (delimiter, "Begin of Ration Disbursement", delimiter))

      td = row.find('td') # Serial No Skip
      serial_no = td.text.strip()
      logger.info("serial_no[%s]", serial_no)
      
      td = td.findNext('td') # registration_no
      registration_no = td.text.strip()
      logger.info("registration_no[%s]", registration_no)

      td = td.findNext('td') # rationcard_no
      rationcard_no = td.text.strip()
      logger.info("rationcard_no[%s]", rationcard_no)

      td = td.findNext('td') # head_of_household
      head_of_household = td.text.strip()
      logger.info("head_of_household[%s]", head_of_household)

      td = td.findNext('td') # father_or_husband
      father_or_husband = td.text.strip()
      logger.info("father_or_husband[%s]", father_or_husband)
      if father_or_husband.find('\\') != -1:
        father_or_husband = father_or_husband.strip('\\')   # Mynk HACK FIXME
        logger.info("father_or_husband[%s]", father_or_husband)

      td = td.findNext('td') # rationcard_type
      rationcard_type = td.text.strip()
      logger.info("rationcard_type[%s]", rationcard_type)

      td = td.findNext('td') # zero_cost_type
      zero_cost_type = td.text.strip()
      logger.info("zero_cost_type[%s]", zero_cost_type)

      td = td.findNext('td') # no_of_familymembers
      no_of_familymembers = td.text.strip()
      logger.info("no_of_familymembers[%s]", no_of_familymembers)
      if no_of_familymembers == "-":
        no_of_familymembers = ""
        logger.info("Updating no_of_familymembers[%s]", no_of_familymembers)

      td = td.findNext('td') # allotment
      allotment = td.text.strip()
      logger.info("allotment[%s]", allotment)

      cur = db.cursor()
      query = 'insert into pdsCardHolders (registrationNo, rationCardNo, dateOfIssue, headOfHousehold, fatherOrHusband, rationCardType, zeroCostType) values ("%s", "%s", "%s", "%s", "%s", "%s", "\
%s")' % (registration_no, rationcard_no, date_of_issue, head_of_household, father_or_husband, rationcard_type, zero_cost_type)
      logger.info('Executing query[%s]' % query)
      try:
        cur.execute(query)
      except IntegrityError as e:
        logger.warning('Attempting Duplicate Entry[%s]', e)

      cur = db.cursor()
      query = 'insert into pdsEnrollment (rationcardNo, dateDisbursed, noOfFamilyMembers, allotment) values ("%s", "%s", "%s", "%s")' % (rationcard_no, date_of_issue, no_of_familymembers, allotment)
      logger.info('Executing query[%s]' % query)
      try:
        cur.execute(query)
      except IntegrityError as e:
        logger.warning('Updating Entry since[%s]', e)
        cur = db.cursor()
        query = 'update pdsEnrollment set rationcardNo="%s", dateDisbursed="%s", noOfFamilyMembers="%s", allotment="%s"' % (rationcard_no, date_of_issue, no_of_familymembers, allotment)
        logger.info('Executing query[%s]' % query)
        # Mynk ForNow cur.execute(query)

      delimiter = "$" * 30
      logger.info("%s %s %s" % (delimiter, "End of Ration Disbursement", delimiter))

    query='update shopMapping set processDate="%s", isDownloaded=0, isProcessed=1 where shopCode="%s"' % (strftime('%Y-%m-%d %H:%M:%S'), shopCode)
    logger.info('query: [%s]', query)
    cur=db.cursor()
    cur.execute(query)

      
    delimiter = "%" * 30
    logger.info("%s %s [%s] %s" % (delimiter, "End of File", filename, delimiter))
    


      
def pdsFetchPrev(logger, driver, db, dir=None, month=None, year=None):
  '''
  Crawl to the page for the khadya site and fecth the previous report for the given month & year
  '''
  
  if not dir:
    dir='./reports'

  if not month:
    month="3"

  if not year:
    year="2015"

  query="select b.pdsBlockCode,b.name,s.shopCode,m.panchayat from pdsShops s,blocks b, shopMapping m where b.blockCode=s.blockCode and s.shopcode = m.shopcode"
  logger.info('query: [%s]', query)
  cur=db.cursor()
  cur.execute(query)
  results = cur.fetchall()
  logger.debug('results: [%s]', str(results))

  for row in results:
    (pdsBlockCode, blockName, shopCode, panchayat) = row
    logger.info('pdsBlockCode[%s], blockName[%s], shopCode[%s], panchayat[%s]' % (pdsBlockCode, blockName, shopCode, panchayat))
    filename = dir + '/' + blockName + '_' + panchayat + '_' + shopCode + '.html'
    logger.info('File Name:[%s]' % filename)
    
    if os.path.exists(filename):
      logger.info("Skipped [%s] as alread downloaded" % filename)
      continue

    if shopCode == "0":
      continue

    url="http://khadya.cg.nic.in/rationcards/RationFC/RptShow_PreviousAllot_ShopWise.aspx"
    logger.info('URL: [%s]', url)

    driver.get(url)
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='DDdist']/option[@value='39']").click()
    driver.find_element_by_xpath("//select[@id='DDUR']/option[@value='R']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='DDBlock_NNN']/option[@value='" + pdsBlockCode + "']").click()
    time.sleep(delay)
    logger.info("Shopcode[" + shopCode + "]")
    driver.find_element_by_xpath("//select[@id='DDShop']/option[@value='" + shopCode + "']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='DDYear']/option[@value='" + year + "']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='DDMonth']/option[@value='" + month + "']").click()
    time.sleep(delay)
    elem=driver.find_element_by_name("Button1")
    elem.click()
    time.sleep(delay)
    html_source = driver.page_source
    raw_html=html_source.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    with open(filename, "wb") as html_file:
      logger.info("Writing [%s]" % filename)
      html_file.write(raw_html.encode("UTF-8"))

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")

  db = dbInitialize(db="surguja", charset="utf8")

  if not args['parse']:
    display = displayInitialize(args['visible'])
    driver = driverInitialize(args['browser'])

  if args['visible']:
    delay = 2

  if args['prev']:
    pdsFetchPrev(logger, driver, db, args['directory'], args['month'], args['year'])
  elif args['parse']:
    pdsReportParse(logger, db, args['directory'])
  elif args['work-allocation']:
    downloadWorkAllocationHTML(driver, db, logger) # Mynk Fix Order
  else:
    pdsFetch(logger, driver, db, args['directory'])

  if not args['parse']:
    driverFinalize(driver)
    displayFinalize(display)

  dbFinalize(db)

  logger.info("...END PROCESSING")
  exit(0)

if __name__ == '__main__':
  main()
