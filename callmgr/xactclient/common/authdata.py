#===============================================================================
#    Copyright (c) 2014 Awaaz.De
#    Authentication Data container
#
#    @author Nikhil (nikhil@awaaz.de, nikhil.navadiya@gmail.com)
#
#===============================================================================


class AuthData:
    '''
    defining constructor
    '''
    def __init__(self, uname, password, baseurl):
        self.username = uname
        self.password = password
        self.baseurl = baseurl
    
    '''
    methods
    '''
    def getUsername(self):
        return self.username
    
    def getPassword(self):
        return self.password
    
    def getUrl(self):
        return self.baseurl
    