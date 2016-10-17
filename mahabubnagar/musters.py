#! /usr/bin/env python

from bs4 import BeautifulSoup
from time import strftime,strptime

import sys
if sys.version_info[0] > 2:
  import pymysql
  pymysql.install_as_MySQLdb()
import MySQLdb     
from MySQLdb import IntegrityError

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize
from wrappers.db import dbInitialize,dbFinalize


#######################
# Global Declarations
#######################

state_code = '36'
district_code = '14'
block_code = '057'

state_name = ''
disttict_name = ''
block_name = 'Ghattu'

#############
# Functions
#############
  
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--timeout', help='Time to wait before a page loads', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-u', '--url', help='Specify the url to crawl', required=False)
  parser.add_argument('-d', '--directory', help='Specify directory to download html file to', required=False)
  parser.add_argument('-q', '--query', help='Query to specify the workset, E.g ... where id=147', required=False)
  parser.add_argument('-j', '--jobcard', help='Specify the jobcard to download/push', required=False)
  parser.add_argument('-c', '--crawl', help='Crawl the Disbursement Data', required=False)
  parser.add_argument('-f', '--fetch', help='Fetch the Jobcard Details', required=False)
  parser.add_argument('-p', '--parse', help='Parse Jobcard HTML for Muster Info', required=False, action='store_const', const=True)
  parser.add_argument('-r', '--process', help='Process downloaded HTML files for Muster Info', required=False, action='store_const', const=True)
  parser.add_argument('-P', '--push', help='Push Muster Info into the DB on the go', required=False, action='store_const', const=True)
  parser.add_argument('-J', '--jobcard-details', help='Fetch the Jobcard Details for DB jobcardDetails table', required=False, action='store_const', const=True)

  args = vars(parser.parse_args())
  return args

def dateConvert(date):
  if date == '-':
    return None
  return strftime('%Y-%m-%d %H:%M:%S', (strptime(date, '%d-%b-%Y')))

def dateConvert2(date):
  if date == '-':
    return None
  return strftime('%Y-%m-%d %H:%M:%S', (strptime(date, '%d-%b-%Y %H:%M:%S %p')))

def lookupInitializePanchayats(logger, db):
  cur = db.cursor()

  query = 'select name, panchayatCode from panchayats'
  logger.info('query[%s]' % query)
  cur.execute(query)
  panchayat_mapping = cur.fetchall()
  logger.debug('mapping tupple[%s]' % str(panchayat_mapping))
  
  return dict((panchayat, panchayatCode) for panchayat, panchayatCode in panchayat_mapping)


def lookupInitialize(logger):
  db = dbInitialize(host=dbhost, user=dbuser, passwd=dbpasswd, db="mahabubnagar")
  cur = db.cursor()

  query = 'select name, jobcardPrefix from panchayats'
  logger.info('query[%s]' % query)
  cur.execute(query)
  jobcard_mapping = cur.fetchall()
  logger.debug('mapping tupple[%s]' % str(jobcard_mapping))
  
  dbFinalize(db)
  return dict((panchayat, jobcardPrefix) for panchayat, jobcardPrefix in jobcard_mapping)


def downloadJobcardHTML(logger, driver, db, jobcard, dirname=None):
  '''
  Download the Jobcard HTML with payment info (Muster Details)
  '''
  if not dirname:
    dirname = './musters'
  logger.info("dirname[%s]", dirname)
  
  if not os.path.exists(dirname):
    os.makedirs(dirname)

  filename = dirname + '/' + jobcard + '.html'
  
  jobcard_url = 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=HouseholdInf_engRH&actionVal=SearchJOB&JOB_No='
  url = jobcard_url + jobcard

  logger.info("Fetching...[%s]" % url)
  driver.get(url)
  logger.info("Fetched [%s]" % driver.title)

  if driver.title != ':: Job Card Holders Information ::':
    logger.info("Refreshing...[%s]" % url)
    driver.get(url)    # A double refresh required for the page to load
    logger.info("Refreshed [%s]" % driver.title) 

  html_source = driver.page_source.replace('<head>',
                                         '<head><meta http-equiv="Content-Type" '
                                          'content="text/html; charset=utf-8"/>').encode('utf-8')
  logger.debug("HTML Fetched [%s]" % html_source)

  bs = BeautifulSoup(html_source, "html.parser")
  span = bs.find('span',attrs={'class':'rpt-hd-txt'})
  if not span:
    logger.error("Span not found for jobcard[%s]" % (jobcard))
    return None

  query = None
  ''' Update Only if there is a change for Google Drive will sync '''
  if os.path.exists(filename):
    with open(filename, 'r+') as html_file:
      cur_source = html_file.read()
      bs2 = BeautifulSoup(cur_source, "html.parser")
      
      if (bs.find(id='main3') != bs2.find(id='main3')):
        html_file.seek(0)
        html_file.write(html_source)
        html_file.truncate()
        logger.info("Updating [%s]" % filename)
      else:
        logger.info("Skipping as no update")
        query = 'update jobcardRegister set downloadDate="%s", isDownloaded=1 where jobcard="%s"' % (strftime('%Y-%m-%d %H:%M:%S'), jobcard)
  else:
    with open(filename, 'w') as html_file:
      logger.info("Writing [%s]" % filename)
      html_file.write(html_source)

  if not query:
    query = 'update jobcardRegister set downloadDate="%s", isDownloaded=1, isProcessed=0 where jobcard="%s"' % (strftime('%Y-%m-%d %H:%M:%S'), jobcard)
  logger.info('Executing query: [%s]', query)
  cur = db.cursor()
  cur.execute(query)

  return html_source


def pushMusterInfo(logger, db, html_source, jobcard, panchayat_code=None, fetch_jobcard_details=None):
  '''
  Parse & Push the Muster Info into the DB
  '''
  bs = BeautifulSoup(html_source, "html.parser")
  span = bs.find('span',attrs={'class':'rpt-hd-txt'})
  if not span:
    logger.error("Span not found for jobcard[%s] panchayat_code[%s]" % (jobcard, panchayat_code))
    return
  
  txt = span.text.strip()
  logger.debug("Span[%s]" % txt)
  panchayat = txt[txt.find('Panchayat')+len('Panchayat :'):txt.find('Habitation')].strip() #Mynk 
  logger.info("Panchayat[%s]" % panchayat)

  if not panchayat_code:
    panchayat_code = lookupPanchayatCode[panchayat]

  if fetch_jobcard_details:
    main1 = bs.find('div',id='main1')
    logger.debug("Main1[%s]" % main1)

    if main1 != None:
      table1 = main1.find('table')
      logger.debug("Table1[%s]" % table1)

      table1A = table1.find('table', id='sortable')
      logger.debug("Table1A[%s]" % table1A)

      table1B = table1A.findNext('table', id='sortable')
      logger.debug("Table1B[%s]" % table1B)

      rows = table1B.findAll('tr')
      hrow = rows[0]
      count = len(rows)
      logger.info("RowCount[%d]" % count)
      logger.debug("Row[%s]" % rows)
      if count > 3:
        th = str(hrow.find('th'))
        logger.debug("HeadRow[%s]" % hrow)
        count = count-3
        
        row = rows[3]
        logger.debug("FirstRow[%s]" % row)

        while count != 0:
          count = count - 1
          td = row.find('td')
          td = td.findNext('td')
          worker_id_value = td.text
          worker_id = worker_id_value.strip()
          logger.debug("worker_id [%s]" % worker_id)

          td = td.findNext('td')
          worker_name_value = td.text
          worker_name = worker_name_value.strip()
          logger.debug("worker_name [%s]" % worker_name)

          td = td.findNext('td')
          age_value = td.text
          age = age_value.strip()
          logger.debug("age [%s]" % age)
          if age == '-':
            age = ""

          td = td.findNext('td')
          gender_value = td.text
          gender = gender_value.strip()
          logger.debug("gender [%s]" % gender)

          td = td.findNext('td')
          relationship_value = td.text
          relationship = relationship_value.strip()
          logger.debug("relationship [%s]" % relationship)

          td = td.findNext('td')
          account_no_value = td.text
          account_no = account_no_value.strip()
          logger.debug("account_no [%s]" % account_no)

          td = td.findNext('td')
          paying_agency_value = td.text
          paying_agency = paying_agency_value.strip()
          logger.debug("paying_agency [%s]" % paying_agency)

          td = td.findNext('td')
          ifsc_code_value = td.text
          ifsc_code = ifsc_code_value.strip()
          logger.debug("ifsc_code [%s]" % ifsc_code)

          td = td.findNext('td')
          branch_value = td.text
          branch = branch_value.strip()
          logger.debug("branch [%s]" % branch)

          td = td.findNext('td')
          uid_no_value = td.text
          uid_no = uid_no_value.strip()
          logger.debug("uid_no [%s]" % uid_no)

          td = td.findNext('td')
          shg_id_value = td.text
          shg_id = shg_id_value.strip()
          logger.debug("shg_id [%s]" % shg_id)

          td = td.findNext('td')
          disabled_value = td.text
          disabled = disabled_value.strip()
          logger.debug("disabled [%s]" % disabled)
          
          if disabled == "N":
            is_disabled = 0
          else:
            is_disabled = 1
          logger.debug("disabled [%s]" % is_disabled)

          cur = db.cursor()
          query = 'insert into jobcardDetails (jobcard, applicantNo, age, applicantName, gender, accountNo, aadharNo, bankNameOrPOName, IFSCCodeOrEMOCode, branchNameOrPOAddress, isDisabled) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (jobcard, worker_id, age, worker_name, gender, account_no, uid_no, paying_agency, ifsc_code, branch, is_disabled) + ' ON DUPLICATE KEY update jobcard="%s", applicantNo="%s", age="%s", applicantName="%s", gender="%s", accountNo="%s", aadharNo="%s", bankNameOrPOName="%s", IFSCCodeOrEMOCode="%s", branchNameOrPOAddress="%s", isDisabled="%s"' % (jobcard, worker_id, age, worker_name, gender, account_no, uid_no, paying_agency, ifsc_code, branch, is_disabled)
          logger.info('Executing query[%s]' % query)
          try:
            cur.execute(query)
          except IntegrityError as e:
            logger.warning('Attempting Duplicate Entry[%s]', e)

          try:
            row = row.findNext('tr')
          except StopIteration:
            break


  # The logic to get muster information begins here
          
  main3 = bs.find(id='main3')
  if main3 == None:
    return
  table3 = main3.find('table')
  # logger.debug("Table2[%s]" % table3)
  header_row = table3.find('tr')
  row = header_row.findNext('tr')

  while True:
    td = row.find('td')
    epay_order_value = td.text
    epay_order_number = epay_order_value.strip()
    logger.debug("Epayorder No[%s]", epay_order_number)
    if False: # Disable this check - len(epay_order_number) != 16:
      logger.debug('Reached End of Table with epay_order_number[%s]' % epay_order_number)
      break

    td = td.findNext('td')
    ftr_no = td.text.strip()
    logger.debug("Ftr No[%s]", ftr_no)

    td = td.findNext('td')
    muster_number = td.text.strip()
    logger.debug("musterNo[%s]", muster_number)

    if muster_number == "Works Benifited": # Mynk Gone to the next table - end loop
      break;

    financial_year = 0
    if muster_number == '-':
      logger.debug('Invalid Muster Number[%s]' % muster_number)
    else:
      financial_year = muster_number[4:6]
      if financial_year == "51":  # For Muster Numbers beginning with 8 #HACK
        financial_year = muster_number[5:7]
      if len(muster_number) != 12: # Highlight differently numbered Musters
        logger.debug('Invalid Muster Number[%s] due to LENGTH' % muster_number)
    logger.debug("financial_year[%s]", financial_year)

    td = td.findNext('td')
    from_date = td.text.strip()
    logger.debug("From Date[%s]", from_date)
    from_date = dateConvert(from_date)
    logger.debug("From Date[%s]", from_date)

    td = td.findNext('td')
    to_date = dateConvert(td.text.strip())
    logger.debug("To Date[%s]", to_date)

    td = td.findNext('td')
    payorder_date = dateConvert(td.text.strip())
    logger.debug("Payorder Date[%s]", payorder_date)
    if not payorder_date:
      logger.error("Found null pay order date example")
    elif muster_number == '-':
      date_str = str(payorder_date)
      fin_year = int(date_str[2:4])
      month = int(date_str[5:7])
      if month > 3:
        fin_year += 1
        muster_number = "20" + str(fin_year-1) + str(fin_year) + "000000"

      financial_year = str(fin_year);
      logger.info('Updating Muster Number[%s], financial_year[%s]' % (muster_number, financial_year))

    td = td.findNext('td')
    work = td.text.strip()
    logger.debug("work[%s]", work)
    if work == '-':
      work = '/'
    if work != '/':
      (work_code, work_name) = work.split(' / ')
      work_name = work_name.replace('"', "'")  # Double Quote Issue E.g - MusterNo[20151632245] JobCard[141975708009010192]
    else:
      (work_code, work_name) = ("", "")
    logger.info("work_code[%s] work_name[%s]", work_code, work_name)

    td = td.findNext('td')
    payorder_number = td.text.strip()
    logger.debug("payorder_number[%s]", payorder_number)

    td = td.findNext('td')
    wageseeker_name = td.text.strip()
    logger.debug("wageseeker_name[%s]", wageseeker_name)

    td = td.findNext('td')  # Skip Caste
    caste = td.text.strip()
    logger.debug("caste[%s]", caste)

    td = td.findNext('td')
    account_number = td.text.strip()
    logger.debug("account_number[%s]", account_number)

    td = td.findNext('td')
    days_worked = td.text.strip()
    logger.debug("days_worked[%s]", days_worked)
    
    if days_worked == '-':  # Needs to go? Mynk
      days_worked = "0"
    logger.debug("Updated days_worked[%s]", days_worked)

    td = td.findNext('td')
    payorder_amount = td.text.strip()
    logger.debug("payorder_amount[%s]", payorder_amount)

    if days_worked != "0":
      day_wage = int(payorder_amount)/int(days_worked)
    else:
      day_wage = int(payorder_amount)   # Mynk days_worked can be 0 as in http://crawl.libtech.info/data/Telangana/Mahabubnagar/Ghattu/Nandinne/141975701001010236.html

    td = td.findNext('td')
    credit_date = td.text.strip()
    logger.debug("credit_date[%s]", credit_date)
    credit_date = dateConvert(credit_date)
    if not credit_date:
      logger.warning("Credit Date messed")
      
    td = td.findNext('td')
    disbursed_amount = td.text.strip()
    logger.debug("disbursed_amount[%s]", disbursed_amount)

    td = td.findNext('td')
    disbursed_date = td.text.strip()
    logger.debug("disbursed_date[%s]", disbursed_date)
    disbursed_date = dateConvert2(disbursed_date)
    if not disbursed_date:
      logger.warning("Disbursed Date messed")

    cur = db.cursor()
    query = 'insert into musters (musterNo, stateCode, districtCode, blockCode, panchayatCode, finyear, workCode, workName, dateFrom, dateTo, crawlDate) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (muster_number, state_code, district_code, block_code, panchayat_code, financial_year, work_code, work_name, from_date, to_date, strftime('%Y-%m-%d %H:%M:%S'))
    logger.info('Executing query[%s]' % query)
    try:
      cur.execute(query)
    except IntegrityError as e:
      logger.warning('Attempting Duplicate Entry[%s]', e)

    cur = db.cursor()
    query = 'insert into musterTransactionDetails (musterNo, finyear, workCode, name, jobcard, daysWorked, dayWage, totalWage, accountNo, wagelistNo, creditedDate, blockCode, panchayatCode, stateCode, districtCode, disbursedAmount, disbursedDate, referenceNoEPayorderNo) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (muster_number, financial_year, work_code, wageseeker_name, jobcard, days_worked, day_wage, payorder_amount, account_number, payorder_number, credit_date, block_code, panchayat_code, state_code, district_code, disbursed_amount, disbursed_date, epay_order_number) + ' ON DUPLICATE KEY update finyear="%s", workCode="%s", daysWorked="%s", dayWage="%s", totalWage="%s", accountNo="%s", wagelistNo="%s", creditedDate="%s", blockCode="%s", panchayatCode="%s", stateCode="%s", districtCode="%s", disbursedAmount="%s", disbursedDate="%s", referenceNoEPayorderNo="%s"' % (financial_year, work_code, days_worked, day_wage, payorder_amount, account_number, payorder_number, credit_date, block_code, panchayat_code, state_code, district_code, disbursed_amount, disbursed_date, epay_order_number)
    logger.info('Executing query[%s]' % query)
    try:
      cur.execute(query)
    except IntegrityError as e:
      logger.warning('Attempting Duplicate Entry[%s]', e)
      
    try:
      row = row.findNext('tr')
    except StopIteration:
      break

  cur = db.cursor()
  query = 'update jobcardRegister set isProcessed=1 where jobcard="%s"' % (jobcard)
  logger.info('Executing query[%s]' % query)
  cur.execute(query)    

    
from datetime import timedelta,date

def daterange(start_date, end_date):
  for n in range(int ((end_date - start_date).days)):
    yield start_date + timedelta(n)
    
def downloadDibsursementReport(logger, driver, cmd=None, dir=None, url=None, date=None):
  '''
  Crawl the html for the musters
  '''
  if cmd == None:
    cmd="CRAWLING"
    
  if dir == None:
    dir = "./html"

  if url == None:
    url = 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=SmartCardreport_engRH&actionVal=debitLoagReport&id=1457@DOP$APOL&type=[DATE]&listType='
    #url = "http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=SmartCardreport_engRH&actionVal=debitLoagReport&id=1457@DOP$APOL&type=01/04/2015&listType="
    #url = "http://www.nrega.telangana.gov.in/"

  if not date:
    date='01/04/2015'
    
  url = url.replace('[DATE]', date)

  logger.info("BEGIN %s..." % cmd)

  logger.info("Command[%s] Directory[%s] URL[%s]" % (cmd, dir, url))

  driver.get(url)
  logger.info("Fetching...[%s]" % url)
  
  driver.get(url)    # A double refresh required for the page to load
  logger.info("Refreshing...[%s]" % url)
  
  html_source = driver.page_source.replace('<head>',
                                           '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
  logger.debug("HTML Fetched [%s]" % html_source)

  bs = BeautifulSoup(html_source, "html.parser")
  tr_list = bs.findAll('tr', attrs={'class':['normalRow', 'alternateRow']})
  logger.debug(str(tr_list))

  for tr in tr_list:
    td = tr.find('td')
    td = td.findNext('td')
    panchayat = td.text.strip()
    logger.info("Panchayat[%s]", panchayat)

    elem = driver.find_element_by_link_text(panchayat)
    elem.click()
    
    filename= dir + '/%s_' % date.replace('/','-') + panchayat + '.html'
    with open(filename, 'w') as html_file:
      logger.info("Writing [%s]" % filename)
      html_file.write(driver.page_source.encode('utf-8'))

    driver.back()

  logger.info("...END %s" % cmd)     

def fetchJobcardDetails(logger, driver, cmd=None, dir=None, url=None):
  '''
  Crawl the html for the musters
  '''
  if cmd == None:
    cmd="Downloading"
    
  if dir == None:
    dir = "./html"

  if url == None:
    url = 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=HouseholdInf_engRH&actionVal=SearchJOB&JOB_No='
  url_source = url

  jobcardPrefix = lookupInitialize(logger)
  logger.info('mapping dictionary[%s]' % str(jobcardPrefix))  

  logger.info("BEGIN %s..." % cmd)

  logger.info("Command[%s] Directory[%s] URL[%s]" % (cmd, dir, url))

  import os
  files = os.listdir(dir)

  for f in files:
    filename = dir + '/' + f
    
    date = filename[7:17]
    with open(filename, 'r') as html_file:
      logger.info("Reading [%s]" % filename)
      html_source = html_file.read()

    bs = BeautifulSoup(html_source, "html.parser")
    tr_list = bs.findAll('tr', attrs={'class':['normalRow', 'alternateRow']})
    logger.debug(str(tr_list))

    for tr in tr_list:
      td = tr.find('td')
      td = td.findNext('td')
      panchayat = td.text.strip().capitalize()
      logger.info("Panchayat[%s]", panchayat)
      if panchayat not in jobcardPrefix:
        logger.info("Missing[%s]", panchayat)
        continue
      
      td = td.findNext('td')
      ePayorderNumber = td.text.strip()
      logger.info("EPayorderNumber[%s]", ePayorderNumber)

      td = td.findNext('td')
      ePayOrderCreationDate = td.text.strip()
      logger.info("EPayOrderCreationDate[%s]", ePayOrderCreationDate)

      td = td.findNext('td')
      ePayOrderSentDate = td.text.strip()
      logger.info("EPayOrderSentDate[%s]", ePayOrderSentDate)

      td = td.findNext('td')
      UID = td.text.strip()
      logger.info("UID[%s]", UID)

      td = td.findNext('td')
      payorderNumber = td.text.strip()
      logger.info("payorderNumber[%s]", payorderNumber)

      td = td.findNext('td')
      jobcard = jobcardPrefix[panchayat] + td.text.strip()
      logger.info("jobcard[%s]", jobcard)

#      filename= './jobcards/'+ date + '_' + panchayat + '_' + jobcard + '.html'
      filename= './jobcards/' + jobcard + '.html'
      if os.path.exists(filename):
        logger.info("Skipping [%s]", filename)
        continue

      url = url_source + jobcard

      driver.get(url)
      logger.info("Fetching...[%s]" % url)
    
      driver.get(url)    # A double refresh required for the page to load
      logger.info("Refreshing...[%s]" % url)
    
      html_source = driver.page_source.replace('<head>',
                                             '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
      logger.debug("HTML Fetched [%s]" % html_source)

  #    elem = driver.find_element_by_link_text(panchayat)
  #    elem.click()

  #    filename= dir + '/%s_' % date.replace('/','-') + panchayat + '.html'

      with open(filename, 'w') as html_file:
        logger.info("Writing [%s]" % filename)
        html_file.write(driver.page_source.encode('utf-8'))

      driver.back()
    
  logger.info("...END %s" % cmd)     

def downloadJobcards(logger, db, cmd=None, directory=None, url=None, isVisible=None, isPushInfo=None, query=None, fetch_jobcard_details=None):
  '''
  Crawl the html for the musters
  '''
  logger.info("BEGIN %s..." % cmd)

  if cmd == None:
    cmd="Downloading"
    
  if directory == None:
    directory = "./jobcards"

  if url == None:
    url = 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=HouseholdInf_engRH&actionVal=SearchJOB&JOB_No='

  if isVisible == None:
    isVisible = 0

  if isPushInfo == None:
    isPushInfo = False

  logger.info("Command[%s] Directory[%s] URL[%s]" % (cmd, directory, url))
    
  if not query:
    # Mynk - use when b.name is not all 'Ghattu'  query = 'select j.jobcard, p.name, b.name from jobcardRegister j, panchayats p, blocks b where j.blockCode=p.blockCode and j.panchayatCode=p.panchayatCode  and j.blockCode=b.blockCode'
    query = 'select j.jobcard, p.name, p.panchayatCode from jobcardRegister j, panchayats p, blocks b where j.blockCode=p.blockCode and j.panchayatCode=p.panchayatCode  and j.blockCode=b.blockCode and DATE_SUB(NOW(), INTERVAL 1 DAY) >= downloadDate order by j.downloadDate'

  logger.info('Executing query: [%s]', query)
  cur = db.cursor()
  cur.execute(query)
  jobcard_details = cur.fetchall()
  if jobcard_details:
    logger.debug("Jobcard Details [%s]" % str(jobcard_details))
  
  display = displayInitialize(isVisible)
  driver = driverInitialize()

  for (jobcard, panchayat, panchayat_code) in jobcard_details:
    logger.info( "jobcard[%s] panchayat[%s] panchayat_code[%s]" % (jobcard, panchayat, panchayat_code))
    dirname = directory + '/' + panchayat    
    html_source = downloadJobcardHTML(logger, driver, db, jobcard, dirname)

    if isPushInfo or fetch_jobcard_details:
      if html_source:
        pushMusterInfo(logger, db, html_source, jobcard, panchayat_code, fetch_jobcard_details)
      else:
        query = 'update jobcardRegister set isDownloaded=0 where jobcard="%s"' % (jobcard) # Mynk
        logger.info('Executing query: [%s]', query)
        cur = db.cursor()
        cur.execute(query)

  driverFinalize(driver)
  displayFinalize(display)

  logger.info("...END %s" % cmd)     

def processMusterInfo(logger, db, cmd=None, dir=None):
  '''
  Parse the Jobcard HTML for Muster Info
  '''
  if cmd == None:
    cmd="PROCESSING"
    
  if dir == None:
    dir = "./jobcards"

  lookupPanchayatCode = lookupInitializePanchayats(logger, db)
  logger.info('mapping dictionary[%s]' % str(lookupPanchayatCode))

  logger.info("BEGIN %s..." % cmd)

  logger.info("Command[%s] Directory[%s]" % (cmd, dir))

  import glob
  files = glob.glob(dir + '/*/*.html')
  logger.debug('files[%s]' % files)

  for abs_filename in files:
    dirname = os.path.dirname(abs_filename)
    panchayat = os.path.basename(dirname)
    panchayat_code = lookupPanchayatCode[panchayat]
    jobcard = os.path.basename(abs_filename).strip('.html')
    filename = abs_filename
    logger.info("filename[%s], jobcard[%s], panchayat[%s], panchayat_code[%s]" % (filename, jobcard, panchayat, panchayat_code))

    with open(filename, 'r') as html_file:
      logger.info("Reading [%s]" % filename)
      html_source = html_file.read()

    pushMusterInfo(logger, db, html_source, jobcard, panchayat_code)

  logger.info("...END %s" % cmd)     

def parseMusterInfo(logger, db, cmd=None, directory=None, query=None, fetch_jobcard_details=None):
  '''
  Parse the Jobcard HTML for Muster Info
  '''
  if cmd == None:
    cmd="PROCESSING"
    
  if directory == None:
    directory = "./jobcards"

  logger.info("BEGIN %s..." % cmd)

  logger.info("Command[%s] Directory[%s]" % (cmd, directory))

  if query == None:
    query = 'select j.jobcard, p.name, p.panchayatCode from jobcardRegister j, panchayats p, blocks b where j.blockCode=p.blockCode and j.panchayatCode=p.panchayatCode  and j.blockCode=b.blockCode and j.isProcessed=0'

  logger.info('Executing query: [%s]', query)
  cur = db.cursor()
  cur.execute(query)
  jobcard_details = cur.fetchall()
  
  for (jobcard, panchayat, panchayat_code) in jobcard_details:
    logger.info( "jobcard[%s] panchayat[%s] panchayat_code[%s]" % (jobcard, panchayat, panchayat_code))
    dirname = directory + '/' + panchayat        
    filename = dirname + '/' + jobcard + '.html'
    logger.info("filename[%s], jobcard[%s], panchayat[%s], panchayat_code[%s]" % (filename, jobcard, panchayat, panchayat_code))

    if not os.path.exists(filename):
      logger.error('File Not downloaded [%s]' % filename)
      continue
    
    with open(filename, 'r') as html_file:
      logger.info("Reading [%s]" % filename)
      html_source = html_file.read()

    pushMusterInfo(logger, db, html_source, jobcard, panchayat_code, fetch_jobcard_details)

  logger.info("...END %s" % cmd)     

  
def fetchJobcard(logger, db, jobcard, cmd=None, dir=None, url=None, isVisible=None, isPushInfo=None):
  '''
  Fetch the Jobcard Details for specified jobcard number
  '''
  logger.info("BEGIN %s..." % cmd)

  if cmd == None:
    cmd="FETCH JOBCARD"
    
  if dir == None:
    dir = "./jobcards"

  if url == None:
    url = 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=HouseholdInf_engRH&actionVal=SearchJOB&JOB_No=' + jobcard

  if isVisible == None:
    isVisible = 0

  if isPushInfo == None:
    isPushInfo = False

  query = 'select j.jobcard, p.name, p.panchayatCode from jobcardRegister j, panchayats p, blocks b where j.blockCode=p.blockCode and j.panchayatCode=p.panchayatCode  and j.blockCode=b.blockCode and j.jobcard="%s"' % jobcard

  logger.info("Command[%s] Directory[%s] URL[%s] jobcard[%s]" % (cmd, dir, url, jobcard))

  downloadJobcards(logger, db, "DOWNLOAD JOBCARDS", dir, url, isVisible, isPushInfo, query)
  
  logger.info("...END %s" % cmd)     


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")

  outdir = args['directory']
  url = args['url']
  fetch_jobcard_details = args['jobcard_details']

  if args['crawl']: #Mynk
    start_date = date(2015, 4, 1)
    end_date = date(2015, 8, 19)
  
    for day in daterange(start_date, end_date):
      downloadDibsursementReport(logger, driver, "CRAWLING", outdir, url, day.strftime("%d/%m/%Y"))
  
  if args['fetch']: #Mynk
    fetchJobcardDetails(logger, driver, "DOWNLOAD JOBCARDS", outdir, url)

  db = dbInitialize(db="mahabubnagar")
  
  if args['parse']:
    parseMusterInfo(logger, db, "PARSE MUSTERS", outdir, args['query'], fetch_jobcard_details)
  elif args['process']:
    processMusterInfo(logger, db, "PROCESS MUSTERS", outdir)
  elif args['jobcard']:
    fetchJobcard(logger, db, args['jobcard'], "FETCH JOBCARD", outdir, url, args['visible'], args['push'])
  else:
    downloadJobcards(logger, db, "DOWNLOAD JOBCARDS", outdir, url, args['visible'], args['push'], args['query'], fetch_jobcard_details)

  dbFinalize(db)


  logger.info("...END PROCESSING")


  exit(0)

if __name__ == '__main__':
  main()
