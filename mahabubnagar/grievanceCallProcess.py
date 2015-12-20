#! /usr/bin/env python

from bs4 import BeautifulSoup

import time
import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize
from wrappers.db import dbInitialize,dbFinalize
from mahabubnagar.musters import fetchJobcard

#######################
# Global Declarations
#######################

delay = 2
timeout = 10


#############
# Functions
#############

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Jobcard script for crawling, downloading & parsing')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--timeout', help='Time to wait before a page loads', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-u', '--url', help='Specify the url to crawl', required=False)
  parser.add_argument('-d', '--directory', help='Specify directory to download html file to', required=False)
  parser.add_argument('-q', '--query', help='Query to specify the workset, E.g ... where id=147', required=False)

  args = vars(parser.parse_args())
  return args


def preText():
  '''
  Prefixing to the html file script
  '''
  text = '''<!DOCTYPE html>
<head>
<title>:: Job Card Holders Information ::</title>
<meta charset="UTF-8">
</head>

<body style="position: relative; min-height: 100%; top: 5px;">

<form action="./submit.php" method="POST">

'''
  return text


def grievanceDetails():
  '''
  Adding the Jobcard for Verification
  '''
  details ='''
<table cellpadding="0" cellspacing="0" align="center" border="1" width="70%">
  <tbody>
    <tr>
      <th colspan="2">Grievance Details</th>
    </tr>
    <tr>
      <td>Jobcard Number: </td>
      <td><input name="jobcardNumber" type="text" value="jobcard_number"></td>
    </tr>

    <tr>
      <td>Mobile Number: </td>
      <td><input name="mobileNumber" type="text" value="mobile_number"></td>
    </tr>

    <tr>
      <td colspan="2"><input name="missedCallID" type="hidden" value="missed_call_id"></td>
    </tr>

    <tr>
      <td>Complaint Number</td>
      <td><input name="complaintNumber" type="text" value="complaint_number"></td>
    </tr>
    <tr>
      <td>Complaint Date</td>
      <td><input name="complaintDate" type="date" value="complaint_date"></td>
    </tr>
    
    <tr>
      <td>Current Step:</td>
      <td><select name="currentStep" value="current_step">
<option value="Call Pending">Trying to Call</option>
<option value="Updated Jobcard Infortion">Updaing JobCard</option>
<option value="Unable to reach callback requested">Request for Call Back</option>
<option value="Form Filled with Basic Details">Form Filled with Basic Details</option>
<option value="Form Finalized">Form Finalized</option>
<option value="Complaint Filed">Filed the Complaint</option>
<option value="Complaint Resolved on Website">Resolved on Website</option>
<option value="Resolved Verified on Field">Verified On Field</option>
</select></td>
    </tr>

    <tr>
      <td>Final Status:</td>
      <td><select name="finalStatus" value="final_status">
<option value="Open">Open</option>
<option value="Closed">Closed</option>
</select></td>
    </tr>

    <tr>
      <td>Reason for Complaint Closure:</td>
      <td><select name="closureReason" value="closure_reason">
<option value="Phone not Reachable">Phone not reachable for a long time</option>
<option value="Duplicate">Duplicate</option>
<option value="Not Nrega Worker">Not An Nrega Worker</option>
<option value="Complaint Resolved Successfully">Verfied that Complaint Successfully Resolved</option>
<option value="Closed and Not Verified on Field">Closed and Not Verified on Field</option>
</select></td>
    </tr>

    <tr>
      <th colspan="2">Problem Details</th>
    </tr>

    <tr>
      <td>Service Type</td>
      <td><select name="serviceType">
<option value="1" selected>NREGS</option>
</select></td>
    </tr>

    <tr>
      <td>Service Category:</td>
      <td><select name="serviceCategory">
<option value="1" selected>Delay in payments(Wages)</option>
</select></td>
    </tr>

    <tr>
      <td>Problem Type:</td>
      <td><select name="problemType" value="problem_type">
<option value="">--Select One--</option>
<option value="Postoffice">Postoffice</option>
<option value="Smartcard payments">Smartcard payments</option>
<option value="how many weeks it is pending">how many weeks it is pending</option>
<option value="Period in weeks">Period in weeks</option>
<option value="Number of weeks payment pending(ask days)">Number of weeks payment pending(ask days)</option>
<option value="Since when">Since when</option>
<option value="Post Office Biometric(Finger Prints Not Match)">Post Office Biometric(Finger Prints Not Match)</option>
<option value="Village Organizations(VO)">Village Organizations(VO)</option>
</select></td>
    </tr>

    <tr>
      <td>Period in weeks:</td>
      <td><input name="periodInWeeks" type="number" value="period_in_weeks"></td>
    </tr>

    <tr>
      <td>Beneficiary Remarks:</td>
      <td><textarea name="beneficiaryRemarks" cols="60" rows="10">beneficiary_remarks</textarea></td>
    </tr>

    <tr>
      <td>RD Call Center Status:</td>
      <td><select name="rdCallCenterStatus" value="rd_status">
<option value="">--Select One--</option>
<option value="MPDOPENDING">MPDOPENDING</option>
<option value="Since when">Since when</option>
<option value="Post Office Biometric(Finger Prints Not Match)">Post Office Biometric(Finger Prints Not Match)</option>
<option value="Village Organizations(VO)">Village Organizations(VO)</option>
</select></td>
    </tr>

    <tr>
      <td>Redressal Remarks:</td>
      <td><textarea name="redressalRemarks" cols="60" rows="10">redressal_remarks</textarea></td>
    </tr>    

  </tbody>
</table>
'''
  
  return details



def postText():
  '''
  Suffixing to the html file script
  '''
  text = '''

<table cellpadding="0" cellspacing="0" align="center" border="1" width="70%">
  <tbody>
    <tr>
      <td colspan="2" align="center">                    
        <button type="submit">Submit</button>
      </td>
    </tr>

  </tbody>
</table>


</form>

</body>
</html>
'''
  return text

def htmlUnescape(s):
  """
  Returns the ASCII decoded version of the given HTML string. This does
  NOT remove normal HTML tags like <p>.
  """
  htmlCodes = (
      ("'", '&#39;'),
      ('"', '&quot;'),
      ('>', '&gt;'),
      ('<', '&lt;'),
      ('&', '&amp;')
    )
  for code in htmlCodes:
    s = s.replace(code[1], code[0])
  return s

def checkboxSet(html, name, checked_list):
  '''
  Sets the option as checked for the chosen checkbox
  '''
  for str in checked_list.split(','):
    old_str = '<input type="checkbox" name="' + name + '" value=' + str + '">'
    new_str = old_str.replace('">', '" checked>')
    print("Old[%s] > New[%s]" %(old_str, new_str))
    return html.replace(old_str, new_str)

  return html

def dropdownOptionSet(html, str):
  '''
  Sets the option as selected for the chosen dropdown
  '''
  if str != "":
    old_str = '<option value="' + str + '">'
    new_str = old_str.replace('">', '" selected>')
    print("Old[%s] > New[%s]" %(old_str, new_str))    
    return html.replace(old_str, new_str)
  else:
    return html

def htmlUpdate(html, log_details):
  '''
  Returns the ASCII decoded version of the given HTML string. This does
  NOT remove normal HTML tags like <p>.
  '''
  if False:
    query = 'select missedCallID, phone, ts, jobcard, htmlgen, currentStep from ghattuMissedCallsLog where'
    cur = db.cursor()
    logger.info("query[%s]" % query)
    cur.execute(query)
    call_details = cur.fetchall()

  missed_call_id = log_details[1]
  mobile_number = log_details[2]
  jobcard_number = log_details[4]
  worker_id_list = log_details[5]
  epay_order_list = log_details[6]
  name = log_details[7]
  complaint_number = log_details[8]
  complaint_date = log_details[9]
  problem_type = log_details[10]
  period_in_weeks = log_details[11]
  beneficiary_remarks = log_details[12]
  redressal_remarks = log_details[16]
  rd_status = log_details[17]
  current_step = log_details[13]
  final_status = log_details[14]
  closure_reason = log_details[15]
  

  html = html.replace('jobcard_number', jobcard_number)
  html = html.replace('mobile_number', mobile_number)
  html = html.replace('missed_call_id', str(missed_call_id))
  html = html.replace('complaint_number', str(complaint_number))
  html = html.replace('complaint_date', str(complaint_date))

  #html = checkboxSet(html, "workerID[]", worker_id_list)
  #html = checkboxSet(html, "ePayOrderList[]", epay_order_list)

  html = dropdownOptionSet(html, current_step)
  html = dropdownOptionSet(html, final_status)
  html = dropdownOptionSet(html, closure_reason)
  
  html = html.replace('beneficiary_remarks', str(beneficiary_remarks))
  html = html.replace('redressal_remarks', str(redressal_remarks))
  html = dropdownOptionSet(html, rd_status)  
  html = dropdownOptionSet(html, problem_type)  
  html = html.replace('period_in_weeks', str(period_in_weeks))
  
  return html

def oldFetchJobcard(logger, driver, log_details, dir=None, url=None):
  '''
  Fetch the html for the jobcard
  '''
  logger.info("LogDetails[%s] Directory[%s] URL[%s]" %
              (log_details, dir, url))

  if dir == None:
    dir = "/root/libtech/ghattu/nrega/html"

  if url == None:
    url = "http://www.nrega.telangana.gov.in/"

  missed_call_id = log_details[1]
  mobile_number = log_details[2]
  jobcard_number = log_details[4]

  logger.info("JocardNumber[%s] MobileNumber[%s] ID[%s] Directory[%s] URL[%s]" %
              (jobcard_number, mobile_number, missed_call_id, dir, url))

  if jobcard_number == None or jobcard_number == "" or len(jobcard_number) != 18:
    jobcard_number = "0"

  logger.info("JocardNumber[%s] MobileNumber[%s] ID[%s] Directory[%s] URL[%s]" %
              (jobcard_number, mobile_number, missed_call_id, dir, url))


  filename = dir + '/' + str(missed_call_id) + '_' + str(mobile_number) + '.html'

  fetched = 1
  
  if jobcard_number != "0":
    driver.get(url)
    logger.info("Fetching...[%s]" % url)

    elem = driver.find_element_by_name("spl")
    elem.send_keys("JobCard")
    #time.sleep(1)

    elem = driver.find_element_by_name("input2")
    elem.send_keys(jobcard_number)

    elem = driver.find_element_by_name("Go")
    elem.click()

    parent_handle = driver.current_window_handle
    logger.info("Handles [%s] Number [%d]" % (driver.window_handles, len(driver.window_handles)))

    if True: # len(driver.window_handles) == 2:
      driver.switch_to_window(driver.window_handles[-1])
      logger.info("Switching to child [%s]" % driver.window_handles[-1])
    else:
      logger.error("Handlers gone wrong [" + str(driver.window_handles) + "]")
      driver.save_screenshot('./button_'+jobcard_number+'.png')

    html_source = driver.page_source
    logger.debug("HTML Fetched [%s]" % html_source)

    driver.close()
    driver.switch_to_window(parent_handle)
    logger.debug("Switching to parent [%s]" % parent_handle)

    if False:
      with open(filename, 'w') as html_file:
        logger.info("Writing Prematurely[%s]" % filename)
        html_file.write(html_source.encode('utf-8'))

    bs = BeautifulSoup(html_source)
    span = bs.find('span',attrs={'class':'rpt-hd-txt'})
    logger.debug("Span[%s]" % span)
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
      if count > 2:
        th = str(hrow.find('th'))
        heading = th.replace('S.No.', 'Select')
        hrow.insert(len(hrow)+1, heading)
        logger.debug("HeadRow[%s]" % hrow)
        count = count-3

        row = rows[3] # hrow.findNext('tr').findNext('tr').findNext('tr')
        logger.debug("FirstRow[%s]" % row)

        worker_id_list = log_details[5].split(',')

        # Mynk logger.info("Cells[%s]"%row.findAll('td'))
        while count != 0:  # Mynk Can change to for perhaps
          count = count - 1
          td = row.find('td')
          td = td.findNext('td')
          worker_id_value = td.text
          worker_id = worker_id_value.strip()

          checkbox = '<input type="checkbox" name="workerID[]" value="'+ worker_id + '">'
          if worker_id in worker_id_list:
            checkbox = checkbox.replace('">', '" checked>')
          logger.debug("Checkbox[%s], WorkerIdValue[%s], WorkerID[%s]" % (checkbox, worker_id_value, worker_id))
          value = str(td).replace(worker_id_value, checkbox).replace('align="right"', 'align="center"')
          row.insert(len(row)+1, value)
          try:
            row = row.findNext('tr')
          except StopIteration:
            break

      main3 = bs.find(id='main3')
      table3 = main3.find('table')
      logger.debug("Table2[%s]" % table3)
      hrow = table3.find('tr')

      th = str(hrow.find('th'))
      heading = th.replace('Epayorder No:', 'Select')
      hrow.insert(len(hrow)+1, heading)
      heading = th.replace('Epayorder No:', 'Muster Signed')
      hrow.insert(len(hrow)+1, heading)

      row = hrow.findNext('tr')

      epay_order_list = log_details[6].split(',')

      while True:
        td = row.find('td')
        epay_order_value = td.text
        epay_order_number = epay_order_value.strip()

        if len(epay_order_number) != 16:
          break

        checkbox = '<input type="checkbox" name="ePayOrderList[]" value="'+ epay_order_number + '">'
        if epay_order_number in epay_order_list:
          checkbox = checkbox.replace('">', '" checked>')
        logger.debug("ePayOrder CheckBox[%s]" % checkbox)
        value = str(td).replace(epay_order_value, checkbox).replace('align="left"', 'align="center"')
        row.insert(len(row)+1, value)

        checkbox = '<input type="checkbox" name="signedPayOrderList[]" value="signed_'+ epay_order_number + '">'
        value = str(td).replace(epay_order_value, checkbox).replace('align="left"', 'align="center"')
        row.insert(len(row)+1, value)

        try:
          row = row.findNext('tr')
        except StopIteration:
          break
    else:
      fetched = 0

  else:
    fetched = 0

  if fetched == 0:  
    span = ""
    table1 = ""
    table3 = ""

  html_text = preText()
  html_text += grievanceDetails()
  html_text += '<div style="background-color: #86C0C0">' + str(span) + '</div> <br />'
  html_text += '<div>' + htmlUnescape(str(table1)) + '</div>'
  html_text += '<div>' + htmlUnescape(str(table3)) + '</div>'
  html_text += postText()

  html_text = htmlUpdate(html_text, log_details)

  with open(filename, 'w') as html_file:
    logger.info("Writing file [%s]" % filename)
    html_file.write(html_text)
    logger.debug("File content [%s]" % html_text)
    
    
def createGrievanceForms(logger, db, log_details, dir=None, url=None):
  '''
  Creates a HTML form for field workers to update about the grievance
  '''

  logger.info("LogDetails[%s] Directory[%s] URL[%s]" %
              (log_details, dir, url))

  if not dir:
    dir = "./forms"
    
  if not os.path.exists(dir):
    os.makedirs(dir)

  missed_call_id = log_details[1]
  mobile_number = log_details[2]
  jobcard_number = log_details[4]

  logger.info("JocardNumber[%s] MobileNumber[%s] ID[%s] Directory[%s] URL[%s]" %
              (jobcard_number, mobile_number, missed_call_id, dir, url))

  if jobcard_number == None or jobcard_number == "" or len(jobcard_number) != 18:
    jobcard_number = "0"

  logger.info("JocardNumber[%s] MobileNumber[%s] ID[%s] Directory[%s] URL[%s]" %
              (jobcard_number, mobile_number, missed_call_id, dir, url))

  filename = dir + '/' + str(missed_call_id) + '_' + str(mobile_number) + '.html'

  fetched = 1
  fetch_dir = "/home/libtech/ghattu.libtech/jobcards"
  
  if jobcard_number != "0":
    query='use mahabubnagar'
    logger.info("query[%s]" % query)

    cur = db.cursor()
    cur.execute(query)
    logger.info("Fetching...[%s]" % jobcard_number)
    fetchJobcard(logger, db, jobcard_number, cmd="FETCH JOBCARD", dir=fetch_dir, isPushInfo=True)

    query='select p.name from jobcardRegister j, panchayats p where j.panchayatCode=p.panchayatCode  and j.jobcard="%s"' % jobcard_number
    logger.info("query[%s]" % query)

    cur = db.cursor()
    cur.execute(query)
    panchayat = cur.fetchall()[0][0]
    logger.info("Fetching...[%s]" % panchayat)
    jobcard_file = fetch_dir + '/' + str(panchayat) + '/' + jobcard_number + '.html'

    query='use libtech'
    logger.info("query[%s]" % query)

    cur = db.cursor()
    cur.execute(query)

    
    logger.info("Reading [%s]" % jobcard_file)
    with open(jobcard_file, "r") as jobcard_fd:
      html_source = jobcard_fd.read()
      
    bs = BeautifulSoup(html_source)
    span = bs.find('span',attrs={'class':'rpt-hd-txt'})
    logger.debug("Span[%s]" % span)
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
      if count > 2:
        th = str(hrow.find('th'))
        heading = th.replace('S.No.', 'Select')
        hrow.insert(len(hrow)+1, heading)
        logger.debug("HeadRow[%s]" % hrow)
        count = count-3

        row = rows[3] # hrow.findNext('tr').findNext('tr').findNext('tr')
        logger.debug("FirstRow[%s]" % row)

        worker_id_list = log_details[5].split(',')

        # Mynk logger.info("Cells[%s]"%row.findAll('td'))
        while count != 0:  # Mynk Can change to for perhaps
          count = count - 1
          td = row.find('td')
          td = td.findNext('td')
          worker_id_value = td.text
          worker_id = worker_id_value.strip()

          checkbox = '<input type="checkbox" name="workerID[]" value="'+ worker_id + '">'
          if worker_id in worker_id_list:
            checkbox = checkbox.replace('">', '" checked>')
          logger.debug("Checkbox[%s], WorkerIdValue[%s], WorkerID[%s]" % (checkbox, worker_id_value, worker_id))
          value = str(td).replace(worker_id_value, checkbox).replace('align="right"', 'align="center"')
          row.insert(len(row)+1, value)
          try:
            row = row.findNext('tr')
          except StopIteration:
            break

      main3 = bs.find(id='main3')
      table3 = main3.find('table')
      logger.debug("Table2[%s]" % table3)
      hrow = table3.find('tr')

      th = str(hrow.find('th'))
      heading = th.replace('Epayorder No:', 'Select')
      hrow.insert(len(hrow)+1, heading)
      heading = th.replace('Epayorder No:', 'Muster Signed')
      hrow.insert(len(hrow)+1, heading)

      row = hrow.findNext('tr')

      epay_order_list = log_details[6].split(',')

      while True:
        td = row.find('td')
        epay_order_value = td.text
        epay_order_number = epay_order_value.strip()

        if len(epay_order_number) != 16:
          break

        checkbox = '<input type="checkbox" name="ePayOrderList[]" value="'+ epay_order_number + '">'
        if epay_order_number in epay_order_list:
          checkbox = checkbox.replace('">', '" checked>')
        logger.debug("ePayOrder CheckBox[%s]" % checkbox)
        value = str(td).replace(epay_order_value, checkbox).replace('align="left"', 'align="center"')
        row.insert(len(row)+1, value)

        checkbox = '<input type="checkbox" name="signedPayOrderList[]" value="signed_'+ epay_order_number + '">'
        value = str(td).replace(epay_order_value, checkbox).replace('align="left"', 'align="center"')
        row.insert(len(row)+1, value)

        try:
          row = row.findNext('tr')
        except StopIteration:
          break
    else:
      fetched = 0

  else:
    fetched = 0

  if fetched == 0:  
    span = ""
    table1 = ""
    table3 = ""

  html_text = preText()
  html_text += grievanceDetails()
  html_text += '<div style="background-color: #86C0C0">' + str(span) + '</div> <br />'
  html_text += '<div>' + htmlUnescape(str(table1)) + '</div>'
  html_text += '<div>' + htmlUnescape(str(table3)) + '</div>'
  html_text += postText()

  html_text = htmlUpdate(html_text, log_details)

  with open(filename, 'w') as html_file:
    logger.info("Writing file [%s]" % filename)
    html_file.write(html_text)
    logger.debug("File content [%s]" % html_text)

    
def processMissedCalls(logger, dir, url, query=None):
  '''
  Process any missed calls in the libtech DB
  '''
  db = dbInitialize(db="libtech")
  cur = db.cursor()

  logger.info("BEGIN PROCESSING...")
  
  if query == None:
    query = '''SELECT log.id, log.missedCallID, log.phone, log.ts, log.jobcard, log.workerID,
    log.payOrderList, log.name, log.complaintNumber, log.complaintDate, log.problemType,
    log.periodInWeeks, log.remarks, log.currentStep, log.finalStatus, log.closureReason,
    log.redressalRemarks, log.rdCallCenterStatus
    FROM ghattuMissedCallsLog AS log
    RIGHT JOIN(
       SELECT missedCallID, max(ts) AS ts FROM ghattuMissedCallsLog
          WHERE htmlgen=0 GROUP BY missedCallID
             ) AS filter
    ON (log.missedCallID = filter.missedCallID and log.ts = filter.ts)'''

  logger.info("query[%s]" % query)
           
  cur.execute(query)
  missedCalls = cur.fetchall()
  logger.debug("missedCalls[%s]" % str(missedCalls))
  for log_details in missedCalls:
    #Put error checks in place and only then update libtech DB

    logger.info("log_details[%s]" % str(log_details))

    if True:
      createGrievanceForms(logger, db, log_details, dir, url)
    elif False:
      oldFetchJobcard(logger, driver, log_details, dir, url)
    else:
      id = log_details[1]
      phone = log_details[2]
      jobcard = log_details[4]
    
      cmd = '/home/mayank/libtech/scripts/fetch -j ' + str(jobcard) + ' -m ' + str(phone) + ' -i ' + str(id) + ' -d ' + dir
      logger.info("cmd[%s]" % cmd)
      os.system(cmd)    

    id = log_details[0]
    query = 'update ghattuMissedCallsLog set htmlgen=1 where id=' + str(id)
    try:    
      cur = db.cursor()
      logger.info("query[%s]" % query)
      cur.execute(query)
    except Exception as e:
      logger.info("query[%s] with exception[%s]" % (query, e))

  dbFinalize(db)
  logger.info("...END PROCESSING")
  

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

#  display = displayInitialize(args['visible'])
#  driver = driverInitialize(args['browser'])

  processMissedCalls(logger, args['directory'], args['url'], args['query'])

#  driverFinalize(driver)
#  displayFinalize(display)

  exit(0)

if __name__ == '__main__':
  main()
