import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

import sys
sys.path.insert(0, '../')
from wrappers.logger import loggerFetch


#######################
# Global Declarations
#######################

timeout = 10
browser = "Firefox"
visible = 0
logfile = "/tmp/%s_firefox_console.log"%os.environ.get('USER')
size = (width, height) = (1024,768)

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
  parser.add_argument('-c', '--cookie-dump', help='Cookie Dump', required=False, action='store_const', const=True)

  args = vars(parser.parse_args())
  return args

def displayInitialize(isVisible=None):
  if not isVisible:
    isVisible = visible
  from pyvirtualdisplay import Display
  
  display = Display(visible=isVisible, size=size) # size=(600, 400))
  display.start()
  return display

def displayFinalize(display):
  display.stop()

def vDisplayInitialize(isVisible=0):
  from xvfbwrapper import Xvfb
  vdisplay = Xvfb()
  vdisplay.start()

  return vdisplay

def vDisplayFinalize(vdisplay):
  vdisplay.stop()

# This is not working  :( Mynk - Source: http://stackoverflow.com/questions/18182653/xvfb-browser-window-does-not-fit-display
def xDisplayInitialize(isVisible=0):
  import Xlib
  import Xlib.display

  ### Create virtual display and open the browser here ###

  dpy = Xlib.display.Display()
  root = dpy.screen().root
  geometry = root.get_geometry()
  for win in root.query_tree().children:
        win.configure(x = 0, y = 0,
                              width = geometry.width, height = geometry.height)
  dpy.sync()

  return dpy

def xDisplayFinalize(display):
  display.stop()

def driverInitialize(browser=None):
  if browser ==  None:
    browser="Firefox"
  if browser == "Firefox":
    fp = webdriver.FirefoxProfile()
    fp.set_preference("webdriver.log.file", logfile)
    fp.native_events_enabled = False
    fp.set_preference("browser.download.folderList",2)
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    fp.set_preference("browser.download.dir", os.getcwd())
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")
    fp.set_preference("browser.privatebrowsing.autostart", True)

# Mynk Doesn't work - http://stackoverflow.com/questions/15397483/how-do-i-set-browser-width-and-height-in-selenium-webdriver
#    fp.set_preference('browser.window.width', width)
#    fp.set_preference('browser.window.height', height)

    driver = webdriver.Firefox(fp)
    driver.set_window_size(width, height)
  elif browser == "PhantomJS":
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
  else:
    driver = webdriver.Chrome()

  driver.implicitly_wait(timeout)

  return driver

def driverFinalize(driver):
  driver.close()
  driver.quit()

def waitUntilID(logger, driver, id, timeout):
  '''
  A function that waits until the ID is available else times out.
  Return: The element if found by ID
  '''
  try:
    logger.info("Waiting for the page to load...")
    elem = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.ID, id))
    )
    logger.info("...done looking")
    return elem

  except (NoSuchElementException, TimeoutException):
    logger.error("Failed to fetch the page")
    return None
  

def wdTest(driver, url=None):
  if not url:
    url = "http://www.google.com"
  driver.get(url)
  return driver.page_source

import pickle
def cookieDump(driver, filename=None):
    # login code
    cookies = driver.get_cookies()
    print("[[[%s]]]" % cookies)
    pickle.dump(cookies, open("QuoraCookies.pkl","wb"))

def cookieLoad(driver, filename=None):
    for cookie in pickle.load(open("QuoraCookies.pkl", "rb")):
        driver.add_cookie(cookie)

def runTestSuite():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")

  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])

  if args['cookie_dump']:
    cookieDump(driver)

  logger.info("Fetching [%s]" % driver.current_url)
  logger.info(wdTest(driver, args['url']))
  logger.info("Fetched [%s]" % driver.current_url)

  if args['cookie_dump']:
    cookieDump(driver)

  driverFinalize(driver)
  displayFinalize(display)

  '''
  display = vDisplayInitialize(visible)
  driver = driverInitialize(browser)

  logger.info(wdTest(driver))

  driverFinalize(driver)
  vDisplayFinalize(display)
  '''	

  logger.info("...END PROCESSING")     


def main():
  runTestSuite()
  exit(0)

if __name__ == '__main__':
  main()
