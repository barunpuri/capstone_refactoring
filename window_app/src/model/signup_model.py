from user_model import UserInfo

class SignupInfo(UserInfo):
    def __init__(self, id = None, pw = None, name = None, email = None):
        super().__init__(id, pw)
        self.name = name
        self.email = email

    def toJson(self):
        return '{"id":"%s", "pw":"%s", "name":"%s", "email":"%s"}' %(self.id, self.pw, self.name, self.email)