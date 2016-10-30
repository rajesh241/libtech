
#===============================================================================
#    Copyright (c) 2014 Awaaz.De
#    Sample SDK to call awaaz.de xact api in python
#
#    @author Nikhil (nikhil@awaaz.de, nikhil.navadiya@gmail.com)
#
#===============================================================================

import time

from xactclient.data.datamgr import TemplateMgr
from xactclient.data.datamgr import CallMgr
from xactclient.common.authdata import AuthData

USERNAME = 'vibhore'
PASSWORD = 'vibhore123'
WS_URL = 'https://awaaz.de/console/xact'
#Our Vendor ID for AwazDe System
vid=1


def awaazdeUpload(file):
    authdata= AuthData(USERNAME,PASSWORD,WS_URL)    
    templateMgr = TemplateMgr(authdata)
    callMgr = CallMgr(authdata);

    template_id = '25' # Hard coded for Template that plays any file by filename match
    
    #Logic to upload the wave_file for the first time -
    file_url = 'http://libtech.info/audio/' + file
                
    template = templateMgr.getTemplate(template_id)

    # print("Template [%s]" % template)
    template_data = {'text': template['text'], 'vocabulary': template['vocabulary'], 'language': template['language']}
    print("Vocabulary %s" % template['vocabulary'])

    filename = file.strip('.wav')  # Strip any other kind of format it might have
    if filename not in template_data['vocabulary']:
        print templateMgr.upload_file(template_id, file_url, is_url=True)
        template_data['vocabulary'].append(filename)
        print template_data
        print templateMgr.update(template_id, template_data)
    else:
        print("File already present [%s]" % file)

    return template

def awaazdeStatusCheck(cur_callid=None):
    authdata= AuthData(USERNAME,PASSWORD,WS_URL)    
    templateMgr = TemplateMgr(authdata)
    callMgr = CallMgr(authdata);

    if not cur_callid:
        vendorcallid='57896'
        return None
    else:
        vendorcallid=cur_callid

    print("Printing details for Call[%s]" % vendorcallid)
    call_details = callMgr.getCall(str(vendorcallid))

    print call_details
    
    status = call_details['status']
    duration = status['duration']
    print duration

    attempts = status['attempts']
    print attempts
    
    sent_on = status['sent_on']
    print sent_on
    
    print status['response']

    # url = call_details['url']
    # print "DeliveryStatus[%s]" % url

    text = call_details['text']
    print text
    
    print call_details['backup_calls']
    print call_details['send_on']
    
    recipient = call_details['recipient']
    print recipient
    
    callsid = call_details['id']
    print callsid
    
    return duration, attempts, sent_on, text, recipient, callsid #, url
    

def awaazdePlaceCall(phone, wave_file=None, calltime=None):
    authdata= AuthData(USERNAME,PASSWORD,WS_URL)    
    templateMgr = TemplateMgr(authdata)
    callMgr = CallMgr(authdata);

    #Logic to upload the wave_file for the first time -
    if not wave_file:
        wave_file = '1308_Rayapuramcampaignbhaskar.wav' # '1431_CgbcstChakeri010316.wav'    # This should be done only once for each new file
    print("WaveFile[%s]" % wave_file)
    filename = wave_file.strip('.wav')
    
    data  = {'recipient': phone, 'text':filename, 'backup_calls':0}  # , 'send_on': calltime}
#    calltime=datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S")#Schedule the call for now

    calldata=callMgr.create(data)
    print calldata
    vendorcallid=calldata['id']

    return vendorcallid


def main():

    phone='9845155447'

    #Logic to upload the wave_file for the first time -
    wave_file = '1459_Venky18MAR2016MittadodiPanchayat.wav' # '1431_CgbcstChakeri010316.wav'    # This should be done only once for each new file
    filename = wave_file.strip('.wav')

    if wave_file:
        print awaazdeUpload(wave_file)

    if False:
        vendorcallid = awaazdePlaceCall(phone, wave_file)
        time.sleep(10)
    else:
        vendorcallid = '71489' # '70239' # '70221' # '57897'
    print("Call ID [%s]" % vendorcallid)

#    callreturn = awaazdeStatusCheck('70217')
    callreturn = awaazdeStatusCheck(vendorcallid)
    print callreturn

 
if __name__ =='__main__':main()
