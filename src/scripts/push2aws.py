import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

import unittest

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize, driverFinalize, displayInitialize, displayFinalize

###

includePath='/home/libtech/repo/django/n.libtech.info/src/custom/includes'
sys.path.append(includePath) # os.path.join(os.path.dirname(__file__), '..', 'includes') #FIXME

from customSettings import repoDir, djangoDir, djangoSettings

sys.path.append(djangoDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)

import django

# This is so Django knows where to find stuff.
# This is so my local_settings.py gets loaded.
django.setup()

from nrega.models import State,District,Block,Panchayat,PaymentInfo,LibtechTag,CrawlQueue,Worker

###

from secure.libtech_settings import LIBTECH_AWS_ACCESS_KEY_ID,LIBTECH_AWS_SECRET_ACCESS_KEY
from libtech.settings import AWS_STORAGE_BUCKET_NAME,AWS_S3_REGION_NAME,MEDIA_URL,S3_URL
    
import boto3
from boto3.session import Session
from botocore.client import Config


#######################
# Global Declarations
#######################

csvfile = 'trial_data.csv'
jsonfile = 'trial_data.json'


#############
# Functions
#############

def push2aws(logger, filename=None):
    if not filename:
        filename = jsonfile
    logger.info('pushing filename[%s]' % filename)

    try:
        with open(filename, 'r') as html_file:
            logger.info('Reading [%s]' % filename)
            html_source = html_file.read()
    except Exception as e:
        logger.error('Exception when opening file for jobcard[%s] - EXCEPT[%s:%s]' % (jobcard_no, type(e), e))
        raise e
        
    with open(filename, 'rb') as filehandle:
        content = filehandle.read()
    cloud_filename='media/temp/rn6/%s' % filename
    session = Session(aws_access_key_id=LIBTECH_AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=LIBTECH_AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3',config=Config(signature_version='s3v4'))
    s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(ACL='public-read',Key=cloud_filename, Body=content)
    public_url='https://s3.ap-south-1.amazonaws.com/libtech-nrega1/%s' % cloud_filename
    logger.info('File written on AWS[%s]' % public_url)

    return 'SUCCESS'

class TestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = loggerFetch('info')
        self.logger.info('BEGIN PROCESSING...')

    def tearDown(self):
        self.logger.info('...END PROCESSING')

    def test_csv2aws(self):
        result = push2aws(self.logger, filename=csvfile)
        self.assertEqual(result, 'SUCCESS')

    def test_json2aws(self):
        result = push2aws(self.logger, filename=jsonfile)
        self.assertEqual(result, 'SUCCESS')
        
if __name__ == '__main__':
    unittest.main()
