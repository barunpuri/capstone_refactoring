from user_model import UserInfo

class LoginInfo(UserInfo):
    def __init__(self):
        super().__init__()
        self.did = None
        self.mac = None

    def toJson(self):
        return '{"id":"%s", "pw":"%s", "did":"%s", "mac":"%s"}' %(self.id, self.pw, self.did, self.mac)