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

firebase = firebase.FirebaseApplication('https://libtech-app.firebaseio.com/', None)

jobcard2panchayats = {"BH-50-005-006":{"block":"JHAJHA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"BH-50-005-006","name":"HATHIYA","slug":"bihar_jhajha_hathiya","state":"BIHAR"},"BH-16-015-009":{"block":"RAJAPAKAR","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"BH-16-015-009","name":"Bhalui","slug":"bihar_rajapakar_bhalui","state":"BIHAR"},"JH-07-009-006":{"block":"BHANDARIA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-07-009-006","name":"KARCHALI","slug":"jharkhand_bhandaria_karchali","state":"JHARKHAND"},"JH-07-009-008":{"block":"BHANDARIA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-07-009-008","name":"MADGARI (K)","slug":"jharkhand_bhandaria_madgari-k","state":"JHARKHAND"},"JH-05-008-016":{"block":"CHHATARPUR","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-05-008-016","name":"CHERAIN","slug":"jharkhand_chhatarpur_cherain","state":"JHARKHAND"},"JH-05-008-018":{"block":"CHHATARPUR","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-05-008-018","name":"HUTUKDAG","slug":"jharkhand_chhatarpur_hutukdag","state":"JHARKHAND"},"JH-07-001-025":{"block":"GARHWA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-07-001-025","name":"URSUGI","slug":"jharkhand_garhwa_ursugi","state":"JHARKHAND"},"JH-08-009-008":{"block":"Hat Gamharia","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-08-009-008","name":"Dumria","slug":"jharkhand_hat-gamharia_dumria","state":"JHARKHAND"},"JH-08-003-008":{"block":"Jhinkpani","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-08-003-008","name":"Kudahatu","slug":"jharkhand_jhinkpani_kudahatu","state":"JHARKHAND"},"JH-06-007-006":{"block":"Mahuadanr","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-06-007-006","name":"Mahuadanr","slug":"jharkhand_mahuadanr_mahuadanr","state":"JHARKHAND"},"JH-13-002-003":{"block":"Mandro","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-13-002-003","name":"BARTALLA","slug":"jharkhand_mandro_bartalla","state":"JHARKHAND"},"JH-07-004-009":{"block":"MERAL","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-07-004-009","name":"HASANDAG","slug":"jharkhand_meral_hasandag","state":"JHARKHAND"},"JH-07-004-010":{"block":"MERAL","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-07-004-010","name":"KARKOMA","slug":"jharkhand_meral_karkoma","state":"JHARKHAND"},"JH-07-004-018":{"block":"MERAL","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-07-004-018","name":"SANGWARIA","slug":"jharkhand_meral_sangwaria","state":"JHARKHAND"},"JH-07-004-020":{"block":"MERAL","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-07-004-020","name":"TISAR TETUKA","slug":"jharkhand_meral_tisar-tetuka","state":"JHARKHAND"},"JH-07-012-006":{"block":"RAMNA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-07-012-006","name":"BULKA","slug":"jharkhand_ramna_bulka","state":"JHARKHAND"},"JH-07-012-007":{"block":"RAMNA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-07-012-007","name":"GAMHARIA","slug":"jharkhand_ramna_gamharia","state":"JHARKHAND"},"JH-07-005-002":{"block":"RANKA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-07-005-002","name":"BISHRAMPUR","slug":"jharkhand_ranka_bishrampur","state":"JHARKHAND"},"JH-05-003-010":{"block":"Satbarwa","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-05-003-010","name":"BAKORIYA","slug":"jharkhand_satbarwa_bakoriya","state":"JHARKHAND"},"JH-13-005-008":{"block":"Taljhari","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-13-005-008","name":"MASKALAIYA","slug":"jharkhand_taljhari_maskalaiya","state":"JHARKHAND"},"JH-01-020-001":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-001","name":"AMMA","slug":"jharkhand_torpa_amma","state":"JHARKHAND"},"JH-01-020-002":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-002","name":"BARKULI","slug":"jharkhand_torpa_barkuli","state":"JHARKHAND"},"JH-01-020-003":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-003","name":"DIYAKELA","slug":"jharkhand_torpa_diyakela","state":"JHARKHAND"},"JH-01-020-004":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-004","name":"DORMA","slug":"jharkhand_torpa_dorma","state":"JHARKHAND"},"JH-01-020-005":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-005","name":"FATKA","slug":"jharkhand_torpa_fatka","state":"JHARKHAND"},"JH-01-020-006":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-006","name":"HUSIR","slug":"jharkhand_torpa_husir","state":"JHARKHAND"},"JH-01-020-007":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-007","name":"JARIA","slug":"jharkhand_torpa_jaria","state":"JHARKHAND"},"JH-01-020-008":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-008","name":"KAMRA","slug":"jharkhand_torpa_kamra","state":"JHARKHAND"},"JH-01-020-009":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-009","name":"MARCHA","slug":"jharkhand_torpa_marcha","state":"JHARKHAND"},"JH-01-020-010":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-010","name":"OKRA","slug":"jharkhand_torpa_okra","state":"JHARKHAND"},"JH-01-020-011":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-011","name":"SUNDARI","slug":"jharkhand_torpa_sundari","state":"JHARKHAND"},"JH-01-020-012":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-012","name":"TAPKARA","slug":"jharkhand_torpa_tapkara","state":"JHARKHAND"},"JH-01-020-013":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-013","name":"TORPA EAST","slug":"jharkhand_torpa_torpa-east","state":"JHARKHAND"},"JH-01-020-014":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-014","name":"TORPA WEST","slug":"jharkhand_torpa_torpa-west","state":"JHARKHAND"},"JH-01-020-015":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-015","name":"UKRIMARI","slug":"jharkhand_torpa_ukrimari","state":"JHARKHAND"},"JH-01-020-016":{"block":"TORPA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"JH-01-020-016","name":"URIKELA","slug":"jharkhand_torpa_urikela","state":"JHARKHAND"},"KN-06-001-003":{"block":"AURAD","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"KN-06-001-003","name":"KAMALANAGAR","slug":"karnataka_aurad_kamalanagar","state":"KARNATAKA"},"KN-27-005-013":{"block":"KARWAR","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"KN-27-005-013","name":"CHENDIA","slug":"karnataka_karwar_chendia","state":"KARNATAKA"},"KL-04-003-009":{"block":"Koduvally","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"KL-04-003-009","name":"Thamarassery","slug":"kerala_koduvally_thamarassery","state":"KERALA"},"KL-14-004-002":{"block":"Nedumangad","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"KL-14-004-002","name":"Aruvikkara","slug":"kerala_nedumangad_aruvikkara","state":"KERALA"},"KL-14-009-001":{"block":"Vamanapuram","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"KL-14-009-001","name":"Kallara","slug":"kerala_vamanapuram_kallara","state":"KERALA"},"OR-05-005-026":{"block":"BHOGRAI","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"OR-05-005-026","name":"SULTANPUR","slug":"odisha_bhograi_sultanpur","state":"ODISHA"},"UP-43-006-037":{"block":"BHITAURA","code":"CodeFromDjango","district":"DistrictFromDjango","jobcardCode":"UP-43-006-037","name":"LAKANI","slug":"uttar-pradesh_bhitaura_lakani","state":"UTTAR PRADESH"}}

panchayats = {
    'jharkhand_cachar_torpa_sundari': {'slug': 'jharkhand_cachar_torpa_sundari', 'name': 'SUNDARI', 'id': 15764, 'state': 'JHARKHAND', 'district': 'CACHAR', 'code': '0423012003', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-011'},
    'jharkhand_dumka_mandro_bartalla': {'slug': 'jharkhand_dumka_mandro_bartalla', 'name': 'BARTALLA', 'id': 66089, 'state': 'JHARKHAND', 'district': 'DUMKA', 'code': '3411008004', 'block': 'Mandro', 'jobcardCode': 'JH-13-002-003'},
    'jharkhand_garhwa_bhandaria_madgari-k': {'slug': 'jharkhand_garhwa_bhandaria_madgari-k', 'name': 'MADGARI (K)', 'id': 66457, 'state': 'JHARKHAND', 'district': 'GARHWA', 'code': '3407009008', 'block': 'BHANDARIA', 'jobcardCode': 'JH-07-009-008'},
    'jharkhand_garhwa_garhwa_ursugi': {'slug': 'jharkhand_garhwa_garhwa_ursugi', 'name': 'URSUGI', 'id': 66523, 'state': 'JHARKHAND', 'district': 'GARHWA', 'code': '3407001025', 'block': 'GARHWA', 'jobcardCode': 'JH-07-001-025'},
    'jharkhand_garhwa_meral_hasandag': {'slug': 'jharkhand_garhwa_meral_hasandag', 'name': 'HASANDAG', 'id': 66570, 'state': 'JHARKHAND', 'district': 'GARHWA', 'code': '3407004009', 'block': 'MERAL', 'jobcardCode': 'JH-07-004-009'},
    'jharkhand_garhwa_meral_karkoma': {'slug': 'jharkhand_garhwa_meral_karkoma', 'name': 'KARKOMA', 'id': 66571, 'state': 'JHARKHAND', 'district': 'GARHWA', 'code': '3407004010', 'block': 'MERAL', 'jobcardCode': 'JH-07-004-010'},
    'jharkhand_garhwa_meral_sangwaria': {'slug': 'jharkhand_garhwa_meral_sangwaria', 'name': 'SANGWARIA', 'id': 66579, 'state': 'JHARKHAND', 'district': 'GARHWA', 'code': '3407004018', 'block': 'MERAL', 'jobcardCode': 'JH-07-004-018'},
    'jharkhand_garhwa_meral_tisar-tetuka': {'slug': 'jharkhand_garhwa_meral_tisar-tetuka', 'name': 'TISAR TETUKA', 'id': 66581, 'state': 'JHARKHAND', 'district': 'GARHWA', 'code': '3407004020', 'block': 'MERAL', 'jobcardCode': 'JH-07-004-020'},
    'jharkhand_garhwa_ramna_bulka': {'slug': 'jharkhand_garhwa_ramna_bulka', 'name': 'BULKA', 'id': 66604, 'state': 'JHARKHAND', 'district': 'GARHWA', 'code': '3407012006', 'block': 'RAMNA', 'jobcardCode': 'JH-07-012-006'},
    'jharkhand_garhwa_ranka_bishrampur': {'slug': 'jharkhand_garhwa_ranka_bishrampur', 'name': 'BISHRAMPUR', 'id': 66613, 'state': 'JHARKHAND', 'district': 'GARHWA', 'code': '3407005002', 'block': 'RANKA', 'jobcardCode': 'JH-07-005-002'},
    'jharkhand_gariyaband_bhandaria_karchali': {'slug': 'jharkhand_gariyaband_bhandaria_karchali', 'name': 'KARCHALI', 'id': 30321, 'state': 'JHARKHAND', 'district': 'GARIYABAND', 'code': '3316014073', 'block': 'BHANDARIA', 'jobcardCode': 'JH-07-009-006'},
    'jharkhand_jashpur_torpa_tapkara': {'slug': 'jharkhand_jashpur_torpa_tapkara', 'name': 'TAPKARA', 'id': 31681, 'state': 'JHARKHAND', 'district': 'JASHPUR', 'code': '3307014066', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-012'},
    'jharkhand_katihar_torpa_kamra': {'slug': 'jharkhand_katihar_torpa_kamra', 'name': 'KAMRA', 'id': 20917, 'state': 'JHARKHAND', 'district': 'KATIHAR', 'code': '0524005006', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-008'},
    'jharkhand_khunti_torpa_amma': {'slug': 'jharkhand_khunti_torpa_amma', 'name': 'AMMA', 'id': 67794, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020001', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-001'},
    'jharkhand_khunti_torpa_barkuli': {'slug': 'jharkhand_khunti_torpa_barkuli', 'name': 'BARKULI', 'id': 67795, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020002', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-002'},
    'jharkhand_khunti_torpa_diyakela': {'slug': 'jharkhand_khunti_torpa_diyakela', 'name': 'DIYAKELA', 'id': 67796, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020003', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-003'},
    'jharkhand_khunti_torpa_dorma': {'slug': 'jharkhand_khunti_torpa_dorma', 'name': 'DORMA', 'id': 67797, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020004', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-004'},
    'jharkhand_khunti_torpa_fatka': {'slug': 'jharkhand_khunti_torpa_fatka', 'name': 'FATKA', 'id': 67798, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020005', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-005'},
    'jharkhand_khunti_torpa_husir': {'slug': 'jharkhand_khunti_torpa_husir', 'name': 'HUSIR', 'id': 67799, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020006', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-006'},
    'jharkhand_khunti_torpa_jaria': {'slug': 'jharkhand_khunti_torpa_jaria', 'name': 'JARIA', 'id': 67748, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401008009', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-007'},
    'jharkhand_khunti_torpa_marcha': {'slug': 'jharkhand_khunti_torpa_marcha', 'name': 'MARCHA', 'id': 67802, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020009', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-009'},
    'jharkhand_khunti_torpa_okra': {'slug': 'jharkhand_khunti_torpa_okra', 'name': 'OKRA', 'id': 67803, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020010', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-010'},
    'jharkhand_khunti_torpa_torpa-east': {'slug': 'jharkhand_khunti_torpa_torpa-east', 'name': 'TORPA EAST', 'id': 67806, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020013', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-013'},
    'jharkhand_khunti_torpa_torpa-west': {'slug': 'jharkhand_khunti_torpa_torpa-west', 'name': 'TORPA WEST', 'id': 67807, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020014', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-014'},
    'jharkhand_khunti_torpa_ukrimari': {'slug': 'jharkhand_khunti_torpa_ukrimari', 'name': 'UKRIMARI', 'id': 67808, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020015', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-015'},
    'jharkhand_khunti_torpa_urikela': {'slug': 'jharkhand_khunti_torpa_urikela', 'name': 'URIKELA', 'id': 67809, 'state': 'JHARKHAND', 'district': 'KHUNTI', 'code': '3401020016', 'block': 'TORPA', 'jobcardCode': 'JH-01-020-016'},
    'jharkhand_latehar_mahuadanr_mahuadanr': {'slug': 'jharkhand_latehar_mahuadanr_mahuadanr', 'name': 'Mahuadanr', 'id': 68013, 'state': 'JHARKHAND', 'district': 'LATEHAR', 'code': '3406007006', 'block': 'Mahuadanr', 'jobcardCode': 'JH-06-007-006'},
    'jharkhand_palamu_chhatarpur_cherain': {'slug': 'jharkhand_palamu_chhatarpur_cherain', 'name': 'CHERAIN', 'id': 68267, 'state': 'JHARKHAND', 'district': 'PALAMU', 'code': '3405008016', 'block': 'CHHATARPUR', 'jobcardCode': 'JH-05-008-016'},
    'jharkhand_palamu_chhatarpur_hutukdag': {'slug': 'jharkhand_palamu_chhatarpur_hutukdag', 'name': 'HUTUKDAG', 'id': 68273, 'state': 'JHARKHAND', 'district': 'PALAMU', 'code': '3405008018', 'block': 'CHHATARPUR', 'jobcardCode': 'JH-05-008-018'},
    'jharkhand_palamu_satbarwa_bakoriya': {'slug': 'jharkhand_palamu_satbarwa_bakoriya', 'name': 'BAKORIYA', 'id': 68482, 'state': 'JHARKHAND', 'district': 'PALAMU', 'code': '3405003010', 'block': 'Satbarwa', 'jobcardCode': 'JH-05-003-010'},
    'jharkhand_pashchim champaran_hat-gamharia_dumria': {'slug': 'jharkhand_pashchim champaran_hat-gamharia_dumria', 'name': 'Dumria', 'id': 23165, 'state': 'JHARKHAND', 'district': 'PASHCHIM CHAMPARAN', 'code': '0512009008', 'block': 'Hat Gamharia', 'jobcardCode': 'JH-08-009-008'},
    'jharkhand_saharsa_ramna_gamharia': {'slug': 'jharkhand_saharsa_ramna_gamharia', 'name': 'GAMHARIA', 'id': 24632, 'state': 'JHARKHAND', 'district': 'SAHARSA', 'code': '0521013001', 'block': 'RAMNA', 'jobcardCode': 'JH-07-012-007'},
    'jharkhand_sahebganj_taljhari_maskalaiya': {'slug': 'jharkhand_sahebganj_taljhari_maskalaiya', 'name': 'MASKALAIYA', 'id': 69079, 'state': 'JHARKHAND', 'district': 'SAHEBGANJ', 'code': '3413005008', 'block': 'Taljhari', 'jobcardCode': 'JH-13-005-008'},
    'jharkhand_west singhbhum_jhinkpani_kudahatu': {'slug': 'jharkhand_west singhbhum_jhinkpani_kudahatu', 'name': 'Kudahatu', 'id': 69446, 'state': 'JHARKHAND', 'district': 'WEST SINGHBHUM', 'code': '3408003008', 'block': 'Jhinkpani', 'jobcardCode': 'JH-08-003-008'},
}


#############
# Functions
#############

# A way to collect the various panchayat details - extreme hacks to get going
def pts_collect(logger, db):
    cur = db.cursor()

    # # Update status of rejected and invalid payments
    # 
    # The update is done at the block level
    #
    # This is the substring in the jobcard that represents the block

    panchayatsForFB = {}
    for panchayat in panchayats:
        logger.info(panchayats[panchayat])
        state = panchayats[panchayat]['state']
        district = panchayats[panchayat]['district']  # Goli to Add from django
        block = panchayats[panchayat]['block']
        name = panchayats[panchayat]['name']
        slug = panchayats[panchayat]['slug']
        code = panchayats[panchayat]['code']
        jobcardCode = panchayats[panchayat]['jobcardCode']
        logger.info('District[%s], Name[%s], jobcardCode[%s], Code[%s], block[%s], state[%s], slug[%s]' % (district, name, jobcardCode, code, block, state, slug))
        panchayat_parts = panchayat.split('_')
        slug = panchayat_parts[2].replace('(', '').replace(')', '')
        # query = 'SELECT COUNT(DISTINCT (jobcard)) AS totalJobcards, COUNT(*) AS totalWorkers FROM libtech3.nrega_applicant WHERE panchayat_ = "%s"'
        query = 'select id, code from nrega_panchayat where slug="%s"' % (slug)
        logger.info('Executing query[%s]' % query)
        cur.execute(query)
        res = cur.fetchall()
        (id, code) = res[0]
        logger.info("%s %s" % (id, code))
        
        # query = 'select diName from highAccuracyPanchayats where panchayat_id="%s"' % id
        query = 'select d.name  from nrega_panchayat p, nrega_block b, nrega_district d where b.district_id = d.id and b.id = p.block_id and p.id="%s" limit 10' % id
        logger.info('Executing query[%s]' % query)
        cur.execute(query)
        res = cur.fetchall()
        district = res[0][0]
        logger.info(district)

        panchayat_slug =  panchayat_parts[0] + '_' + district.lower() + '_' + panchayat_parts[1] + '_' + slug
        logger.info('SLUG[%s]' % panchayat_slug)

        panchayatsForFB[panchayat_slug] = {'state': state, 'district': district, 'block': block, 'name': name, 'slug': panchayat_slug, 'code': code, 'jobcardCode': jobcardCode, 'id': id}

    for k, v in sorted(panchayatsForFB.items()):
        panchayatsForFB[k] = v
        print("'%s': %s," % (str(k), str(v)))

    return 'SUCCESS'

def ptsMeta_patch(logger, db):
    cur = db.cursor()

    for panchayat in panchayats:
        logger.info(panchayats[panchayat])
        state = panchayats[panchayat]['state']
        district = panchayats[panchayat]['district']  # Goli to Add from django
        block = panchayats[panchayat]['block']
        name = panchayats[panchayat]['name']
        slug = panchayats[panchayat]['slug']
        code = panchayats[panchayat]['code']
        jobcardCode = panchayats[panchayat]['jobcardCode']
        logger.info('District[%s], Name[%s], jobcardCode[%s], Code[%s], block[%s], state[%s], slug[%s]' % (district, name, jobcardCode, code, block, state, slug))
        panchayat_parts = panchayat.split('_')
        slug = panchayat_parts[2].replace('(', '').replace(')', '')

        query = 'SELECT COUNT(DISTINCT (jobcard)) AS totalJobcards, COUNT(*) AS totalWorkers FROM nrega_applicant WHERE panchayat_id = "%s"' % id
        logger.info('Executing query[%s]' % query)
        cur.execute(query)
        res = cur.fetchall()
        
        # query = 'SELECT COUNT(DISTINCT (jobcard)) AS totalJobcards, COUNT(*) AS totalWorkers FROM libtech3.nrega_applicant WHERE panchayat_ = "%s"'
        query = 'select id, code from nrega_panchayat where slug="%s"' % (slug)
        logger.info('Executing query[%s]' % query)
        cur.execute(query)
        res = cur.fetchall()
        (id, code) = res[0]
        logger.info("%s %s" % (id, code))


    return 'SUCCESS'
    

def panchayats_patch(logger, db):
    cur = db.cursor()

    # # Update status of rejected and invalid payments
    # 
    # The update is done at the block level
    #
    # This is the substring in the jobcard that represents the block

    if 0:
        for panchayat in panchayat_list:
            logger.info(panchayat)
            # (state, panchayatCode, panchayatName, block, panchayatKey) = panchayat.values()
            state = panchayat['state']
            # district = panchayat['district']  - Goli to Add from django
            block = panchayat['block']
            name = panchayat['panchayatName']
            slug = panchayat['panchayatKey']
            code = panchayat['panchayatCode']
            jobcardCode = panchayat['jobcardCode']
            logger.info('jobcardCode[%s] panchayatCode[%s] Key[%s] Name[%s] Block[%s] State[%s]' % (jobcardCode, panchayatCode, panchayatKey, panchayatName, block, state))

            query = 'Replace with Django API'
            logger.info('Executing query[%s]' % query)
            # cur.execute(query)
            # res = cur.fetchall()

            if slug in panchayats:
                pass
            else:
                panchayats[slug] = {'state': state, 'district': district, 'block': block, 'name': name, 'slug': slug, 'code': code, 'jobcardCode': jobcardCode}
    if 0:
        result = firebase.delete('https://libtech-app.firebaseio.com/panchayats/', None)
    else:
        result = firebase.patch('https://libtech-app.firebaseio.com/panchayats/', panchayats)
        logger.info(result)

    return 'SUCCESS'

# Patch the Firebase Database

def jobcards_patch(logger, db):
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
    # To Delete/Reset Uncoment the line below
    # result = firebase.delete('https://libtech-app.firebaseio.com/jcs/', None)
    # exit(0)

    for blString in block_strings:    
        # blString = 'JH-01-020'
        logger.info('Block String[%s]' % blString)

        if 0: #Mynk
            query = 'SELECT COUNT(DISTINCT (jobcard)) AS totalJobcards, COUNT(*) AS totalWorkers FROM nrega_applicant WHERE panchayat_id = "%s"' % (panchayat_id)
            logger.info('Executing query[%s]' % query)
            cur.execute(query)
            res = cur.fetchall()

        qRejInvPerJc = "SELECT zjobcard,SUBSTRING(zjobcard, 1, 13) AS ptString,SUBSTRING(zjobcard, 15, 3) AS vString,substring_index(zjobcard, '/', -1) as hString,round(sum(case WHEN musterStatus = 'Credited' then 1 else 0 END ), 0) as totCredited,round(sum(case WHEN musterStatus = '' then 1 else 0 END ), 0) as totPending,round(sum(case WHEN musterStatus = 'Rejected' then 1 else 0 END ), 0) as totRejected,round(sum(case WHEN musterStatus = 'Invalid Account' then 1 else 0 END ), 0) as totInvalid FROM libtech3.nrega_workdetail WHERE musterStatus = 'credited'AND musterStatus != '' AND SUBSTRING(zjobcard, 1, 9) = '{0}' GROUP BY zjobcard ORDER BY zjobcard".format(blString)
        logger.info('Executing query[%s]' % qRejInvPerJc)
        cur.execute(qRejInvPerJc)
        rejInvPerJc = cur.fetchall()

        for r in rejInvPerJc:
            jc = r[0]
            pt = r[1]
            vil = r[2]
            # print('HHD[%s]' % r[3])
            hhd = r[3]
            if '-' in hhd:
                hhd = hhd.split('-')
                hhd_slug = hhd[0].zfill(10) + '-' +  hhd[1]
            else:
                hhd_slug = hhd.zfill(10)

            jobcard = pt + '-' + vil
            jobcardSlug = pt + '-' + vil + '_' + hhd_slug
            
            if jobcard in geo:
                pass
            else:
                if pt in jobcard2panchayats:
                    geo[jobcard] = {'panchayatSlug': jobcard2panchayats[pt]['slug']}
                else:
                    geo[jobcard] = {}
                logger.info(geo[jobcard])

            geo[jobcard][jobcardSlug] = {'totCredited': str(r[4]), 'totPending': str(r[5]), 'totRejected': str(r[6]), 'totInvalid': str(r[7]), 'jobcardSlug': jobcardSlug, 'jobcard': jc}
            logger.info(geo[jobcard][jobcardSlug])

        result = firebase.patch('https://libtech-app.firebaseio.com/jcs/', geo)
    
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
            jc = n[3]
            pt = n[3][0:13]
            vil = n[3][14:17]
            hhd = n[3].split('/')[-1]
            logger.info('hhd[%s]' % hhd)

            if '-' in hhd:
                hhd = hhd.split('-')
                hhd_slug = hhd[0].zfill(10) + '-' +  hhd[1]
            else:
                hhd_slug = hhd.zfill(10)

            jobcard = pt + '-' + vil
            jobcardSlug = pt + '-' + vil + '_' + hhd_slug
            logger.info('geo[%s][%s] = ' % (jobcard, jobcardSlug)) # , str(geo[jobcard][jobcardSlug])))
            

            if 'applicants' in geo[jobcard][jobcardSlug]:
                logger.info('Passed with PRE value ' + str(geo[jobcard][jobcardSlug]['applicants']))
            else:
                geo[jobcard][jobcardSlug]['applicants'] = {}
            
            for a in applicantFields:
                if (n[i] != '') and (n[i] != '0'):
                    nDetails[a] = n[i]
                else:
                    pass
                i = i+1
                
            geo[jobcard][jobcardSlug]['applicants'][appNo] = nDetails
            logger.info('Applicant to be added to ' + str(geo[jobcard][jobcardSlug]['applicants']))

        result = firebase.patch('https://libtech-app.firebaseio.com/jcs/', geo)
        logger.info(result)

    return 'SUCCESS'



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

        if 0: #Mynk
            query = 'SELECT COUNT(DISTINCT (jobcard)) AS totalJobcards, COUNT(*) AS totalWorkers FROM nrega_applicant WHERE panchayat_id = "%s"' % (panchayat_id)
            logger.info('Executing query[%s]' % query)
            cur.execute(query)
            res = cur.fetchall()


        qRejInvPerJc = "SELECT zjobcard,SUBSTRING(zjobcard, 1, 13) AS ptString,SUBSTRING(zjobcard, 15, 3) AS vString,substring_index(zjobcard, '/', -1) as hString,round(sum(case WHEN musterStatus = 'Credited' then 1 else 0 END ), 0) as totCredited,round(sum(case WHEN musterStatus = '' then 1 else 0 END ), 0) as totPending,round(sum(case WHEN musterStatus = 'Rejected' then 1 else 0 END ), 0) as totRejected,round(sum(case WHEN musterStatus = 'Invalid Account' then 1 else 0 END ), 0) as totInvalid FROM libtech3.nrega_workdetail WHERE musterStatus = 'credited'AND musterStatus != '' AND SUBSTRING(zjobcard, 1, 9) = '{0}' GROUP BY zjobcard ORDER BY zjobcard".format(blString)
        logger.info('Executing query[%s]' % qRejInvPerJc)
        cur.execute(qRejInvPerJc)
        rejInvPerJc = cur.fetchall()

        for r in rejInvPerJc:
            jc = r[0]
            pt = r[1]
            if pt != 'JH-01-020-001':
                continue
            vil = r[2]
            hhd = r[3]
            
            if pt in geo:
                pass
            else:
                if pt in jobcard2panchayats:                    
                    geo[pt] = {'panchayatSlug': jobcard2panchayats[pt]['slug']}
                else:
                    geo[pt] = {}
                logger.info(geo[pt])
                
            if vil in geo[pt]:
                pass
            else:
                geo[pt][vil] = {}
                
            if hhd in geo[pt][vil]:
                pass
            else:
                geo[pt][vil][hhd] = {'totCredited': str(r[4]), 'totPending': str(r[5]), 'totRejected': str(r[6]), 'totInvalid': str(r[7]), 'jobcardSlug': jc}


        result = firebase.patch('https://libtech-app.firebaseio.com/geo/', geo)
    
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

        #get_ipython().run_cell_magic('timeit', '', "result = firebase.patch('https://libtech-app.firebaseio.com/geo/', geo)\nprint(len(result))")
        result = firebase.patch('https://libtech-app.firebaseio.com/geo/', geo)
        # result = firebase.get('geo/', None)
        logger.info(result)

        if 0: #Review
            result = firebase.post('https://libtech-app.firebaseio.com/tempNode/', {'panchayatName': 'tempPanchayat'})
            print(result)

    return 'SUCCESS'

#Review Awating Vivek's review
def delete_data():
    # # Deleting data
    # 
    # If I have to delete data from a node on, I can use the following.  In the example below, I delete the entire database.
    # 
    # result = firebase.delete('https://libtech-app.firebaseio.com', None)
    # print(result)

    # # Fire base data structure philosophy
    # 
    # Every time we access a node on firebase, we get all the data of all the children of that node.  This means that if our data is not flat (i.e. if there are a lot of children), we will get a lot of data.  For example, I originally structured the data as a geographic drilldown enging with jobcard numbers and transaction data.  Each time I tried to get a list of Panchayats, I also ended up getting the entire database downloaded.  This is costly. 
    # 
    # What I am going to do below is to generate a list of relatively small and flat nodes containing just the data I need for given views.  There will be duplication in presentation of data but retrieval would be a lot more efficient.
    # 
    # When I have data for a block or so, I will then go through the data through a set of queries to create various nodes and datapoints.

    if 0: #Review - where is queryNregaApplicant defined???
        logger.info('Executing query[%s]' % queryNregaApplicant)
        cur.execute(queryInvalidRejected)
        InvalidRejectedJcs = cur.fetchall()

        for i in InvalidRejectedJcs:
            print(i)
            panchayatName = i[0]
            jobcard = i[1]
            jobcard = jobcard.replace('/', '~')
            result = firebase.patch('https://libtech-app.firebaseio.com/%s/%s'%(panchayatName, jobcard), {'musterStatus': 'rejInv'})
            print(result)

#Review Goli says this query will not work in the new database. Do we still need it???        
def update_data():
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
            result = firebase.patch('https://libtech-app.firebaseio.com/%s/%s/%s/%s'%(panchayatName, jobcard, dateTo, newTransactionNo), {'jobcard': jobcard, 'name': name, 'musterNo': musterNo, 'workName': workName, 'totalWage': totalWage, 'wagelistNo': wagelistNo, 'ftoNo': ftoNo, 'musterStatus': musterStatus, 'bankNameOrPOName': bankNameOrPOName, 'dateTo': dateTo, 'firstSignatoryDate': firstSignatoryDate, 'secondSignatoryDate': secondSignatoryDate, 'transactionDate': transactionDate, 'bankProcessedDate': bankProcessedDate, 'paymentDate': paymentDate, 'creditedDate': creditedDate, 'ftoStatus': ftoStatus, 'rejectionReason': rejectionReason, 'maxDate': maxDate, 'maxDateColName': maxDateColName})
            print(result)


    
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
                    'https://libtech-app.firebaseio.com/', None)
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
        'https://libtech-app.firebaseio.com/', None)
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
        'https://libtech-app.firebaseio.com/', None)
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
    # result = pts_collect(self.logger, self.db)
    result = panchayats_patch(self.logger, self.db)
    # result = firebase_patch(self.logger, self.db)
    # result = jobcards_patch(self.logger, self.db)
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
