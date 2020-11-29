class UserInfo:
    def __init__(self, id = None, pw = None):
        self.id = id
        self.pw = pw
    
    def toJson(self):
        return '{"id":"%s", "pw":"%s"}' %(self.id, self.pw)