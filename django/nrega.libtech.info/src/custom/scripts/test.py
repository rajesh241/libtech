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
from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,Wagelist,Applicant,LibtechTag,Jobcard,PanchayatCrawlQueue,PendingPostalPayment,FTO
# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
from django.core.files import File
from django.core.files.base import ContentFile
application = get_wsgi_application()
#my_obj.categories.add(fragmentCategory.objects.get(id=1))
from django.contrib.auth.models import User
from django.db.models import Count,Sum

#myobjs=User.objects.filter(username='demo')
#for obj in myobjs:
#  print(obj.id)

#myobjs=Wagelist.objects.filter(block__code="1603004")
myobjs=FTO.objects.filter(block__code="1603004")
#myobjs=Muster.objects.filter(panchayat__code="1603004002")
for obj in myobjs:
  obj.isDownloaded=False
  obj.isProcessed=False
  obj.save()

exit(0)

myobjs=PanchayatCrawlQueue.objects.filter(isComplete=True)
for obj in myobjs:
  print(obj.status)
  obj.status='7'
  obj.save()
exit(0)

myobjs=PendingPostalPayment.objects.all()
for obj in myobjs:
  print(obj.id)
  obj.delete()
exit(0) 
myobjs=PanchayatCrawlQueue.objects.filter(panchayat__block__code='3614057')
for obj in myobjs:
  obj.priority=300
  obj.status=0
  obj.save()
exit(0)
myWorkDetails=WorkDetail.objects.filter(worker__jobcard__panchayat__block__id=2639,musterStatus='Rejected').values("worker__jobcard__panchayat__block__id","muster__finyear").annotate(dcount=Count('pk'),tcount=Sum('totalWage'))
for obj in myWorkDetails:
  s="finyear %s count %s sum %s " % (obj["muster__finyear"],str(obj["dcount"]),str(obj["tcount"]))
  print(s)
exit(0)
surveyTag=LibtechTag.objects.filter(name="baseLineSurvey").first()
alwaysTag=LibtechTag.objects.filter(name="always")
replacementTag=LibtechTag.objects.filter(name="baseLineSurveyReplacement").first()
blockCodes=['3614005','3614006','3614007','3614004','3614008']

pid=68012
jcEnd='64'

myWorkDetails=WorkDetail.objects.filter(worker__jobcard__panchayat__id=pid,worker__jobcard__jobcard__endswith=jcEnd).values("worker__jobcard__jobcard","worker__jobcard__headOfHousehold").annotate(dcount=Count('pk'))
for eachWorkDetail in myWorkDetails:
  print(eachWorkDetail["worker__jobcard__jobcard"])
  print(eachWorkDetail["worker__jobcard__headOfHousehold"])
  print(eachWorkDetail["dcount"])

baselineSurvey='''
blockCodes=['3614007','3614008']
for eachblockcode in blockCodes:
  myBlock=Block.objects.filter(code=eachblockcode).first()
  myJobcards=Jobcard.objects.filter(panchayat__block=myBlock,isBaselineSurvey=True)
  for eachJobcard in myJobcards:
    eachJobcard.isBaselineSurvey=False
    print(eachJobcard.tjobcard)
    eachJobcard.save()
  myJobcards=Jobcard.objects.filter(panchayat__block=myBlock,isBaselineReplacement=True)
  for eachJobcard in myJobcards:
    eachJobcard.isBaselineReplacement=False
    print(eachJobcard.tjobcard)
    eachJobcard.save()
'''

a='''
myobjs=Jobcard.objects.filter(libtechTag__in=myLibtechTag)
i=0
for obj in myobjs:
  i=i+1
  print(i)
  print(obj.code)
  obj.libtechTag.add(alwaysTag)
  obj.save() 
'''
telanganaStateCode='36'
#myobjs=Panchayat.objects.filter(isDataAccurate=True).values("block__district__code","block__district__name","block__district__state__name").annotate(dcount=Count('pk'))
#myobjs=Muster.objects.filter(panchayat__code="3405008014")
#for obj in myobjs:
#  obj.isProcessed=False
#  obj.save()

groupby='''
myobjs=Applicant.objects.filter(panchayat__block__district__state__code="36").values("panchayat__block__code","panchayat__block__name","panchayat__name","panchayat__code").annotate(dcount=Count('pk'))
for obj in myobjs:
  blockName=obj['panchayat__block__name']
  panchayatName=obj['panchayat__name']
  panchayatCode=obj['panchayat__code']
  count=obj['dcount']
  scApplicants=Applicant.objects.filter(panchayat__code=panchayatCode,caste__contains='SC')
  scCount=len(scApplicants)
  print("%s,%s,%s,%s" % (blockName,panchayatName,count,str(scCount)))
'''
testArray='''
myWorkDetails=WorkDetail.objects.filter(id=823211)[:2]
for eachWorkDetail in myWorkDetails:
  wagelistArray=eachWorkDetail.wagelist.all()
  print(wagelistArray[len(wagelistArray) -1 ])
'''
many_to_many='''
wagelistNo="3408009WL000166"
myWagelist=Wagelist.objects.filter(wagelistNo=wagelistNo)
wagelistArray=[]
for eachWagelist in myWagelist:
  print(eachWagelist.id)
  wagelistArray.append(eachWagelist.id)
myWDRecords=WorkDetail.objects.filter(wagelist__in=wagelistArray)
for eachWDRecord in myWDRecords:
  print(eachWDRecord.id)
#if myDistrict is not None:
#  print(myDistrict.code)
'''
fileopen='''
with open('/tmp/survey.csv') as fp:
    for line in fp:
      line=line.lstrip().rstrip()
      if line != '':
        print(line)
        lineArray=line.split(",")
        jobcard=lineArray[0]
        remarks=lineArray[1]
        print(jobcard)
        obj=Jobcard.objects.filter(jobcard=jobcard).first()
        #obj.libtechTag.add(surveyTag)
        if "Replacement" in remarks:
          print("This is Replacement")
          obj.isBaselineReplacement=True
        else:
          obj.isBaselineSurvey=True
        obj.save()
'''

groupby= '''
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
'''



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
