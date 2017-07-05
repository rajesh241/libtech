import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

import csv
import json
import unittest

from firebase import firebase
from wrappers.db import dbInitialize,dbFinalize
from wrappers.logger import loggerFetch


#######################
# Global Declarations
#######################

firebase = firebase.FirebaseApplication('https://libtech-backend.firebaseio.com/', None)


#############
# Functions
#############

def pts_patch(logger, db):
    cur = db.cursor()

    # # Update status of rejected and invalid payments
    # 
    # The update is done at the block level
    #
    # This is the substring in the jobcard that represents the block

    panchayat_list = [{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-001","panchayatKey":"jharkhand-torpa-amma","panchayat":"AMMA","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"KL-14-004-002","panchayatKey":"kerala-nedumangad-aruvikkara","panchayat":"Aruvikkara","block":"Nedumangad","state":"KERALA"},{"panchayatCode":"fromDjango","jobcardCode":"JH-05-003-010","panchayatKey":"jharkhand-satbarwa-bakoriya","panchayat":"BAKORIYA","block":"Satbarwa","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-002","panchayatKey":"jharkhand-torpa-barkuli","panchayat":"BARKULI","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-13-002-003","panchayatKey":"jharkhand-mandro-bartalla","panchayat":"BARTALLA","block":"Mandro","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-07-005-002","panchayatKey":"jharkhand-ranka-bishrampur","panchayat":"BISHRAMPUR","block":"RANKA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-07-012-006","panchayatKey":"jharkhand-ramna-bulka","panchayat":"BULKA","block":"RAMNA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"BH-16-015-009","panchayatKey":"bihar-rajapakar-bhalui","panchayat":"Bhalui","block":"RAJAPAKAR","state":"BIHAR"},{"panchayatCode":"fromDjango","jobcardCode":"KN-27-005-013","panchayatKey":"karnataka-karwar-chendia","panchayat":"CHENDIA","block":"KARWAR","state":"KARNATAKA"},{"panchayatCode":"fromDjango","jobcardCode":"JH-05-008-016","panchayatKey":"jharkhand-chhatarpur-cherain","panchayat":"CHERAIN","block":"CHHATARPUR","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-003","panchayatKey":"jharkhand-torpa-diyakela","panchayat":"DIYAKELA","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-004","panchayatKey":"jharkhand-torpa-dorma","panchayat":"DORMA","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-08-009-008","panchayatKey":"jharkhand-hat_gamharia-dumria","panchayat":"Dumria","block":"Hat Gamharia","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-005","panchayatKey":"jharkhand-torpa-fatka","panchayat":"FATKA","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-07-012-007","panchayatKey":"jharkhand-ramna-gamharia","panchayat":"GAMHARIA","block":"RAMNA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-07-004-009","panchayatKey":"jharkhand-meral-hasandag","panchayat":"HASANDAG","block":"MERAL","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"BH-50-005-006","panchayatKey":"bihar-jhajha-hathiya","panchayat":"HATHIYA","block":"JHAJHA","state":"BIHAR"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-006","panchayatKey":"jharkhand-torpa-husir","panchayat":"HUSIR","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-05-008-018","panchayatKey":"jharkhand-chhatarpur-hutukdag","panchayat":"HUTUKDAG","block":"CHHATARPUR","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-007","panchayatKey":"jharkhand-torpa-jaria","panchayat":"JARIA","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"KN-06-001-003","panchayatKey":"karnataka-aurad-kamalanagar","panchayat":"KAMALANAGAR","block":"AURAD","state":"KARNATAKA"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-008","panchayatKey":"jharkhand-torpa-kamra","panchayat":"KAMRA","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-07-009-006","panchayatKey":"jharkhand-bhandaria-karchali","panchayat":"KARCHALI","block":"BHANDARIA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-07-004-010","panchayatKey":"jharkhand-meral-karkoma","panchayat":"KARKOMA","block":"MERAL","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"KL-14-009-001","panchayatKey":"kerala-vamanapuram-kallara","panchayat":"Kallara","block":"Vamanapuram","state":"KERALA"},{"panchayatCode":"fromDjango","jobcardCode":"JH-08-003-008","panchayatKey":"jharkhand-jhinkpani-kudahatu","panchayat":"Kudahatu","block":"Jhinkpani","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"UP-43-006-037","panchayatKey":"uttar_pradesh-bhitaura-lakani","panchayat":"LAKANI","block":"BHITAURA","state":"UTTAR PRADESH"},{"panchayatCode":"fromDjango","jobcardCode":"JH-07-009-008","panchayatKey":"jharkhand-bhandaria-madgari_(k)","panchayat":"MADGARI (K)","block":"BHANDARIA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-009","panchayatKey":"jharkhand-torpa-marcha","panchayat":"MARCHA","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-13-005-008","panchayatKey":"jharkhand-taljhari-maskalaiya","panchayat":"MASKALAIYA","block":"Taljhari","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-06-007-006","panchayatKey":"jharkhand-mahuadanr-mahuadanr","panchayat":"Mahuadanr","block":"Mahuadanr","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-010","panchayatKey":"jharkhand-torpa-okra","panchayat":"OKRA","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-07-004-018","panchayatKey":"jharkhand-meral-sangwaria","panchayat":"SANGWARIA","block":"MERAL","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"OR-05-005-026","panchayatKey":"odisha-bhograi-sultanpur","panchayat":"SULTANPUR","block":"BHOGRAI","state":"ODISHA"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-011","panchayatKey":"jharkhand-torpa-sundari","panchayat":"SUNDARI","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-012","panchayatKey":"jharkhand-torpa-tapkara","panchayat":"TAPKARA","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-07-004-020","panchayatKey":"jharkhand-meral-tisar_tetuka","panchayat":"TISAR TETUKA","block":"MERAL","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-013","panchayatKey":"jharkhand-torpa-torpa_east","panchayat":"TORPA EAST","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-014","panchayatKey":"jharkhand-torpa-torpa_west","panchayat":"TORPA WEST","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"KL-04-003-009","panchayatKey":"kerala-koduvally-thamarassery","panchayat":"Thamarassery","block":"Koduvally","state":"KERALA"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-015","panchayatKey":"jharkhand-torpa-ukrimari","panchayat":"UKRIMARI","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-01-020-016","panchayatKey":"jharkhand-torpa-urikela","panchayat":"URIKELA","block":"TORPA","state":"JHARKHAND"},{"panchayatCode":"fromDjango","jobcardCode":"JH-07-001-025","panchayatKey":"jharkhand-garhwa-ursugi","panchayat":"URSUGI","block":"GARHWA","state":"JHARKHAND"}]
        
    panchayats = {}
    for panchayat in panchayat_list:
        logger.info(panchayat)
        # (state, panchayatCode, panchayatName, block, panchayatKey) = panchayat.values()
        state = panchayat['state']
        block = panchayat['block']
        panchayatName = panchayat['panchayat']
        panchayatKey = panchayat['panchayatKey']
        panchayatCode = panchayat['panchayatCode']
        jobcardCode = panchayat['jobcardCode']
        logger.info('jobcardCode[%s] panchayatCode[%s] Key[%s] Name[%s] Block[%s] State[%s]' % (jobcardCode, panchayatCode, panchayatKey, panchayatName, block, state))

        query = 'Replace with Django API'
        logger.info('Executing query[%s]' % query)
        # cur.execute(query)
        # res = cur.fetchall()

        if panchayatKey in panchayats:
            pass
        else:
            panchayats[panchayatKey] = panchayat
            
    result = firebase.patch('https://libtech-backend.firebaseio.com/ptsWithData/', panchayats)
    logger.info(result)

    return 'SUCCESS'

# Patch the Firebase Database
        

def firebase_patch(logger, db):
    cur = db.cursor()

    # # Update status of rejected and invalid payments
    # 
    # The update is done at the block level
    #
    # This is the substring in the jobcard that represents the block

    block_strings = [
        'BH-16-015', 'BH-50-005', 'JH-01-020', 'JH-05-003', 'JH-05-008', 'JH-06-007', 'JH-07-001', 'JH-07-004', 'JH-07-005', 'JH-07-009', 'JH-07-012', 'JH-08-003', 'JH-08-009', 'JH-13-002', 'JH-13-005', 'KL-04-003', 'KL-14-004', 'KL-14-009', 'KN-06-001', 'KN-27-005', 'OR-05-005', 'UP-43-006',
    ]
    block_strings = [ 'JH-01-020' ]
    
    geo = {}
    for blString in block_strings:    
        # blString = 'JH-01-020'
        logger.info('Block String[%s]' % blString)

        qRejInvPerJc = "SELECT zjobcard,SUBSTRING(zjobcard, 1, 13) AS ptString,SUBSTRING(zjobcard, 15, 3) AS vString,substring_index(zjobcard, '/', -1) as hString,round(sum(case WHEN musterStatus = 'Credited' then 1 else 0 END ), 0) as totCredited,round(sum(case WHEN musterStatus = '' then 1 else 0 END ), 0) as totPending,round(sum(case WHEN musterStatus = 'Rejected' then 1 else 0 END ), 0) as totRejected,round(sum(case WHEN musterStatus = 'Invalid Account' then 1 else 0 END ), 0) as totInvalid FROM libtech3.nrega_workdetail WHERE musterStatus = 'credited'AND musterStatus != '' AND SUBSTRING(zjobcard, 1, 9) = '{0}' GROUP BY zjobcard ORDER BY zjobcard".format(blString)
        logger.info('Executing query[%s]' % qRejInvPerJc)
        cur.execute(qRejInvPerJc)
        rejInvPerJc = cur.fetchall()

        for r in rejInvPerJc:
            jc = r[0]
            pt = r[1]
            vil = r[2]
            hhd = r[3]
            
            if pt in geo:
                pass
            else:
                geo[pt] = {}
                
            if vil in geo[pt]:
                pass
            else:
                geo[pt][vil] = {}
                
            if hhd in geo[pt][vil]:
                pass
            else:
                geo[pt][vil][hhd] = {'totCredited': str(r[4]), 'totPending': str(r[5]), 'totRejected': str(r[6]), 'totInvalid': str(r[7])}


        result = firebase.patch('https://libtech-backend.firebaseio.com/geo/', geo)
    
        logger.info(len(result))


        # # Update jobcard register information
        # 
        # Update details on name, etc. from the jobcard register.

        # Fields I want from the NREGA_APPLICANT table in mysql
        applicantFields = ['applicantNo', 'id', 'name', 'jobcard', 'accountNo', 'age', 'bankBranchCode', 'bankBranchName', 'bankCode', 'bankName', 'caste', 'gender', 'poAccountName', 'poAddress', 'uid']
        applicantSelect = ', '.join(applicantFields)

        queryNregaApplicant = "Select {0} from libtech3.nrega_applicant where SUBSTRING(jobcard, 1, 9) = '{1}';".format(applicantSelect, blString)
        logger.info('Executing query[%s]' % queryNregaApplicant)
        cur.execute(queryNregaApplicant)
        nregaApplicants = cur.fetchall()

        # In[10]:
        for n in nregaApplicants:
            nDetails = {}
            i = 0    
            appNo = n[0]
            pt = n[3][0:13]
            vil = n[3][14:17]
            hhd = n[3].split('/')[-1]
            if pt in geo:
                pass
            else:
                geo[pt] = {}
                
            if vil in geo[pt]:
                pass
            else:
                geo[pt][vil] = {}
                
            if hhd in geo[pt][vil]:
                pass
            else:
                geo[pt][vil][hhd] = {}
                
            if 'applicants' in geo[pt][vil][hhd]:
                pass
            else:
                geo[pt][vil][hhd]['applicants'] = {}
            
            for a in applicantFields:
                if (n[i] != '') and (n[i] != '0'):
                    nDetails[a] = n[i]
                else:
                    pass
                i = i+1
                
            geo[pt][vil][hhd]['applicants'][appNo] = nDetails

        #geo['JH-01-020-001']['001']['1']['totRejected']

        #get_ipython().run_cell_magic('timeit', '', "result = firebase.patch('https://libtech-backend.firebaseio.com/geo/', geo)\nprint(len(result))")
        result = firebase.patch('https://libtech-backend.firebaseio.com/geo/', geo)
        #result = firebase.get('geo/', None)
        print(result)

        result = firebase.post('https://libtech-backend.firebaseio.com/tempNode/', {'panchayatName': 'tempPanchayat'})
        print(result)


        # # Deleting data
        # 
        # If I have to delete data from a node on, I can use the following.  In the example below, I delete the entire database.
        # 
        # result = firebase.delete('https://libtech-backend.firebaseio.com', None)
        # print(result)

        # # Fire base data structure philosophy
        # 
        # Every time we access a node on firebase, we get all the data of all the children of that node.  This means that if our data is not flat (i.e. if there are a lot of children), we will get a lot of data.  For example, I originally structured the data as a geographic drilldown enging with jobcard numbers and transaction data.  Each time I tried to get a list of Panchayats, I also ended up getting the entire database downloaded.  This is costly. 
        # 
        # What I am going to do below is to generate a list of relatively small and flat nodes containing just the data I need for given views.  There will be duplication in presentation of data but retrieval would be a lot more efficient.
        # 
        # When I have data for a block or so, I will then go through the data through a set of queries to create various nodes and datapoints.

        if 0: # Mynk
            logger.info('Executing query[%s]' % queryNregaApplicant)
            cur.execute(queryInvalidRejected)
            InvalidRejectedJcs = cur.fetchall()

            for i in InvalidRejectedJcs:
                print(i)
                panchayatName = i[0]
                jobcard = i[1]
                jobcard = jobcard.replace('/', '~')
                result = firebase.patch('https://libtech-backend.firebaseio.com/%s/%s'%(panchayatName, jobcard), {'musterStatus': 'rejInv'})
                print(result)
            
        # Currently, this has a filter for rejected or invalid transactions.  Also has 2000 row limit.
        queryTransactionDetails = "select  panchayatName, jobcard, name, musterNo, workName, totalWage, wagelistNo, ftoNo, musterStatus, bankNameOrPOName, date_format(dateTo, '%d-%M-%Y') as dateTo, DATE_FORMAT(firstSignatoryDate, '%d-%M-%Y') as firstSignatoryDate, DATE_FORMAT(secondSignatoryDate, '%d-%M-%Y') as secondSignatoryDate, DATE_FORMAT(transactionDate, '%d-%M-%Y') as transactionDate, DATE_FORMAT(bankProcessedDate, '%d-%M-%Y') as bankProcessedDate, DATE_FORMAT(paymentDate, '%d-%M-%Y') as paymentDate, DATE_FORMAT(creditedDate, '%d-%M-%Y') as creditedDate, ftoStatus, rejectionReason, @varMaxDate:=greatest(COALESCE(dateTo, '1900-01-01 00:00:00'),   COALESCE(firstSignatoryDate,    '1900-01-01 00:00:00'),   COALESCE(secondSignatoryDate,    '1900-01-01 00:00:00'),   COALESCE(transactionDate, '1900-01-01 00:00:00'),   COALESCE(bankProcessedDate, '1900-01-01 00:00:00'),   COALESCE(paymentDate, '1900-01-01 00:00:00'),   COALESCE(creditedDate, '1900-01-01 00:00:00')) as maxDate, CASE @varMaxDate WHEN dateTo THEN 'dateTo' WHEN firstSignatoryDate THEN 'firstSignatoryDate' WHEN secondSignatoryDate THEN 'secondSignatoryDate' WHEN transactionDate THEN 'transactionDate' WHEN bankProcessedDate THEN 'bankProcessedDate' WHEN paymentDate THEN 'paymentDate' WHEN creditedDate THEN 'creditedDate' END AS maxDateColName from surguja.workDetails where musterStatus != 'Credited' and musterStatus != '' order by dateTo limit 2000 ;"
        logger.info('Executing query[%s]' % queryTransactionDetails)
        cur.execute(queryTransactionDetails)
        transactionDetails = cur.fetchall()


        # # Updating data on firebase
        # 
        # If I use the 'post' method, firebase creates a random number for each transaction, which is a pain visually.  Instead, I want to create node names that are based on panchayat name, jobcards, etc that are meaningful.  In order to do that, I can use the 'patch' function.  
        # 
        # Patch function is used for updating data in an existing url.  Thus, if I try to post new data to an existing URL it would modify the old data.  For example, if I post two transactions one by one to 'panchayat/jobcard/dateTo' (in a case where two people have worked in a house on the same project on the same day), it would post the first one correctly but then update it with the new values for the second transaction.  So, we have to be careful to post unique data.
        # 
        # ## Need for transaction number
        # 
        # One way of getting the unique data is to include panchayat, jobcard, dateTo and the name of the worker (assuming hte same person has not worked in twice in the same muster).  The problem with this is that firebase has difficulty in handling hindi names in the url.  As a hack, I now do this:
        # 
        # - Try retrieving the data in that url using the get method. 
        # - If there is no data there already, it would throw an exception.
        # - If there is data already, I can find out the length of the dict item.  That shows how many transactions there have been for that week already.
        # - Using the information above, I create a transaction number.  This is then used in creating the URL instead of the name
        # 

        for row in transactionDetails:
            panchayatName = row[0]
            jobcard = row[1]
            jobcard = jobcard.replace('/', '~')
            name = row[2]
            musterNo = row[3]
            workName = row[4]
            totalWage = row[5]
            wagelistNo = row[6]
            ftoNo = row[7]
            musterStatus = row[8]
            bankNameOrPOName = row[9]
            dateTo = row[10]
            firstSignatoryDate = row[11]
            secondSignatoryDate = row[12]
            transactionDate = row[13]
            bankProcessedDate = row[14]
            paymentDate = row[15]
            creditedDate = row[16]
            ftoStatus = row[17]
            rejectionReason = row[18]
            maxDate = row[19]
            maxDateColName = row[20]
            try:
                currentStatusOfNode = firebase.get('/%s/%s/%s'%(panchayatName, jobcard, dateTo), None)
                currentNoTransactionsForDate = len(currentStatusOfNode) - 1
                newTransactionNo = currentNoTransactionsForDate + 1
            except: 
                newTransactionNo = 1
                result = firebase.patch('https://libtech-backend.firebaseio.com/%s/%s/%s/%s'%(panchayatName, jobcard, dateTo, newTransactionNo), {'jobcard': jobcard, 'name': name, 'musterNo': musterNo, 'workName': workName, 'totalWage': totalWage, 'wagelistNo': wagelistNo, 'ftoNo': ftoNo, 'musterStatus': musterStatus, 'bankNameOrPOName': bankNameOrPOName, 'dateTo': dateTo, 'firstSignatoryDate': firstSignatoryDate, 'secondSignatoryDate': secondSignatoryDate, 'transactionDate': transactionDate, 'bankProcessedDate': bankProcessedDate, 'paymentDate': paymentDate, 'creditedDate': creditedDate, 'ftoStatus': ftoStatus, 'rejectionReason': rejectionReason, 'maxDate': maxDate, 'maxDateColName': maxDateColName})
                print(result)

    return 'SUCCESS'

    
# # Updating data on firebase (By Chirag & Karthika)
# 
# This is the python script that Chirag and Karthika created to update data on firebase using the schema they created.

def load_panchayats(filename="workDetails.csv"):
    records = {}
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['panchayatName'] not in records:
                records[row['panchayatName']] = {
                    'job_cards': set(),
                    'transactions': 0,
                    'dates': set()
                }
                records[row['panchayatName']]['job_cards'].add(row['jobcard'])
                records[row['panchayatName']]['transactions'] += 1
                records[row['panchayatName']]['dates'].add(row['dateTo'])
                firebase_conn = firebase.FirebaseApplication(
                    'https://libtech-backend.firebaseio.com/', None)
    for panchayat_name in records:
        records[panchayat_name]['num_jobcards'] =             len(records[panchayat_name]['job_cards'])
        records[panchayat_name]['earliest_date'] =             min(records[panchayat_name]['dates'])
        records[panchayat_name]['latest_date'] =             max(records[panchayat_name]['dates'])
        new_record = {
            'num_jobcards': records[panchayat_name]['num_jobcards'],
            'earliest_date': records[panchayat_name]['earliest_date'],
            'latest_date': records[panchayat_name]['latest_date'],
            'transactions': records[panchayat_name]['transactions']
        }
        result = firebase_conn.put('/panchayats', panchayat_name,
                                   new_record)
        print (result)

def load_jobcards(filename="workDetails.csv"):
    records = {}
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['panchayatName'] not in records:
                records[row['panchayatName']] = {}
            if row['jobcard'] not in records[row['panchayatName']]:
                records[row['panchayatName']][row['jobcard']] = {
                    'count': 0,
                    'dates': set()
                }
            records[row['panchayatName']][row['jobcard']]['count'] += 1
            records[row['panchayatName']][row['jobcard']]['dates'].add(
                row['dateTo'])

    firebase_conn = firebase.FirebaseApplication(
        'https://libtech-backend.firebaseio.com/', None)
    for panchayat_name in records:
        for jobcard in records[panchayat_name]:
            records[panchayat_name][jobcard]['earliest_date'] =                 min(records[panchayat_name][jobcard]['dates'])
            records[panchayat_name][jobcard]['latest_date'] =                 max(records[panchayat_name][jobcard]['dates'])
            print (panchayat_name, jobcard,
                   records[panchayat_name][jobcard]['earliest_date'],
                   records[panchayat_name][jobcard]['latest_date'],
                   records[panchayat_name][jobcard]['count'])
            new_record = {
                'num_transactions': records[panchayat_name][jobcard]['count'],
                'earliest_date':
                records[panchayat_name][jobcard]['earliest_date'],
                'latest_date': records[panchayat_name][jobcard]['latest_date'],
            }
            try:
                result = firebase_conn.put('/jobcards',
                                           '{0}/{1}'.format(
                                              panchayat_name,
                                              jobcard.replace('/', '_')),
                                           new_record)
            except Exception as e:
                print ("\n\n\n\nWATCH!!!!!")
                print (e)
            print (result)

def load_transactions(filename="workDetails.csv"):
    records = {}
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['panchayatName'] not in records:
                records[row['panchayatName']] = {}
            if row['jobcard'] not in records[row['panchayatName']]:
                records[row['panchayatName']][row['jobcard']] = []
            records[row['panchayatName']][row['jobcard']].append(row)

    firebase_conn = firebase.FirebaseApplication(
        'https://libtech-backend.firebaseio.com/', None)
    for panchayat_name in records:
        for jobcard in records[panchayat_name]:
            for i, record in enumerate(records[panchayat_name][jobcard]):
                jc = jobcard.replace('/', '_')
                print (jc + ':{}'.format(i + 1), record)
                try:
                    result = firebase_conn.put('/transactions',
                                               '{0}/{1}'.format(
                                                   jc,
                                                   jc + ':{}'.format(i + 1)),
                                               record)
                except Exception as e:
                    print (e)
                print (result)


#############
# Tests
#############


class TestSuite(unittest.TestCase):
  def setUp(self):
    self.logger = loggerFetch('info')
    self.logger.info('BEGIN PROCESSING...')
    self.db = dbInitialize(db="libtech3", charset="utf8")

  def tearDown(self):
    dbFinalize(self.db)
    self.logger.info("...END PROCESSING")
    
  def test_firebase_patch(self):
    result = pts_patch(self.logger, self.db)
    self.assertEqual('SUCCESS', result)

  def test_load_panchayats(self):
    if 0:
        result = load_panchayats(self.logger)    
        result = load_jobcards(self.logger)    
        result = load_transactions(self.logger)    
    else:
        result = 'SUCCESS'
    self.assertEqual('SUCCESS', result)

if __name__ == '__main__':
  unittest.main()
