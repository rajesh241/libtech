from django.contrib.auth.models import User, Group
from rest_framework import serializers
from nrega.models import State,District,Block,Panchayat, Jobcard, WorkDetail, Muster, PaymentDetail, PendingPostalPayment, Applicant, PanchayatStat, PanchayatCrawlQueue, Worker

#----------------RECORDS TO HELP SELECT THE RIGHT PANCHAYAT AND JOBCARD-----------
# The following functions provide data to help the chatbot user select the right Panchayat and the right jobcard for which they want data.

class CrawlStatusSerializer(serializers.ModelSerializer):
  class Meta:
    model = PanchayatCrawlQueue
    fields = ('panchayat', 'isComplete', 'isError', 'status')
    
class StateSerializer1(serializers.ModelSerializer):
  state = serializers.CharField()
  block = serializers.CharField()
  transactions = serializers.IntegerField()
  class Meta:
    model = State
    fields = ('state', 'block', 'transactions')

class StateSerializer(serializers.ModelSerializer):
  class Meta:
    model = State
    fields = ('name', 'id')

class DistrictSerializer(serializers.ModelSerializer):
  state = StateSerializer()
  class Meta:
    model = District
    fields = ('name', 'id', 'state')


# This returns details about the block in the Panchayat serializer
class BlockSerializer(serializers.ModelSerializer):
  district = DistrictSerializer()
  class Meta:
    model = Block
    fields = ('id', 'name', 'district')


class PanchayatSerializer(serializers.ModelSerializer):
    block = BlockSerializer()
    class Meta:
        model = Panchayat
        fields = ('id', 'name', 'block')

    
class PanchayatStatSerializer(serializers.ModelSerializer):
  panchayat = PanchayatSerializer()
  class Meta:
    model = PanchayatStat
    fields = ('panchayat', 'workDaysAccuracyIndex')


# This returns block details along with district and state names.
class SelectBlockSerializer(serializers.ModelSerializer):
  district = DistrictSerializer()
  class Meta:
    model = Block
    fields = ('id', 'name', 'district')


class JobcardSerializer(serializers.ModelSerializer):
  class Meta:
    model = Jobcard
    fields = ('jobcard', 'panchayat', 'headOfHousehold', 'group', 'tjobcard')


class JobcardSerializer2(serializers.ModelSerializer):
  totalTrans = serializers.IntegerField()
  jobcard = serializers.CharField()
  headOfHousehold = serializers.CharField()
  class Meta:
    model = WorkDetail
    fields = ('jobcard', 'totalTrans', 'headOfHousehold')


#----------INFO ABOUT THE PANCHAYAT-----------------
class BlAvgSerializer(serializers.ModelSerializer):
  totalWage = serializers.IntegerField()
  jcs = serializers.IntegerField()
  ptid = serializers.IntegerField()
  ptname = serializers.CharField()
  class Meta:
    model = WorkDetail
    fields = ('ptid', 'ptname', 'totalWage', 'jcs')
  
class PtAvgSerializer(serializers.ModelSerializer):
  totalWage = serializers.IntegerField()
  fy = serializers.CharField()
  jcs = serializers.IntegerField()
#  ptid = serializers.IntegerField()
#  ptname = serializers.CharField()
  class Meta:
    model = WorkDetail
    fields = ('fy', 'totalWage', 'jcs')

class ApplicantSerializer(serializers.ModelSerializer):
  class Meta:
    model = Applicant
    fields = ('name', 'jobcard1')

class MusterDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = Muster
    fields = ('workName', 'dateTo')

class WorkDetailSerializer(serializers.ModelSerializer):
  muster = MusterDetailSerializer()
  class Meta:
    model = WorkDetail
    fields = ('daysWorked', 'totalWage', 'muster')

class PaymentDetailTransactionsSerializer(serializers.ModelSerializer):
  applicant = ApplicantSerializer()
  workDetail = WorkDetailSerializer()
  creditedAmount = serializers.IntegerField()
  disbursedAmount = serializers.IntegerField()  
  class Meta:
    model = PaymentDetail
    fields = ('applicant', 'creditedAmount', 'processDate', 'status', 'disbursedAmount', 'disbursedDate', 'rejectionReason', 'workDetail')

class PaymentDetailSerializer(serializers.ModelSerializer):
  workDetailAmount = serializers.IntegerField()
  paymentDetailAmount = serializers.IntegerField()  
  jcs = serializers.IntegerField()
  fy = serializers.IntegerField()
  class Meta:
    model = PaymentDetail
    fields = ('fy', 'workDetailAmount', 'paymentDetailAmount', 'jcs')

class EmploymentStatusByPtSerializer(serializers.ModelSerializer):
  avgWage = serializers.IntegerField()
  days = serializers.IntegerField()
  jcs = serializers.IntegerField()
  ptid = serializers.IntegerField()
  ptname = serializers.CharField()
  fy = serializers.IntegerField()
  class Meta:
    model = WorkDetail
    fields = ('ptid', 'ptname', 'fy', 'days', 'avgWage', 'jcs')

    
class EmploymentStatusSerializer(serializers.ModelSerializer):
  days = serializers.IntegerField()
  jcs = serializers.IntegerField()
  fy = serializers.IntegerField()
  dayWage = serializers.IntegerField()
  class Meta:
    model = WorkDetail
    fields = ('fy', 'days', 'jcs', 'dayWage')


class getInfoByJcSerializer(serializers.ModelSerializer):
  amount = serializers.CharField()
  fy = serializers.CharField()
  class Meta:
    model = WorkDetail
    fields = ('fy', 'amount')
  
#----------INFORMATION PERTAINING TO THE SELECTED JOBCARD---------------
# Once a jobcard has been selected by the user, the following functions extract information relevant to the jobcard.

class WorkSerializer(serializers.ModelSerializer):
  class Meta:
    model = Muster
    fields = ('workName', 'workCode')

class WorkCreditStatusPtSerializer(serializers.ModelSerializer):
  workCode = serializers.CharField()
  workName = serializers.CharField()
  totalWage = serializers.CharField()
  daysWorked = serializers.CharField()
  class Meta:
    model = WorkDetail
    fields = ('totalWage', 'daysWorked', 'workCode', 'workName')
class MusterSerializer(serializers.ModelSerializer):
  class Meta:
    model = Muster
    fields = ('dateTo', 'paymentDate', 'workName', 'workCode')

class getWorkDetailsByJcSerializer(serializers.ModelSerializer):
  muster = MusterSerializer()
  class Meta:
    model = WorkDetail
    fields = ('daysWorked', 'totalWage', 'musterStatus', 'creditedDate', 'muster')

class WorkerSerializer(serializers.ModelSerializer):
  jobcard = JobcardSerializer()
  class Meta:
    model = Worker
    fields = ('id', 'name', 'fatherHusbandName', 'jobcard')


class PostalPaymentSerializer(serializers.ModelSerializer):
  worker = WorkerSerializer()
  class Meta:
    model = PendingPostalPayment
    fields = ('id', 'balance', 'worker')


class PostalPaymentPtSerializer(serializers.ModelSerializer):
  ptId = serializers.CharField()
  totBalance = serializers.IntegerField()
  class Meta:
    model = PendingPostalPayment
    fields = ('ptId', 'totBalance')

    
class JcsByMusterStatus(serializers.ModelSerializer):
  jc = serializers.CharField()
  totalWage = serializers.IntegerField()  
  class Meta:
    model = WorkDetail
    fields = ('totalWage', 'jc')
#---------ADMIN RECORDS-----------------------    

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

