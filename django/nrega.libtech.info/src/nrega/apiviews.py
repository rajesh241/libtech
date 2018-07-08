# Note: I don't need serializer to get aggregate values that don't have to be iterated.

from django.shortcuts import render
from datetime import datetime, timedelta
# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum, Avg, F, Q, ExpressionWrapper, fields, Max
from django.db.models.expressions import RawSQL
from django.db import connection # To execute raw queries and get results
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from nrega.models import Panchayat, State, Block, Jobcard, Applicant, WorkDetail, Muster, PaymentDetail, PendingPostalPayment, PanchayatStat, PanchayatCrawlQueue, PanchayatReport, PaymentInfo,Worker,CrawlQueue

from nrega.serializers import PanchayatSerializer, StateSerializer, StateSerializer1, SelectBlockSerializer, JobcardSerializer2, JobcardSerializer, PtAvgSerializer, getInfoByJcSerializer, getWorkDetailsByJcSerializer, MusterSerializer, WorkSerializer, WorkCreditStatusPtSerializer, JcsByMusterStatus, EmploymentStatusSerializer, PaymentDetailSerializer, PostalPaymentSerializer, PostalPaymentPtSerializer, PaymentDetailTransactionsSerializer, PanchayatStatSerializer, BlAvgSerializer, EmploymentStatusByPtSerializer, CrawlStatusSerializer, PaymentInfoSerializer, PaymentDetailsTemp,WorkerSerializer,WorkerSerializer1

import json

@csrf_exempt
def crawlDataForPt(request):
    """
    This is the api to initiate a crawl 
    """
    ptid=request.GET.get('ptid', '')
    myPanchayat=Panchayat.objects.filter(id=ptid).first()

    inQueueCount=len(PanchayatCrawlQueue.objects.filter(panchayat=myPanchayat,isComplete=False))
    if inQueueCount == 0:
        PanchayatCrawlQueue.objects.create(panchayat=myPanchayat,priority=5000)
    else:
        pass
    output = {"Response": "Added to queue"}
    return JsonResponse(output, safe=False)    

@csrf_exempt
def PanchayatReport(request):
    ptid = request.GET.get('ptid', '')
    report = PanchayatReport.objects.filter(panchayat == ptid)
    output = {'output': report}
    JsonResponse(output, safe=False)

@csrf_exempt
def crawlDataRequest(request):
    """
    This is the api to initiate a crawl 
    """
    print("in the crawlQueue")
    code=request.GET.get('code', '')
    if len(code) == 7:
      myPanchayats=Panchayat.objects.filter(block__code=code)
    elif len(code) == 10:
      myPanchayats=Panchayat.objects.filter(code=code)
    else:
      myPanchayats=None
    for eachPanchayat in myPanchayats:
#      inQueueCount=len(PanchayatCrawlQueue.objects.filter(panchayat=eachPanchayat,isComplete=False))
      inQueueCount=0
      if inQueueCount == 0:
          PanchayatCrawlQueue.objects.create(panchayat=eachPanchayat,priority=5000)
          CrawlQueue.objects.create(panchayat=eachPanchayat)
         # CrawlQueue.objects.create(panchayat=eachPanchayat,priority=5000)
          print("I am in crawlQueue")
      else:
          pass
    output = {"Response": "Added to queue"}
    return JsonResponse(output, safe=False)    



@csrf_exempt
def crawlStatusPt(request):
    ptid=request.GET.get('ptid', '')
    if ptid == '':
        crawlStatus = PanchayatCrawlQueue.objects.filter(isComplete = True)
    else:
        myPanchayat=Panchayat.objects.filter(id=ptid).first()
        crawlStatus = PanchayatCrawlQueue.objects.filter(panchayat = myPanchayat)
    crawlStatus = crawlStatus[:50]
    serializer = CrawlStatusSerializer(crawlStatus, many=True)
    return JsonResponse(serializer.data, safe=False)    

@csrf_exempt
def getPanchayatsAccurateData(request):
    """
    Get a list of Panchayats based on the furnished parameters.  If names of state, district or block are given, they are used as filters.  Accepts any part of the name of any parameter.  
    """
    if request.method == 'GET':
        panchayat=request.GET.get('panchayat', '')
        ptid=request.GET.get('ptid', '')
        block = request.GET.get('block', '')
        bid = request.GET.get('bid', '')
        district = request.GET.get('district', '')
        state = request.GET.get('state', '')
        limit=request.GET.get('limit', '')
        if limit == '':
          limit=500
        else:
          limit=int(limit)
        #PTID we need to make it exact. Finyaer make it current finyear
        panchayats = PanchayatStat.objects.filter(panchayat__name__icontains = panchayat, panchayat__id__icontains = ptid, panchayat__block__id__icontains = bid, panchayat__block__name__icontains=block, panchayat__block__district__name__icontains = district, panchayat__block__district__state__name__icontains = state, workDaysAccuracyIndex__gte = 90, finyear = '17')


        panchayats = panchayats[:limit]
        serializer = PanchayatStatSerializer(panchayats, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def getPanchayats(request):
    """
    Get a list of Panchayats based on the furnished parameters.  If names of state, district or block are given, they are used as filters.  Accepts any part of the name of any parameter.  
    """
    if request.method == 'GET':
        inName=request.GET.get('panchayat', '')
        ptid=request.GET.get('ptid', '')
        blockName=request.GET.get('block', '')
        bid = request.GET.get('bid', '')
        districtName = request.GET.get('district', '')
        stateName = request.GET.get('state', '')
        limit=request.GET.get('limit', '')
        if limit == '':
          limit=50
        else:
          limit=int(limit)
        if ptid == '':
            if bid != '':
              panchayats=Panchayat.objects.filter(name__icontains=inName, block__id=bid)
            else:
              panchayats=Panchayat.objects.filter(name__icontains=inName, block__name__icontains=blockName, block__id__icontains=bid, block__district__name__icontains = districtName, block__district__state__name__icontains = stateName)
        else:
            panchayats=Panchayat.objects.filter(id = ptid)
            

    #    if inCode != '':
    #      panchayats=
        panchayats = panchayats[:limit]
        serializer = PanchayatSerializer(panchayats, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def getStates(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        state = request.GET.get('state', '')
        curfinyear='18'
        totalTransactions=PanchayatStat.objects.filter(panchayat__block__district__state__name=state,finyear=curfinyear,workDaysAccuracyIndex__gte = 90).values ('panchayat__block__district__state__name', 'panchayat__block__name').annotate(state = F('panchayat__block__district__state__name'), block = F('panchayat__block__name'), transactions = Count('id'))
        serializer = StateSerializer1(totalTransactions, many=True)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def getBlocks(request):
    """
    List of blocks based on district and/or state names given.
    """
    if request.method == 'GET':
        blockName = request.GET.get('block', '')
        bid = request.GET.get('bid', '')
        districtName=request.GET.get('district', '')
        stateName=request.GET.get('state', '')
        limit=request.GET.get('limit', '')
        if limit == '':
          limit=50
        else:
          limit=int(limit)
        if bid=='':
          blocks = Block.objects.filter(name__icontains=blockName, district__name__icontains = districtName, district__state__name__icontains=stateName)
        else:
          blocks = Block.objects.filter(id = bid)

        blocks = blocks[:limit]
        serializer = SelectBlockSerializer(blocks, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def getWorkers(request):
    if request.method == 'GET':
      pcode=request.GET.get('pcode', '')
      limit=request.GET.get('limit', '')
    if limit == '':
      limit=1000
    else:
      limit=int(limit)
    if pcode == '':
      workers=Worker.objects.all()[:limit]
    else:
      workers=Worker.objects.filter(jobcard__panchayat__code=pcode)[:limit]
    serializer = WorkerSerializer1(workers, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def getJobcards(request):
    """
    This function gets the active jobcards in the Panchayat by getting jobcards from the workdetail table.  I could have taken them from the jobcard register, but it leads to a lot of inactive jobcards with no data, which could be frustrating on the ground.  If the feedback is that it is frustrating to not find other jobcards, I may have to revert to the jobcard register. 

    From api.ai, I might get two numbers for the jobcard intent. One will correspond to the last numbers of a jobcard and the other is likely to be a village code.  There are challenges in putting them together.  Right now, I am going to give one query for ends with and the village code to just say that is contained.  Given that I am searching within a Panchayat, this is likely to be quite accurate.
    """
    if request.method == 'GET':
        jcEnd=request.GET.get('jobend', '')
        jcContains=request.GET.get('vcode', '')
        ptid=request.GET.get('ptid', '')
        limit=request.GET.get('limit', '')
        if limit == '':
          limit=50
        else:
          limit=int(limit)
        if jcContains == '':
            jobcards = WorkDetail.objects.filter(worker__jobcard__panchayat__id = ptid, worker__jobcard__jobcard__endswith = jcEnd).values("worker__jobcard__jobcard").annotate(totalTrans = Count('pk'), jobcard = F('worker__jobcard__jobcard'), headOfHousehold = F('worker__jobcard__headOfHousehold'))
        else:
            jobcards = WorkDetail.objects.filter(worker__jobcard__panchayat__id = ptid, worker__jobcard__jobcard__endswith = jcEnd, worker__jobcard__jobcard__icontains = jcContains).values("worker__jobcard__jobcard").annotate(totalTrans = Count('pk'), jobcard = F('worker__jobcard__jobcard'), headOfHousehold = F('worker__jobcard__headOfHousehold'))

        jobcards = jobcards[:limit]
        serializer = JobcardSerializer2(jobcards, many=True)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def getJobcardsAll(request):
    """
    This function gets all the jobcards and does not look at whether the jobcard is active or not. 

    From api.ai, I might get two numbers for the jobcard intent. One will correspond to the last numbers of a jobcard and the other is likely to be a village code.  There are challenges in putting them together.  Right now, I am going to give one query for ends with and the village code to just say that is contained.  Given that I am searching within a Panchayat, this is likely to be quite accurate.
    """
    #GOLITODO add the extra field in models for the village and use it here for filtring
    if request.method == 'GET':
        jcEnd=request.GET.get('jobend', '')
        jcContains=request.GET.get('vcode', '')
        ptid=request.GET.get('ptid', '')
        limit=request.GET.get('limit', '')
        if limit == '':
          limit=50
        else:
          limit=int(limit)

        if ptid == '':
            error = {"response": "Sorry, you need to provide Panchayat id to get jobcards."}
            res = JsonResponse(error, safe=False)
        else:
            if jcContains == '':
                jobcards = Jobcard.objects.filter(panchayat__id = ptid, jobcard__endswith = jcEnd)
            else:
                jobcards = Jobcard.objects.filter(panchayat__id = ptid, jobcard__endswith = jcEnd, jobcard__icontains = jcContains)

                jobcards = jobcards[:limit]
            serializer = JobcardSerializer(jobcards, many=True)
            res = JsonResponse(serializer.data, safe=False)
    return res


# Number of jobcards in the Panchayat.
@csrf_exempt
def getNumberJobcards(request):
    """
    This returns the number of jobcard holders that are there in a Panchayat. 

    """
    if request.method == 'GET':
        ptid=request.GET.get('ptid', '')

        noJobcards=Jobcard.objects.filter(panchayat__id=ptid).count()

        return JsonResponse(noJobcards, safe=False)

@csrf_exempt
def paymentInfo(request):
    jobcard = request.GET.get('jobcard', '')
    ptid = request.GET.get('ptid', '')
    payments = PaymentInfo.objects.filter(workDetail__worker__jobcard__panchayat = ptid, status = 'Rejected')
    serializer = PaymentInfoSerializer(payments, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def totalTransactionsForBlock(request):
    '''
    I use this function to find out if we track any data for the block that the user selected.  Starting with the PaymentDetails table, it finds the total number of transactions and the number of Panchayats covered in our database.

TODO: When the accurate Panchayats index is made in the database, I should uncomment the lines below and remove the current data. 
    '''
    if request.method == 'GET':
        bid=request.GET.get('bid', '')

        accuratePts = PanchayatStat.objects.filter(panchayat__block__id = bid, workDaysAccuracyIndex__gte = 90)
        serializer = PanchayatStatSerializer(accuratePts, many=True)
        return JsonResponse(serializer.data, safe=False)       
#        totalTransactions=PaymentDetail.objects.filter(applicant__panchayat__block__id=bid).count()
#        return JsonResponse(totalTransactions, safe=False)    

# See getInfoByMusterStatus for description
def musterStatusBlLevel(musterstatus, bid):
    if musterstatus == '':
        paymentStatusByPt = WorkDetail.objects.filter(muster__panchayat__block__id = bid).values('muster__panchayat__id').annotate(ptid = F('muster__panchayat__id'), ptname = F('muster__panchayat__name'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('muster__panchayat__name')
            
    elif musterstatus == 'uncredited':
        paymentStatusByPt = WorkDetail.objects.filter(muster__panchayat__block__id = bid).exclude(musterStatus = 'credited').values('muster__panchayat__id').annotate(ptid = F('muster__panchayat__id'), ptname = F('muster__panchayat__name'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('muster__panchayat__name')
            
    elif musterstatus == 'nofto':
        paymentStatusByPt = WorkDetail.objects.filter(muster__panchayat__block__id = bid, musterStatus = '').values('muster__panchayat__id').annotate(ptid = F('muster__panchayat__id'), ptname = F('muster__panchayat__name'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('muster__panchayat__name')
            
    else:
        paymentStatusByPt = WorkDetail.objects.filter(muster__panchayat__block__id = bid, musterStatus = musterstatus).values('muster__panchayat__id').annotate(ptid = F('muster__panchayat__id'), ptname = F('muster__panchayat__name'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('muster__panchayat__name')

    return paymentStatusByPt

# See getInfoByMusterStatus for description
def musterStatusPtJcLevel(musterstatus, ptid, jobcard):
    if jobcard== '':
      if musterstatus == '':
          paymentStatusByFy = WorkDetail.objects.filter(muster__panchayat__id = ptid,  zjobcard__icontains = jobcard).values('muster__finyear').annotate(fy = F('muster__finyear'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('fy')
              
      elif musterstatus == 'uncredited':
          paymentStatusByFy = WorkDetail.objects.filter(muster__panchayat__id = ptid, zjobcard__icontains = jobcard).exclude(musterStatus = 'credited').values('muster__finyear').annotate(fy = F('muster__finyear'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('fy')
              
      elif musterstatus == 'nofto':
          paymentStatusByFy = WorkDetail.objects.filter(muster__panchayat__id = ptid, musterStatus = '', zjobcard__icontains = jobcard).values('muster__finyear').annotate(fy = F('muster__finyear'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('fy')
              
      else:
        paymentStatusByFy = WorkDetail.objects.filter(muster__panchayat__id = ptid, musterStatus = musterstatus, zjobcard__icontains = jobcard).values('muster__finyear').annotate(fy = F('muster__finyear'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('fy')


    else: 
      if musterstatus == '':
          paymentStatusByFy = WorkDetail.objects.filter(muster__panchayat__id = ptid,  worker__jobcard__jobcard = jobcard).values('muster__finyear').annotate(fy = F('muster__finyear'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('fy')
              
      elif musterstatus == 'uncredited':
          paymentStatusByFy = WorkDetail.objects.filter(muster__panchayat__id = ptid, worker__jobcard__jobcard = jobcard).exclude(musterStatus = 'credited').values('muster__finyear').annotate(fy = F('muster__finyear'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('fy')
              
      elif musterstatus == 'nofto':
          paymentStatusByFy = WorkDetail.objects.filter(muster__panchayat__id = ptid, musterStatus = '', worker__jobcard__jobcard = jobcard).values('muster__finyear').annotate(fy = F('muster__finyear'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('fy')
              
      else:
        paymentStatusByFy = WorkDetail.objects.filter(muster__panchayat__id = ptid, musterStatus = musterstatus, worker__jobcard__jobcard = jobcard).values('muster__finyear').annotate(fy = F('muster__finyear'), totalWage = Sum('totalWage'), jcs = Count('zjobcard', distinct = True)).order_by('fy')

    return paymentStatusByFy

'''
Get the total value of wages by the status of muster such as total wages, uncredited, rejected and invalid.  

If the block id is given, get information Panchayat wise at the block level.  I am not doing total values for the block level or above.  Theoretically I can get the total payments by muster status for block, district or state levels.  The problem is that we don't track data for all the Panchayats in a block or above, and so any summary stat at that level would be misleading.  That is why I stick to Panchayat or jobcard level.

If the jobcard information is given, it will fetch information at the jobcard level.  Else, at the Panchayat level. Panchayt id is required for jobcard info since it speeds up retrieval.  

'''
@csrf_exempt
def getInfoByMusterStatus(request):
    if request.method == 'GET':
        bid = request.GET.get('bid', '')
        ptid = request.GET.get('ptid', '')
        jobcard = request.GET.get('jobcard', '')
        bid = request.GET.get('bid', '')
        musterstatus = request.GET.get('musterstatus', '')
        if ptid == '':
            paymentStatusByPt = musterStatusBlLevel(musterstatus, bid)
            serializer = BlAvgSerializer(paymentStatusByPt, many=True)
        else:
            paymentStatusByFy = musterStatusPtJcLevel(musterstatus, ptid, jobcard)
            serializer = PtAvgSerializer(paymentStatusByFy, many=True)
        return JsonResponse(serializer.data, safe=False)

'''
Gets payment information at the Panchayat level or the jobcard level starting from the payment detail table.  Additional details are gathered from the workdetail and the muster tables.  If the jobcard number is given, information is retrieved for the jobcard.  Else, it's done for the Panchayat. 
'''
@csrf_exempt
def getInfoByMusterStatus_paymentDetail(request):
    if request.method == 'GET':
        ptid=request.GET.get('ptid', '')
        musterstatus = request.GET.get('musterstatus', '')
        jobcard = request.GET.get('jobcard', '')

        # If jobcard number is not given, get info for Panchayat.
        if jobcard == '':
            
            if musterstatus == '':
                paymentDetail = PaymentDetail.objects.filter(applicant__panchayat__id = ptid).values('fto__finyear').annotate(paymentDetailAmount = Sum('creditedAmount'), workDetailAmount = Sum('workDetail__totalWage'), jcs = Count('worker__jobcard__jobcard', distinct = True), fy = F('fto__finyear'))
            
            elif musterstatus == 'nofto':
                paymentDetail = PaymentDetail.objects.filter(applicant__panchayat__id = ptid, status = '').values('fto__finyear').annotate(paymentDetailAmount = Sum('creditedAmount'), workDetailAmount = Sum('workDetail__totalWage'), jcs = Count('worker__jobcard__jobcard', distinct = True), fy = F('fto__finyear'))
            
            elif musterstatus == 'uncredited':
                paymentDetail = PaymentDetail.objects.filter(applicant__panchayat__id = ptid).exclude(status = 'credited').values('fto__finyear').annotate(paymentDetailAmount = Sum('creditedAmount'), workDetailAmount = Sum('workDetail__totalWage'), jcs = Count('worker__jobcard__jobcard', distinct = True), fy = F('fto__finyear'))


            else:
                paymentDetail = PaymentDetail.objects.filter(applicant__panchayat__id = ptid, status__icontains = musterstatus).values('fto__finyear').annotate(paymentDetailAmount = Sum('creditedAmount'), workDetailAmount = Sum('workDetail__totalWage'), jcs = Count('worker__jobcard__jobcard', distinct = True), fy = F('fto__finyear'))    

        # If jobcard number is given, get info for jobcard
        else:

            if musterstatus == '':
                paymentDetail = PaymentDetail.objects.filter(worker__jobcard__jobcard = jobcard).values('fto__finyear').annotate(paymentDetailAmount = Sum('creditedAmount'), workDetailAmount = Sum('workDetail__totalWage'), jcs = Count('worker__jobcard__jobcard', distinct = True), fy = F('fto__finyear'))
            
            elif musterstatus == 'nofto':
                paymentDetail = PaymentDetail.objects.filter(worker__jobcard__jobcard = jobcard, status = '').values('fto__finyear').annotate(paymentDetailAmount = Sum('creditedAmount'), workDetailAmount = Sum('workDetail__totalWage'), jcs = Count('worker__jobcard__jobcard', distinct = True), fy = F('fto__finyear'))
            
            elif musterstatus == 'uncredited':
                paymentDetail = PaymentDetail.objects.filter(worker__jobcard__jobcard = jobcard).exclude(status = 'credited').values('fto__finyear').annotate(paymentDetailAmount = Sum('creditedAmount'), workDetailAmount = Sum('workDetail__totalWage'), jcs = Count('worker__jobcard__jobcard', distinct = True), fy = F('fto__finyear'))


            else:
                paymentDetail = PaymentDetail.objects.filter(worker__jobcard__jobcard = jobcard, status__icontains = musterstatus).values('fto__finyear').annotate(paymentDetailAmount = Sum('creditedAmount'), workDetailAmount = Sum('workDetail__totalWage'), jcs = Count('worker__jobcard__jobcard', distinct = True), fy = F('fto__finyear'))    

            
            
        serializer = PaymentDetailSerializer(paymentDetail, many=True)
        return JsonResponse(serializer.data, safe=False)



# Number of days it takes to process payments at each level for which we have information.  Right now, I get it only at the Panchayat level. 
@csrf_exempt
def paymentDays(request):
    if request.method == 'GET':
        ptid = request.GET.get('ptid', '')
        with connection.cursor() as cursor:
            q = "SELECT round(avg(datediff(paymentDate, dateTo))) as workToPay, round(avg(datediff(creditedDate, paymentDate))) as payToCred, round(avg(datediff(creditedDate, dateTo))) as workTocred from nrega_muster, nrega_workdetail where nrega_muster.id = nrega_workdetail.muster_id and creditedDate is not Null and panchayat_id = {} and paymentDate is not Null and dateTo is not Null;"

            cursor.execute(q.format(ptid))
            r = cursor.fetchall()[0]
            output = {'overall': {'workToPay': r[0], 'payToCred': r[1], 'workToCred': r[2]}}

            sixMonthsAgo = datetime.today() - timedelta(6*365/12)
            sixMonthsAgo = sixMonthsAgo.strftime('%Y-%m-%d')

            last6months = "SELECT round(avg(datediff(paymentDate, dateTo))) as workToPay, round(avg(datediff(creditedDate, paymentDate))) as payToCred, round(avg(datediff(creditedDate, dateTo))) as workTocred from nrega_muster, nrega_workdetail where nrega_muster.id = nrega_workdetail.muster_id and creditedDate is not Null and panchayat_id = {} and paymentDate is not Null and dateTo is not Null and creditedDate > '{}';".format(ptid, sixMonthsAgo)
            
            cursor.execute(last6months)
            l = cursor.fetchall()[0]
            output['lastSixMonths'] = {'workToPay': l[0], 'payToCred': l[1], 'workToCred': l[2]}
            

        return JsonResponse(output, safe=False)
'''
'''
@csrf_exempt
def employmentStatus(request):
    if request.method == 'GET':
        ptid=request.GET.get('ptid', '')
        jobcard = request.GET.get('jobcard', '')
        bid = request.GET.get('bid', '')

        if bid == '':
            if jobcard == '':
                employmentStatusByFy = WorkDetail.objects.filter(muster__panchayat__id = ptid).values('muster__finyear').annotate(fy = F('muster__finyear'), days = Sum('daysWorked'), dayWage = Avg('dayWage'), jcs = Count('zjobcard', distinct = True)).order_by('fy')

                serializer = EmploymentStatusSerializer(employmentStatusByFy, many=True)

            else:
                employmentStatusByFy = WorkDetail.objects.filter(worker__jobcard__jobcard = jobcard).values('muster__finyear').annotate(fy = F('muster__finyear'), days = Sum('daysWorked'), dayWage = Avg('dayWage'), jcs = Count('zjobcard', distinct = True)).order_by('fy')

                serializer = EmploymentStatusSerializer(employmentStatusByFy, many=True)

        else:
            employmentByPt = WorkDetail.objects.filter(muster__panchayat__block__id = bid).values('muster__panchayat__id', 'muster__finyear').annotate(ptid = F('muster__panchayat__id'), ptname = F('muster__panchayat__name'), fy = F('muster__finyear'), days = Sum('daysWorked'), avgWage = Avg('dayWage'), jcs = Count('zjobcard', distinct = True)).order_by('muster__panchayat__name', 'muster__finyear')

            serializer = EmploymentStatusByPtSerializer(employmentByPt, many=True)
            
        return JsonResponse(serializer.data, safe=False)



#--------------JOBCARD LEVEL INFO----------------

# Applicant__jobcard1 will be deprecated in some time.  At that point, replace it with the worker table.  Right now that table is not working. 
@csrf_exempt
def getInfoByJc(request):
    if request.method == 'GET':
        ptid=request.GET.get('ptid', '')
        jcno = request.GET.get('jobcard', '')
        mStatus = request.GET.get('musterstatus', '')
        if mStatus == '':
            paymentStatusByFy = WorkDetail.objects.filter(worker__jobcard__jobcard = jcno).values('muster__finyear').annotate(fy = F('muster__finyear'), amount = Sum('totalWage'), jcs = Count('worker__jobcard__jobcard', distinct = True)).order_by('fy')

        else:
            paymentStatusByFy = WorkDetail.objects.filter(worker__jobcard__jobcard = jcno, musterStatus = mStatus).values('muster__finyear').annotate(fy = F('muster__finyear'), amount = Sum('totalWage'), jcs = Count('worker__jobcard__jobcard', distinct = True)).order_by('fy')

        
        serializer = getInfoByJcSerializer(paymentStatusByFy, many=True)
        return JsonResponse(serializer.data, safe=False)
@csrf_exempt
def getWorkDetailsByJc(request):
    if request.method == 'GET':
        musterstatus = request.GET.get('musterstatus', '')
        workcode = request.GET.get('workcode', '')
        jcno = request.GET.get('jobcard', '')
        if musterstatus == '':
            transactions = WorkDetail.objects.filter(worker__jobcard__jobcard = jcno).order_by('-muster__dateTo')
        elif musterstatus == 'uncredited':
            transactions = WorkDetail.objects.filter(worker__jobcard__jobcard = jcno).exclude(musterStatus = 'credited').order_by('-muster__dateTo')
        else:
            transactions = WorkDetail.objects.filter(worker__jobcard__jobcard = jcno, musterStatus = musterstatus).order_by('-muster__dateTo')
        
        serializer = getWorkDetailsByJcSerializer(transactions, many=True)
        return JsonResponse(serializer.data, safe=False)

    
@csrf_exempt
def getTransactionByWorkCode(request):
    if request.method == 'GET':
        workcode = request.GET.get('workcode', '')
        jcno = request.GET.get('jobcard', '')
        if workcode == '':
            transactions = WorkDetail.objects.filter(worker__jobcard__jobcard = jcno).order_by('-muster__dateTo')
        else:
            transactions = WorkDetail.objects.filter(worker__jobcard__jobcard = jcno, muster__workCode = workcode).order_by('-muster__dateTo')
        
        serializer = getWorkDetailsByJcSerializer(transactions, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def workCreditStatusPt(request):
    if request.method == 'GET':
        musterstatus = request.GET.get('musterstatus', '')
        ptid = request.GET.get('ptid', '')
        if musterstatus == '':
            transactions = Muster.objects.filter(panchayat = ptid).values('workCode', 'workName').distinct()
            serializer = WorkSerializer(transactions, many=True)
        elif musterstatus == 'uncredited':
            transactions = WorkDetail.objects.filter(muster__panchayat = ptid).exclude(musterStatus = 'credited').values('muster__workCode', 'muster__workName').distinct().annotate(workCode = F('muster__workCode'), workName = F('muster__workName'), totalWage = Sum('totalWage'), daysWorked = Sum('daysWorked'))
            serializer = WorkCreditStatusPtSerializer(transactions, many=True)
        else:
            transactions = WorkDetail.objects.filter(muster__panchayat = ptid, musterStatus = musterstatus).values('muster__workCode', 'muster__workName').distinct().annotate(workCode = F('muster__workCode'), workName = F('muster__workName'), totalWage = Sum('totalWage'), daysWorked = Sum('daysWorked'))
            serializer = WorkCreditStatusPtSerializer(transactions, many=True)
            
        return JsonResponse(serializer.data, safe=False)

#-----------LIST OF PEOPLE WITH DIFFERENT ISSUES----------------------

def peopleByMusterStatus(request):
    if request.method == 'GET':
        musterstatus = request.GET.get('musterstatus', '')
        ptid = request.GET.get('ptid', '')
        # This would correspond to active workers
        if musterstatus == '':
            transactions = WorkDetail.objects.filter(panchayat = ptid).values('zjobcard').distinct().annotate(jc = F('zjobcard'), totalWage = Sum('totalWage'))
            serializer = JcsByMusterStatus(transactions, many=True)
        elif musterstatus == 'uncredited':
            transactions = WorkDetail.objects.filter(muster__panchayat = ptid).exclude(musterStatus = 'credited').values('zjobcard').distinct().annotate(jc = F('zjobcard'), totalWage = Sum('totalWage'))
            serializer = JcsByMusterStatus(transactions, many=True)
        else:
            transactions = WorkDetail.objects.filter(muster__panchayat = ptid, musterStatus = musterstatus).values('zjobcard').distinct().annotate(jc = F('zjobcard'), totalWage = Sum('totalWage'))
            serializer = JcsByMusterStatus(transactions, many=True)
            
        return JsonResponse(serializer.data, safe=False)

#-----------------TELANGANA DATA--------------------------
'''
Gets the latest pending payments from the postal website.  We have to test the data though. 
'''
@csrf_exempt
def getPostalData(request):
    if request.method == 'GET':
        jobcard = request.GET.get('jobcard', '')
        ptid = request.GET.get('ptid', '')
        if ptid == '':
            delayInfo = PendingPostalPayment.objects.filter(worker__jobcard__tjobcard__icontains = jobcard)
        else:
            delayInfo = PendingPostalPayment.objects.filter(worker__jobcard__panchayat__id = ptid, worker__jobcard__tjobcard__icontains = jobcard)

        delayInfo = delayInfo[:50]
        serializer = PostalPaymentSerializer(delayInfo, many=True)
            
        return JsonResponse(serializer.data, safe=False)

'''
Gets the total pending payments with the post office for a given Panchayat. 
'''
@csrf_exempt
def postalDelayPt(request):
    if request.method == 'GET':
        ptid = request.GET.get('ptid', '')
        balance = PendingPostalPayment.objects.filter(worker__jobcard__panchayat__id = ptid).values('worker__jobcard__panchayat__id').annotate(ptId = F('worker__jobcard__panchayat__id'), totBalance = Sum('balance'))

        serializer = PostalPaymentPtSerializer(balance, many=True)

        return JsonResponse(serializer.data, safe=False)

'''
TODO: PUT THIS INFORMATION IN THE CHATBOT
Gets individual transation details.  This starts with the payment detail table but also gets details from workDetail and muster tables.  It does a left join with the payment detail and so, we will get data where available for workdetail table and ignore it otherwise.  This is useful for Telangana, for which we have no corresponding information in the workDetail table. 

Currently, payment information is joined with the Applicant table but may have to change with Applicant table is replaced by the worker table.
'''
@csrf_exempt
def getPaymentDetail(request):
    if request.method == 'GET':
        jobcard = request.GET.get('jobcard', '')
        transactions = PaymentInfo.objects.filter(workDetail__worker__jobcard__jobcard = jobcard).order_by('-processDate')
        serializer = PaymentInfoSerializer(transactions, many=True)
#        serializer = PaymentDetailTransactionsSerializer(transactions, many=True)

            
        return JsonResponse(serializer.data, safe=False)

