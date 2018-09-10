from django.conf.urls import url
from nrega import apiviews


urlpatterns = [
    url(r'^api/states/$', apiviews.getStates),
    url(r'^api/blocks/$', apiviews.getBlocks),
    url(r'^api/panchayats/$', apiviews.getPanchayats),
    url(r'^api/wagelists/$', apiviews.getWagelists),
    url(r'^api/jcinfo/$', apiviews.jobcardInfo),
    url(r'^api/getfto/$', apiviews.getFTO),
    url(r'^api/getpi/$', apiviews.getPaymentInfo),
    url(r'^api/crawldatarequest/$', apiviews.crawlDataRequest),
    url(r'^api/getworkers/$', apiviews.getWorkers),
]
