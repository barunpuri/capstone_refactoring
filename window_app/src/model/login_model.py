from user_model import UserInfo

class LoginInfo(UserInfo):
    def __init__(self, id = None, pw = None, did = None, mac = None):
        super().__init__(id, pw)
        self.did = did
        self.mac = mac

    def toJson(self):
        return '{"id":"%s", "pw":"%s", "did":"%s", "mac":"%s"}' %(self.id, self.pw, self.did, self.mac)