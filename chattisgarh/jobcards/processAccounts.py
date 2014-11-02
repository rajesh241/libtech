#This code will get the Oabcgatat Banes
import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
#regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
regex=re.compile(r'<input type="hidden" value="[A-Za-z0-9]+.*?"\s*/>+',re.DOTALL)
#Connect to MySQL Database
db = MySQLdb.connect(host="localhost", user="root", passwd="golani123", db="surguja",charset='utf8')
cur=db.cursor()
db.autocommit(True)
#Query to set up Database to read Hindi Characters
query="SET NAMES utf8"
cur.execute(query)
#Getting all the blocks
query="select name,blockCode from blocks limit 1"
cur.execute(query)
results = cur.fetchall()
for row in results:
  blockName=row[0]
  blockCode=row[1]
  print blockName+blockCode
