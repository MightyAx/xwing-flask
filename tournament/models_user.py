import flask_login
from passlib.handlers.pbkdf2 import pbkdf2_sha256

from tournament import r


class User(flask_login.UserMixin):
    def __init__(self, user_id, email, nickname, pw_hash):
        self.UserId = int(user_id)
        self.Email = email.lower()
        self.Nickname = nickname
        self.Hash = pw_hash

    def get_id(self):
        return self.UserId

    @classmethod
    def get(cls, user_id):
        user_id = int(user_id)
        return cls(user_id,
                   email=r.hget('user:{}'.format(user_id), 'email'),
                   nickname=r.hget('user:{}'.format(user_id), 'nickname'),
                   pw_hash=r.hget('user:{}'.format(user_id), 'hash')
                   )

    @classmethod
    def exists(cls, email):
        return r.zscore('users', email.lower())

    @classmethod
    def create(cls, email, nickname, password):
        pw_hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)

        user = User(int(r.incr('next_user_id')), email.lower(), nickname, pw_hash)
        r.hmset('user:{}'.format(user.UserId), {'email': user.Email, 'nickname': user.Nickname, 'hash': user.Hash})
        r.zadd('users', user.Email, user.UserId)
        return user
