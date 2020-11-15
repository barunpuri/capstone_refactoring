from user_model import UserInfo

class SignupInfo(UserInfo):
    def __init__(self):
        super().__init__()
        self.name = None
        self.email = None

    def toJson(self):
        return '{"id":"%s", "pw":"%s", "name":"%s", "email":"%s"}' %(self.id, self.pw, self.name, self.email)