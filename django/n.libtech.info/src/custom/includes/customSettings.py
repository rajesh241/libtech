from datetime import datetime, timedelta
musterTimeThreshold = datetime.now() - timedelta(hours=240)
wagelistTimeThreshold = datetime.now() - timedelta(minutes=1)
panchayatCrawlThreshold = datetime.now() - timedelta(days=7)
panchayatRetryThreshold = datetime.now() - timedelta(hours=5)
panchayatAttemptRetryThreshold = datetime.now() - timedelta(hours=5)
crawlRetryThreshold = datetime.now() - timedelta(seconds=5)
#jobCardRegisterTimeThreshold = datetime.now() - timedelta(days=15)
jobCardRegisterTimeThreshold = datetime.now() - timedelta(days=4)
telanganaJobcardTimeThreshold = datetime.now() - timedelta(days=5)
crawlerTimeThreshold = datetime.now() - timedelta(days=3)
crawlProcessTimeThreshold=3 #this is about an hour
statsURL="http://mnregaweb4.nic.in/netnrega/all_lvl_details_new.aspx"
wagelistGenerationThresholdDays = 30
repoDir="/home/libtech/repo/src/"
djangoDir="/home/libtech/repo/django/n.libtech.info/src/"
logDir="/home/libtech/logs/"
djangoSettings="libtech.settings"
searchIP='164.100.129.6'
startFinYear='16'
telanganaThresholdDate="2015-04-01"
#postalWebsite="http://bdp.tsonline.gov.in/NeFMS_TS/NeFMS/Reports/NeFMS/PaymentPendingAccountsMandal.aspx"
postalWebsite="https://bdp.tsonline.gov.in/NeFMS_TS/NeFMS/Reports/NeFMS/PaymentPendingAccountsMandal.aspx"
telanganaStateCode='36'
apStateCode='02'
nregaPortalMinHour=6
nregaPortalMaxHour=21
