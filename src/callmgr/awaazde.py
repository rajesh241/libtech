
#===============================================================================
#    Copyright (c) 2014 Awaaz.De
#    Sample SDK to call awaaz.de xact api in python
#
#    @author Nikhil (nikhil@awaaz.de, nikhil.navadiya@gmail.com)
#
#===============================================================================

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

import time

from wrappers.logger import loggerFetch

from xactclient.data.datamgr import TemplateMgr
from xactclient.data.datamgr import CallMgr
from xactclient.common.authdata import AuthData

USERNAME = 'vibhore'
PASSWORD = 'vibhore123'
WS_URL = 'https://awaaz.de/console/xact'
#Our Vendor ID for AwazDe System
vid=1


def awaazdeUpload(logger, file):
    authdata= AuthData(USERNAME,PASSWORD,WS_URL)    
    templateMgr = TemplateMgr(authdata)
    callMgr = CallMgr(authdata);

    template_id = '25' # Hard coded for Template that plays any file by filename match
    
    #Logic to upload the wave_file for the first time -
    file_url = 'http://libtech.info/audio/' + file
                
    template = templateMgr.getTemplate(template_id)

    # logger.info("Template [%s]" % template)
    template_data = {'text': template['text'], 'vocabulary': template['vocabulary'], 'language': template['language']}
    #logger.info("Vocabulary %s" % template['vocabulary'])

    filename = file.strip('.wav')  # Strip any other kind of format it might have
    logger.info('FileName[%s]' % filename)
    if filename not in template_data['vocabulary']:
        logger.info(templateMgr.upload_file(template_id, file_url, is_url=True))
        template_data['vocabulary'].append(filename)
        #logger.info(template_data)
        logger.info(templateMgr.update(template_id, template_data))
    else:
        logger.info("File already present [%s]" % file)

    return template

def awaazdeStatusCheck(logger, cur_callid=None):
    authdata= AuthData(USERNAME,PASSWORD,WS_URL)    
    templateMgr = TemplateMgr(authdata)
    callMgr = CallMgr(authdata);

    if not cur_callid:
        vendorcallid='57896'
        return None
    else:
        vendorcallid=cur_callid

    logger.info("CallDetails[%s]" % vendorcallid)
    call_details = callMgr.getCall(str(vendorcallid))

    logger.info('Call Details[%s]' % call_details)
    
    status = call_details['status']
    duration = status['duration']
    attempts = status['attempts']
    sent_on = status['sent_on']
    text = call_details['text']
    recipient = call_details['recipient']
    callsid = call_details['id']
    
    return duration, attempts, sent_on, text, recipient, callsid #, url
    

def awaazdePlaceCall(logger, phone, wave_file=None, calltime=None):
    authdata= AuthData(USERNAME,PASSWORD,WS_URL)    
    templateMgr = TemplateMgr(authdata)
    callMgr = CallMgr(authdata);

    #Logic to upload the wave_file for the first time -
    if not wave_file:
        wave_file = '1629_RSCD281016.wav' # '1308_Rayapuramcampaignbhaskar.wav' #     # This should be done only once for each new file
    logger.info("WaveFile[%s]" % wave_file)
    filename = wave_file.strip('.wav')
    
    data  = {'recipient': phone, 'text':filename, 'backup_calls':0}  # , 'send_on': calltime}
#    calltime=datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S")#Schedule the call for now

    calldata=callMgr.create(data)
    logger.info("CallData[%s]" % calldata)
    vendorcallid=calldata['id']

    return vendorcallid


def main():

    logger = loggerFetch("info")
    logger.info("BEGIN PROCESSING...")

    phone='9845155447'

    #Logic to upload the wave_file for the first time -
    wave_file = '1629_RSCD281016.wav' # '1431_CgbcstChakeri010316.wav'    # This should be done only once for each new file
    filename = wave_file.strip('.wav')

    if wave_file:
        logger.info(awaazdeUpload(logger, wave_file))

    if False:
        vendorcallid = awaazdePlaceCall(logger, phone, wave_file)
        time.sleep(10)
    else:
        vendorcallid = '71503' # '70239' # '70221' # '57897'
    logger.info("Call ID [%s]" % vendorcallid)

    callreturn = awaazdeStatusCheck(logger, vendorcallid)
    logger.info(callreturn)

    logger.info("...END PROCESSING")     

 
if __name__ =='__main__':main()
