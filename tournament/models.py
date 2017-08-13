from math import inf

from passlib.handlers.pbkdf2 import pbkdf2_sha256
import datetime

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
        pw_hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)

        user = User(int(r.incr('next_user_id')), email.lower(), nickname, pw_hash)
        r.hmset('user:%s' % user.UserId, {'email': user.Email, 'nickname': user.Nickname, 'hash': user.Hash})
        r.zadd('users', user.Email, user.UserId)
        return user


class Tournament:
    def __init__(self, tournament_id, name, location, admin_id, date):
        self.TournamentId = int(tournament_id)
        self.Name = name
        self.Location = location
        self.AdminId = int(admin_id)
        self.Date = date

    @classmethod
    def get(cls, tournament_id):
        tournament_id = int(tournament_id)
        return cls(tournament_id,
                   r.hget('tournament:%s' % tournament_id, 'name'),
                   r.hget('tournament:%s' % tournament_id, 'location'),
                   r.hget('tournament:%s' % tournament_id, 'admin_id'),
                   r.hget('tournament:%s' % tournament_id, 'date')
                   )

    @classmethod
    def create(cls, name, location, admin_id, date):
        tournament = Tournament(int(r.incr('next_tournament_id')), name, location, admin_id, date)
        r.hmset('tournament:%s' % tournament.TournamentId,
                {
                    'name': tournament.Name,
                    'location': tournament.Location,
                    'admin_id': tournament.AdminId,
                    'date': tournament.Date
                })
        score = date - datetime.date(2017, 1, 1)
        r.zadd('tournaments', tournament.TournamentId, score.days)
        r.zadd('user:%s:tournaments' % tournament.AdminId, tournament.TournamentId, score.days)
        return tournament

    @classmethod
    def get_all(cls, except_id=None):
        score = datetime.date.today() - datetime.timedelta(days=30) - datetime.date(2017, 1, 1)
        min_score = score.days
        max_score = inf
        tournaments = []
        for tournament_id in r.zrangebyscore('tournaments', min_score, max_score):
            potential = Tournament.get(tournament_id)
            if not except_id or except_id != potential.AdminId:
                tournaments.append(potential)
        return tournaments

    @classmethod
    def get_for_user(cls, admin_id):
        score = datetime.date.today() - datetime.timedelta(days=30) - datetime.date(2017, 1, 1)
        min_score = score.days
        max_score = inf
        tournaments = []
        for tournament_id in r.zrangebyscore('user:%s:tournaments' % admin_id, min_score, max_score):
            tournaments.append(Tournament.get(tournament_id))
        return tournaments
