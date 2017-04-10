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
#  "जनवरी":1, "फरवरी":2, "मार्च":3, "अप्रैल":4, "मई":5, "जून":6, "जुलाई":7, "अगस्त":8, "सितम्बर":9, "अक्टूबर":10, "नवम्बर":11, "दिसम्बर":12
#  "जनवरी":1, "फरवरी":2, "मार्च":3, "अप्रैल":4, "मई":5, "जून":6, "जुलाई":7, "अगस्त":8, "सितंबर":9, "अक्टूबर":10, "नवम्बर":11, "दिसंबर":12
  "जनवरी":1, "फरवरी":2, "मार्च":3, "अप्रैल":4, "मई":5, "जून":6, "जुलाई":7, "अगस्त":8, "सितंबर":9, "अक्टूबर":10, "नवम्बर":11, "दिसम्बर":12
}

blockSelectCode = {
  'UDAIPUR':'1', 'BATAULI':'2', 'MAINPAT':'3', 'LAKHANPUR':'4', 'LUNDRA':'5', 'AMBIKAPUR':'6', 'SITAPUR':'7'
}

shopSelectCode = {
  #Udaipur shopCode Mapping
  "392005001":"1",
  "392005002":"2",
  "392005003":"3",
  "392005004":"4",
  "392005005":"5",
  "392005006":"6",
  "392005007":"7",
  "392005008":"8",
  "392005009":"9",
  "392005010":"10",
  "392005011":"11",
  "392005012":"12",
  "392005013":"13",
  "392005014":"14",
  "392005015":"15",
  "392005016":"16",
  "392005017":"17",
  "392005018":"18",
  "392005019":"19",
  "392005020":"20",
  "392005021":"21",
  "392005022":"22",
  "392005023":"23",
  "392005024":"24",
  "392005025":"25",
  "392005026":"26",
  "392005027":"27",
  "392005028":"28",
  "392005029":"29",
  "392005030":"30",
  "392005031":"31",
  "392005032":"32",
  "392005033":"33",
  "392005034":"34",
  "392005035":"35",
  "392005036":"36",
  "392005037":"37",
  "392005038":"38",
  "392005039":"39",
  "392005040":"40",
  "392005041":"41",
  "392005042":"42",
  "392005043":"43",
  "392005044":"44",
  "392005045":"45",
  "392005046":"46",
  "392005047":"47",
  "392005048":"48",
  "392005049":"49",
  "392005050":"50",
  "392005051":"51",
  "392005052":"52",
  "392005053":"53",

  #Batauli shopCode Mapping
  "392004001":"1",
  "392004002":"2",
  "392004003":"3",
  "392004004":"4",
  "392004005":"5",
  "392004006":"6",
  "392004007":"7",
  "392004008":"8",
  "392004009":"9",
  "392004010":"10",
  "392004011":"11",
  "392004012":"12",
  "392004013":"13",
  "392004014":"14",
  "392004015":"15",
  "392004016":"16",
  "392004017":"17",
  "392004018":"18",
  "392004019":"19",
  "392004020":"20",
  "392004021":"21",
  "392004022":"22",
  "392004023":"23",
  "392004024":"24",
  "392004025":"25",
  "392004026":"26",
  "392004027":"27",
  "392004028":"28",
  "392004029":"29",
  "392004030":"30",
  "392004031":"31",
  "392004032":"32",
  "392004033":"33",
  "392004034":"34",
  "392004035":"35",
  "392004036":"36",
  "392004037":"37",
  "392004038":"38",
  "392004039":"39",
  "392004040":"40",

  #Lundra shopCode Mapping
  "392007001":"1",
  "392007002":"2",
  "392007003":"3",
  "392007004":"4",
  "392007005":"5",
  "392007006":"6",
  "392007007":"7",
  "392007008":"8",
  "392007009":"9",
  "392007010":"10",
  "392007011":"11",
  "392007012":"12",
  "392007013":"13",
  "392007014":"14",
  "392007015":"15",
  "392007016":"16",
  "392007017":"17",
  "392007018":"18",
  "392007019":"19",
  "392007020":"20",
  "392007021":"21",
  "392007022":"22",
  "392007023":"23",
  "392007024":"24",
  "392007025":"25",
  "392007026":"26",
  "392007027":"27",
  "392007028":"28",
  "392007029":"29",
  "392007030":"30",
  "392007031":"31",
  "392007032":"32",
  "392007033":"33",
  "392007034":"34",
  "392007035":"35",
  "392007036":"36",
  "392007037":"37",
  "392007038":"38",
  "392007039":"39",
  "392007040":"40",
  "392007041":"41",
  "392007042":"42",
  "392007043":"43",
  "392007044":"44",
  "392007045":"45",
  "392007046":"46",
  "392007047":"47",
  "392007048":"48",
  "392007049":"49",
  "392007050":"50",
  "392007051":"51",
  "392007052":"52",
  "392007053":"53",
  "392007054":"54",
  "392007055":"55",
  "392007056":"56",
  "392007057":"57",
  "392007058":"58",
  "392007059":"59",
  "392007060":"60",
  "392007061":"61",
  "392007062":"62",
  "392007063":"63",
  "392007064":"64",
  "392007065":"65",
  "392007066":"66",
  "392007067":"67",
  "392007068":"68",
  "392007069":"69",
  "392007070":"70",
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
  parser.add_argument('-f', '--fetch', help='Fetch the pds reports for all districts', required=False, action='store_const', const=True)

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


def pdsFetchReports(logger, driver, db, dir=None):
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

    url='http://khadya.cg.nic.in/pdsonline/cgfsa/Report/SSRS_Reports/RptMonthWiseDeleteRestoreNew_RC.aspx'
    logger.info('URL: [%s]', url)

    start_date = '4/1/2015'
    end_date = '1/20/2016'  # Mynk Need to Test
    end_date = '12/31/2015'
    
    driver.get(url)
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='ReportViewer1_ctl00_ctl03_ddValue']/option[@value='26']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='ReportViewer1_ctl00_ctl05_ddValue']/option[@value='2']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='ReportViewer1_ctl00_ctl07_ddValue']/option[@value='"+blockSelectCode[blockName]+"']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='ReportViewer1_ctl00_ctl09_ddValue']/option[@value='"+shopSelectCode[shopCode]+"']").click()
    time.sleep(delay)

    '''
    driver.find_element_by_link_text(u"ऊ.मु.दुकान = 392005001-आदिमजाति सेवा सहकारी समिति उदयपुर").click()
    '''

    driver.find_element_by_id("ReportViewer1_ctl00_ctl11_txtValue").clear()
    driver.find_element_by_id("ReportViewer1_ctl00_ctl11_txtValue").send_keys("12/1/2014")
    #driver.find_element_by_id("ReportViewer1_ctl00_ctl11_txtValue").send_keys("20141201")  # YYYYMMDD
    #driver.find_element_by_xpath("//select[@id='ReportViewer1_ctl00_ctl11_txtValue']/option[@value='"+start_date+"']").click()
    #driver.find_element_by_id("ReportViewer1_ctl00_ctl11_ddDropDownButton").click()
    time.sleep(delay)

    driver.find_element_by_id("ReportViewer1_ctl00_ctl13_txtValue").clear
    driver.find_element_by_id("ReportViewer1_ctl00_ctl13_txtValue").send_keys("12/31/2015")
    #driver.find_element_by_xpath("//select[@id='ReportViewer1_ctl00_ctl13_txtValue']/option[@value='"+end_date+"']").click()
    time.sleep(delay)

    driver.find_element_by_id("ReportViewer1").click()
    elem=driver.find_element_by_name("ReportViewer1$ctl00$ctl00")
    elem.click()
    time.sleep(delay)
    html_source = driver.page_source
    raw_html=html_source.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    with open(filename, "wb") as html_file:
      logger.info("Writing [%s]" % filename)
      html_file.write(raw_html.encode("UTF-8"))

    logger.info("Done")
    exit(0)

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

    logger.debug("month[%s]vs[%s]", month, list(month2number.keys())[list(month2number.values()).index(12)])
    logger.info("month[%s]", month)
    month_number = month2number[month]
    logger.info("month_number[%d]", month_number)
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
      query = 'insert into pdsEnrollment (rationcardNo, shopCode, dateDisbursed, noOfFamilyMembers, allotment) values ("%s", "%s", "%s", "%s", "%s")' % (rationcard_no, shopCode, date_of_issue, no_of_familymembers, allotment) + ' ON DUPLICATE KEY UPDATE rationcardNo="%s", shopCode="%s", dateDisbursed="%s", noOfFamilyMembers="%s", allotment="%s"' % (rationcard_no, shopCode, date_of_issue, no_of_familymembers, allotment)
      logger.info('Executing query[%s]' % query)
      try:
        cur.execute(query)
      except IntegrityError as e:
        logger.warning('Attempting Duplicate Entry[%s]', e)
            
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

  download_dir = args['directory']
  if download_dir:
    download_dir = download_dir + '/' + strftime('%B-%Y')
    logger.info('download_dir[%s]' % download_dir)
    if not os.path.exists(download_dir):
      os.makedirs(download_dir)

  if args['prev']:
    pdsFetchPrev(logger, driver, db, download_dir, args['month'], args['year'])
  elif args['parse']:
    pdsReportParse(logger, db, download_dir)
  elif args['work_allocation']:
    downloadWorkAllocationHTML(driver, db, logger) # Mynk Fix Order
  elif args['fetch']:
    pdsFetchReports(logger, driver, db, download_dir)
  else:
    pdsFetch(logger, driver, db, download_dir)

  if not args['parse']:
    driverFinalize(driver)
    displayFinalize(display)

  dbFinalize(db)

  logger.info("...END PROCESSING")
  exit(0)

if __name__ == '__main__':
  main()
