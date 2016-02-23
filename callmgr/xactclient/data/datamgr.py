#===============================================================================
#    Copyright (c) 2014 Awaaz.De
#    This file is part of awaaz.de xact api client lib
#
#    @author Nikhil (nikhil@awaaz.de, nikhil.navadiya@gmail.com)
#
#===============================================================================
import requests
import simplejson as json

TEMPLATE_WS_URL = '/templates'
CALL_WS_URL = '/calls'
FILE_WS_URL = '/files'

class TemplateMgr:
    '''
    Template Manager is responsible for dealing with template data
    '''
    def __init__(self, authdata):
        self.authdata = authdata
    
    '''
    returns all templates
    '''
    def getAll(self):
        response = requests.get(self.authdata.getUrl() + TEMPLATE_WS_URL, auth=(self.authdata.getUsername(), self.authdata.getPassword()))
        if response.status_code == 200:
            templates_data = []
            for template in response.json()['results']:
                templates_data.append(template)
            
            return templates_data
        else:
            return response.text
    
    '''
    returns template detail for given template id
    '''
    def getTemplate(self, id):
        response = requests.get(self.authdata.getUrl() + TEMPLATE_WS_URL + '/' + id, auth=(self.authdata.getUsername(), self.authdata.getPassword()))
        if response.status_code == 200:
            template = None
            if response.json():
                template = response.json()
                
            return template
        else:
            return response.text


    '''
    creating new temnplate
    '''
    def create(self, templatedata):
        headers = {'content-type': 'application/json'}
        response = requests.post(self.authdata.getUrl() + TEMPLATE_WS_URL + "/", data=json.dumps(templatedata), headers=headers, auth=(self.authdata.getUsername(), self.authdata.getPassword()))
        if response.status_code == 201:
            template = None
            if response.json():
                template = response.json()
            return template
        else:
            return response.text


    '''
    editing template
    '''
    def update(self, id, templatedata):
        headers = {'content-type': 'application/json'}
        response = requests.put(self.authdata.getUrl() + TEMPLATE_WS_URL + '/' + str(id) + '/', data=json.dumps(templatedata), headers=headers, auth=(self.authdata.getUsername(), self.authdata.getPassword()))
        if response.status_code == 201:
            template = None
            if response.json():
                template = response.json()

            return template
        else:
            return response.text


    '''
    deleting template
    '''
    def delete(self, id):
        headers = {'content-type': 'application/json'}
        response = requests.delete(self.authdata.getUrl() + TEMPLATE_WS_URL + '/' + str(id) + '/', headers=headers, auth=(self.authdata.getUsername(), self.authdata.getPassword()))
        if response.status_code == 204:
            return "true"
        else:
            return response.text

    '''
    Upload template file
    '''
    def upload_file(self, id, file, is_url=False):
        #headers = {'content-type': 'application/x-www-urlformencoded'}
        data = {'template_pk': id}
        files = {}
        if is_url is False:
             files = {'file': open(file, 'rb')}
        else:
            data['file_url'] = file
            
        url = self.authdata.getUrl() + TEMPLATE_WS_URL + '/' + str(id) + FILE_WS_URL + "/"
        
        response = requests.post(url, data=data, files=files, auth=(self.authdata.getUsername(), self.authdata.getPassword()))
        if response.status_code == 201:
            if response.json():
                return response.json()
            return None
        else:
            return response.text

class CallMgr:
    '''
    Call Manager is responsible for dealing with call data
    '''
    def __init__(self, authdata):
        self.authdata = authdata
    
    '''
    returns all calls
    '''
    def getAll(self):
        response = requests.get(self.authdata.getUrl() + CALL_WS_URL, auth=(self.authdata.getUsername(), self.authdata.getPassword()))
        if response.status_code == 200:
            calls_data = []
            for call in response.json()['results']:
                calls_data.append(call)
            
            return calls_data
        else:
            return response.text
    
    '''
    returns call detail for given call id
    '''
    def getCall(self, id):
        response = requests.get(self.authdata.getUrl() + CALL_WS_URL + '/' + id, auth=(self.authdata.getUsername(), self.authdata.getPassword()))
        if response.status_code == 200:
            call = None
            if response.json():
                call = response.json()
                
            return call
        else:
            return response.text
        
    
    '''
    creating new call
    '''
    def create(self, calldata):
        headers = {'content-type': 'application/json'}
        response = requests.post(self.authdata.getUrl() + CALL_WS_URL + "/", data=json.dumps(calldata), headers=headers, auth=(self.authdata.getUsername(), self.authdata.getPassword()))
        if response.status_code == 201:
            call = None
            if response.json():
                call = response.json()
                
            return call
        else:
            return response.text
        
    
    '''
    editing call
    '''
    def update(self, id, calldata):
        headers = {'content-type': 'application/json'}
        response = requests.put(self.authdata.getUrl() + CALL_WS_URL + '/' + id, data=json.dumps(calldata), headers=headers, auth=(self.authdata.getUsername(), self.authdata.getPassword()))
        if response.status_code == 201:
            call = None
            if response.json():
                call = response.json()
                
            return call
        else:
            return response.text
        
        
    '''
    deleting call
    '''
    def delete(self, id):
        headers = {'content-type': 'application/json'}
        response = requests.delete(self.authdata.getUrl() + CALL_WS_URL + '/' + id, headers=headers, auth=(self.authdata.getUsername(), self.authdata.getPassword()))
        if response.status_code == 204:
            return "true"
        else:
            return response.text
        