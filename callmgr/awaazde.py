#===============================================================================
#    Copyright (c) 2014 Awaaz.De
#    Sample SDK to call awaaz.de xact api in python
#
#    @author Nikhil (nikhil@awaaz.de, nikhil.navadiya@gmail.com)
#
#===============================================================================


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
    print templateMgr.upload_file(template_id, file_url, is_url=True)
                
    template = templateMgr.getTemplate(template_id)

    print template
    template_data = {'text': template['text'], 'vocabulary': template['vocabulary'], 'language': template['language']}
    print template['vocabulary']

    filename = file.strip('.wav')  # Strip any other kind of format it might have
    if filename not in template_data['vocabulary']:
        template_data['vocabulary'].append(filename)
        print template_data
        print templateMgr.update(template_id, template_data)
        

def main():
    authdata= AuthData(USERNAME,PASSWORD,WS_URL)    
    templateMgr = TemplateMgr(authdata)
    callMgr = CallMgr(authdata);
    phone='9845155447'
    phone='9845065241'
    #data  = {"recipient":"9845065241", "text":"welcome have you picked rashan for september If you did not get rashan for september press one repeat have you picked rashan for september If you did not get rashan for september press one"}

    template_id = '25'
    template = templateMgr.getTemplate(template_id)

#    print template
#    template_data = {'text': template['text'], 'vocabulary': [], 'language': template['language']}
    template_data = {'text': template['text'], 'vocabulary': template['vocabulary'], 'language': template['language']}
    print template['vocabulary']

    #Logic to upload the wave_file for the first time -
    wave_file = '1004_anupds.wav'    # This should be done only once for each new file
    filename = wave_file.strip('.wav')
    if filename not in template_data['vocabulary']:
        template_data['vocabulary'].append(filename)
    print template_data

#    print templateMgr.update(template_id, template_data)

    exit(0)
    
    data  = {"recipient":"9845155447", 'text':'1004_anupds'}
    data['recipient']=phone
#    data['text']=callparams
    calltime=datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S")#Schedule the call for now
#    data['send_on']=calltime
    calldata=callMgr.create(data)
    print calldata
    print "Call ID is "+str(calldata['id'])
    vendorcallid=calldata['id']
    print vendorcallid

 
if __name__ =='__main__':main()
