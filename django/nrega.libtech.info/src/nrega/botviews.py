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
from rest_framework.response import Response
from rest_framework.views import APIView

import requests
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from nrega.models import Panchayat, State, Block, Jobcard, Applicant, WorkDetail, Muster, PaymentDetail, PendingPostalPayment, PanchayatStat, PanchayatCrawlQueue
from nrega.serializers import PanchayatSerializer, StateSerializer, StateSerializer1, SelectBlockSerializer, JobcardSerializer2, JobcardSerializer, PtAvgSerializer, getInfoByJcSerializer, getWorkDetailsByJcSerializer, MusterSerializer, WorkSerializer, WorkCreditStatusPtSerializer, JcsByMusterStatus, EmploymentStatusSerializer, PaymentDetailSerializer, PostalPaymentSerializer, PostalPaymentPtSerializer, PaymentDetailTransactionsSerializer, PanchayatStatSerializer, BlAvgSerializer, EmploymentStatusByPtSerializer, CrawlStatusSerializer, UserSerializer1

import json

def processRequest(req):
        textList = ["Hi there.  If you are new to the service, I recommend a tutorial.  If you have been here before, you might want to start by selecting a Panchayat."]
        options = ["Tutorial", "Select Panchayat"]
        contextOut = {"name":"welcome", "lifespan":2, "parameters":{}}

        res = (textList, options, contextOut)
       
        return res

class UserList(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer1(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data=request.data
        with open("/tmp/post.csv","w") as f:
          f.write(str(data))
#        serializer = UserSerializer(data=request.DATA)
#       if serializer.is_valid():
#           serializer.save()
#           return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        users = User.objects.all()
        serializer = UserSerializer1(users, many=True)
        return Response(serializer.data)


