from django.conf.urls import url
from nrega import apiviews
from nrega import botviews
urlpatterns = [
    url(r'^api/panchayats/$', apiviews.getPanchayats),
    url(r'^api/accuratedatapts/$', apiviews.getPanchayatsAccurateData),
    url(r'^api/states/$', apiviews.getStates),
    url(r'^api/blocks/$', apiviews.getBlocks),
    url(r'^api/jobcardnumber/$', apiviews.getJobcards),
    url(r'^api/getworkers/$', apiviews.getWorkers),
    url(r'^api/jobcardsall/$', apiviews.getJobcardsAll),    
    url(r'^api/numberofjobcards/$', apiviews.getNumberJobcards),
    url(r'^api/jobcard/$', apiviews.getInfoByJc),
    url(r'^api/workdetails/$', apiviews.getWorkDetailsByJc),
    url(r'^api/jcworkcode/$', apiviews.getTransactionByWorkCode),
    url(r'^api/workcreditstatuspt/$', apiviews.workCreditStatusPt),
    url(r'^api/peoplebymusterstatus/$', apiviews.peopleByMusterStatus),    
    url(r'^api/transactionsinblock/$', apiviews.totalTransactionsForBlock),
    url(r'^api/employmentstatus/$', apiviews.employmentStatus),        
    url(r'^api/workdetailbypt/$', apiviews.getInfoByMusterStatus),
    url(r'^api/musterstatus/$', apiviews.getInfoByMusterStatus_paymentDetail),
    url(r'^api/postaldata/$', apiviews.getPostalData),
    url(r'^api/postaldelaypt/$', apiviews.postalDelayPt),
    url(r'^api/paymentdetails/$', apiviews.getPaymentDetail),
    url(r'^api/daystopay/$', apiviews.paymentDays),
    url(r'^api/crawldatapt/$', apiviews.crawlDataForPt),
    url(r'^api/crawldatarequest/$', apiviews.crawlDataRequest),
    url(r'^api/crawlstatuspt/$', apiviews.crawlStatusPt),
    url(r'^api/bot/$', botviews.UserList.as_view()),
    url(r'^api/ptreport/$', apiviews.PanchayatReport),
    url(r'^api/paymentinfo/$', apiviews.paymentInfo),
]

