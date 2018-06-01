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

repoDir="/home/libtech/repo/src/"
djangoDir="/home/libtech/repo/django/nrega.libtech.info/src/"
djangoSettings="libtech.settings"
searchIP='164.100.129.6'
startFinYear='16'
telanganaThresholdDate="2015-04-01"
#postalWebsite="http://bdp.tsonline.gov.in/NeFMS_TS/NeFMS/Reports/NeFMS/PaymentPendingAccountsMandal.aspx"
postalWebsite="https://bdp.tsonline.gov.in/NeFMS_TS/NeFMS/Reports/NeFMS/PaymentPendingAccountsMandal.aspx"
telanganaStateCode='36'
apStateCode='02'
