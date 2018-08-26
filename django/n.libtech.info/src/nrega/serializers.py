from django.contrib.auth.models import User, Group
from rest_framework import serializers
from nrega.models import State,District,Block,Panchayat,Wagelist,PaymentInfo,Muster,WorkDetail,FTO,Worker,CrawlQueue,PanchayatStat,Jobcard


class CrawlStatusSerializer(serializers.ModelSerializer):
  class Meta:
    model = CrawlQueue
    fields = ('panchayat', 'isComplete', 'isError', 'status', 'crawlStartDate', 'crawlAttemptDate')

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
        fields = ('id', 'code','name', 'block')

class PanchayatStatSerializer(serializers.ModelSerializer):
  panchayat = PanchayatSerializer()
  class Meta:
    model = PanchayatStat
    fields = ('panchayat', 'workDaysAccuracyIndex')


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


class WorkerSerializer5(serializers.ModelSerializer):
  class Meta:
    model = Worker
    fields=('id','name')

class WagelistSerializer5(serializers.ModelSerializer):
  class Meta:
    model = Wagelist
    fields = ('id','wagelistNo','contentFile')
class FTOSerializer5(serializers.ModelSerializer):
  class Meta:
    model = FTO
    fields = ('id','ftoNo','contentFile')

class MusterSerializer5(serializers.ModelSerializer):
  class Meta:
    model = Muster
    fields = ('id','panchayat','musterNo','dateFrom','dateTo','workCode','workName','contentFile')

class PaymentInfoSerializer5(serializers.ModelSerializer):
  wagelist=WagelistSerializer5()
  fto=FTOSerializer5()
  class Meta:
    model = PaymentInfo
    fields = ('id','status','rejectionReason','accountNo','transactionDate','processDate','creditedAmount','primaryAccountHolder','wagelist','fto')

class WorkDetailSerializer5(serializers.ModelSerializer):
  worker=WorkerSerializer5()
  muster=MusterSerializer5()
  paymentInfo=PaymentInfoSerializer5(read_only=True, many=True)
  class Meta:
    model = WorkDetail
    fields=('id','status','musterStatus','worker','muster','paymentInfo')

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
  class Meta:
    model = WorkDetail
    fields = ('fy', 'totalWage', 'jcs')


class MusterDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = Muster
    fields = ('workName', 'dateTo')

class WorkDetailSerializer(serializers.ModelSerializer):
  muster = MusterDetailSerializer()
  class Meta:
    model = WorkDetail
    fields = ('daysWorked', 'totalWage', 'muster')



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


class WorkerSerializer1(serializers.ModelSerializer):
  jobcard = JobcardSerializer()
  class Meta:
    model = Worker
    fields = ('id', 'name', 'applicantNo','fatherHusbandName', 'jobcard')

class WorkerSerializer(serializers.ModelSerializer):
  jobcard = JobcardSerializer()
  class Meta:
    model = Worker
    fields = ('id', 'name', 'applicantNo','fatherHusbandName', 'jobcard')


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

class UserSerializer1(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username', 'first_name', 'last_name', 'email')

class WorkDetailSerializer_new(serializers.ModelSerializer):
  class Meta:
    model = WorkDetail
    fields = ('worker', 'zname', 'zjobcard')

class PaymentInfoSerializer(serializers.ModelSerializer):
  status = serializers.CharField()
  rejectionReason = serializers.CharField()
  creditedAmount = serializers.CharField()
  accountNo = serializers.CharField()
  workDetail = WorkDetailSerializer_new()
  class Meta:
    model = PaymentInfo
    fields = ('status', 'rejectionReason', 'creditedAmount', 'accountNo', 'workDetail')
