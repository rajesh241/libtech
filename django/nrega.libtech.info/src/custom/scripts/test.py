import os
import sys
import django
from datetime import datetime,date
proj_path = "/home/libtech/repo/django/nrega.libtech.info/src/"
sys.path.append(proj_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "libtech.settings")
django.setup()
# This is so Django knows where to find stuff.
# This is so my local_settings.py gets loaded.
os.chdir(proj_path)
#from django.contrib.auth.models import User
#from django.conf.settings import AUTH_USER_MODEL 
from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail
# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
from django.core.files import File
from django.core.files.base import ContentFile
application = get_wsgi_application()
#my_obj.categories.add(fragmentCategory.objects.get(id=1))
from django.contrib.auth.models import User
from django.db.models import Count

#myobjs=User.objects.filter(username='demo')
#for obj in myobjs:
#  print(obj.id)
myUser=User.objects.filter(username='demo').first()
myobjs=Muster.objects.filter(isProcessed=1)
myobjs=WorkDetail.objects.values("muster__panchayat","muster__dateTo","zjobcard").annotate(dcount=Count('pk'))[:5]
for obj in myobjs:
  print(str(obj))
  panchayatID=obj['muster__panchayat']
  dateTo=obj["muster__dateTo"]
  jobcard=obj["zjobcard"]
  myPanchayat=Panchayat.objects.filter(id=panchayatID).first()
  blockName=myPanchayat.block.name
  panchayatName=myPanchayat.name
  print(blockName+"-"+panchayatName)
  wdRecords=WorkDetail.objects.filter(muster__panchayat=panchayatID,muster__dateTo=dateTo,zjobcard=jobcard)
  for wd in wdRecords:
    name=wd.zname
    musterStatus=wd.musterStatus
    print(blockName+"-"+panchayatName+"-"+name+"-"+musterStatus)
#myobjs=Panchayat.objects.filter(block__isRequired=1).order_by('-jobcardCrawlDate')[:1]
#myobjs=Panchayat.objects.filter(id=100).order_by('-jobcardCrawlDate')[:1]
#for obj in myobjs:
#  print(obj.fullPanchayatCode+obj.name)
#  obj.jobcardCrawlDate=date.today()
#  obj.save()
# path=open('/tmp/a.html')
# content=""
# content="<h1>गुजरात</h1>"
# obj.jobcardRegisterFile.save("test.html", ContentFile(content))
# obj.save()
#stateCode='33'
#states=State.objects.filter(stateCode=stateCode)
#mystate=states.first()
#print(mystate)
#districtCode='1123'
#districtName='abcd'
#District.objects.create(state=mystate,fullDistrictCode=districtCode,name=districtName)

#for state in states:
#  print("Found an Audio")
#  print(state.name)

#stateName="CHHATTISGARH"
#stateCode="05"
#stateShortCode="CH"
#P=state(name=stateName,stateCode=stateCode,stateShortCode=stateShortCode)
#P.save()
