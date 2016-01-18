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
visible = 1
logfile = "/tmp/%s_firefox_console.log"%os.environ.get('USER')
size = (width, height) = (1024,768)

#############
# Functions
#############


def displayInitialize(isVisible=0):
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

def waitUntilID(driver, id, timeout):
  '''
  A function that waits until the ID is available else times out.
  Return: True if found else False
  '''
  try:
    # logger.info("Waiting for the page to load...")
    elem = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.ID, id))
    )
    # logger.info("...done looking")

  except (NoSuchElementException, TimeoutException):
    # logger.error("Failed to fetch the page")
    return False

  finally:
    return True
  

def wdTest(driver):
  driver.get("http://www.google.com")
  #return driver.page_source.encode('utf-8')
  return driver.title

def runTestSuite():
  logger = loggerFetch("info")
  logger.info("BEGIN PROCESSING...")

  display = displayInitialize(visible)
  driver = driverInitialize(browser)

  logger.info(wdTest(driver))

  driverFinalize(driver)
  displayFinalize(display)

  display = vDisplayInitialize(visible)
  driver = driverInitialize(browser)

  logger.info(wdTest(driver))

  driverFinalize(driver)
  vDisplayFinalize(display)


  logger.info("...END PROCESSING")     


def main():
  runTestSuite()
  exit(0)

if __name__ == '__main__':
  main()
