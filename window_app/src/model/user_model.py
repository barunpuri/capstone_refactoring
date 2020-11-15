class UserInfo:
    def __init__(self):
        self.id = None
        self.pw = None
    
    def toJson(self):
        return '{"id":"%s", "pw":"%s"}' %(self.id, self.pw)