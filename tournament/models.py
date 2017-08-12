from tournament import app, flask_login, r

class User(flask_login.UserMixin):
    def __init__(self, id, email, nickname, hash):
        self.id = int(id)
        self.email = email.lower()
        self.nickname = nickname
        self.hash = hash

    @classmethod
    def get(cls, id):
        id = int(id)
        return cls(id, r.hget('user:%s' % id, 'email'), r.hget('user:%s' % id, 'nickname'), r.hget('user:%s' % id, 'hash'))
