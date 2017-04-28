from bs4 import BeautifulSoup
from datetime import datetime,date,timedelta
import requests
import os
import sys
import re
import time
from customSettings import repoDir,djangoDir,djangoSettings
from customSettings import musterTimeThreshold
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import Q


os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster



with open('/tmp/statsBlocks.csv') as fp:
  for line in fp:
    line=line.lstrip().rstrip()
    if len(line) == 6:
      line="0"+line
    myBlock=Block.objects.filter(fullBlockCode=line).first()
    myBlock.crawlRequirement='STAT'
    myBlock.save()
