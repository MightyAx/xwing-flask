from passlib.handlers.pbkdf2 import pbkdf2_sha256

from tournament import flask_login, r


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
                   r.hget('user:%s' % user_id, 'email'),
                   r.hget('user:%s' % user_id, 'nickname'),
                   r.hget('user:%s' % user_id, 'hash')
                   )

    @classmethod
    def exists(cls, email):
        return r.zscore('users', email.lower())

    @classmethod
    def create(cls, email, nickname, password):
        user_id = int(r.incr('next_user_id'))
        pw_hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)

        user = User(user_id, email.lower(), nickname, pw_hash)
        r.hmset('user:%s' % user.UserId, {'email': user.Email, 'nickname': user.Nickname, 'hash': user.Hash})
        r.zadd('users', user.Email, user.UserId)
        return user
