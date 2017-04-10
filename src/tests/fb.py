import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

import json
import pyrebase
import unittest

from wrappers.logger import loggerFetch

#######################
# Global Declarations
#######################
filename = 'z.json'

config = {
    'apiKey': "AIzaSyDTZ88Axv_uVn_02j3HPK8dzJFXKCwME4A",
    'authDomain': "workdetailtest.firebaseapp.com",
    'databaseURL': "https://workdetailtest.firebaseio.com",
    'storageBucket': "workdetailtest.appspot.com",
    'messagingSenderId': "251568860067",
#    'serviceAccount': "~/.serviceAccountCredentials.json",
    'serviceAccount': "/home/mayank/.serviceAccountCredentials.json",
}


#############
# Functions
#############

def json2fb(logger):
  with open(filename, 'r') as infile:
    logger.info('Reading from file[%s]' % filename)
    data = json.load(infile)
    logger.info(data)

  firebase = pyrebase.initialize_app(config)
  db = firebase.database()

  all_users = db.child("9099").get()
  for user in all_users.each():
    print(user.key()) # Morty
    print(user.val()) # {name": "Mortimer 'Morty' Smith"}
    
  return 'SUCCESS'
    

#############
# Tests
#############


class TestSuite(unittest.TestCase):
  def setUp(self):
    self.logger = loggerFetch('info')
    self.logger.info('BEGIN PROCESSING...')

  def tearDown(self):
    self.logger.info("...END PROCESSING")

  def test_json2fb(self):
    result = json2fb(self.logger)
    self.assertEqual('SUCCESS', result)

if __name__ == '__main__':
  unittest.main()

