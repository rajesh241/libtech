
import re
from bs4 import BeautifulSoup
import os

def writeFile3(filename,filedata):
  if not os.path.exists(os.path.dirname(filename)):
    os.makedirs(os.path.dirname(filename))
  with open(filename, 'wb') as html_file:
    html_file.write(filedata)
def writeFile(filename,filedata):
  if not os.path.exists(os.path.dirname(filename)):
    os.makedirs(os.path.dirname(filename))
  myfile = open(filename, "wb")
  myfile.write(filedata.encode("UTF-8"))
  myfile.close()
def cleanFPSName(inname):
  fpsName1 = inname.replace("'","")
  fpsName2 = fpsName1.replace("/", "")
  fpsName3 = fpsName2.replace(".", "")
  fpsName=fpsName3.replace(" ", "_")
  return fpsName
