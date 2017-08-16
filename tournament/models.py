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


class Tournament:
    def __init__(self, tournament_id, name, location, admin_id, date):
        self.TournamentId = int(tournament_id)
        self.Name = name
        self.Location = location
        self.AdminId = int(admin_id)
        self.Date = date

    def add_player(self, player_id):
        player_id = int(player_id)
        player = Player.get(player_id)
        r.zadd('tournament:{}:players'.format(self.TournamentId), player.PlayerId, 0)
        if player.Group:
            r.sadd('tournament:{}:player_groups'.format(self.TournamentId), player.Group)
            r.sadd('tournament:{}:player_group:{}'.format(self.TournamentId, player.Group), player.PlayerId)

    def remove_player(self, player_id):
        player_id = int(player_id)
        player = Player.get(player_id)
        r.zrem('tournament:{}:players'.format(self.TournamentId), player.PlayerId)
        if player.Group:
            r.srem('tournament:{}:player_groups'.format(self.TournamentId), player.Group)
            r.srem('tournament:{}:player_group:{}'.format(self.TournamentId, player.Group), player.PlayerId)

    def list_players(self, group=None):
        players = []
        if group:
            player_ids = r.smembers('tournament:{}:player_group:{}'.format(self.TournamentId, group))
        else:
            player_ids = r.smembers('tournament:{}:players'.format(self.TournamentId))
        for player_id in player_ids:
            player_id = int(player_id)
            players.append(Player.get(player_id))
        return players

    def list_groups(self):
        return r.smembers('tournament:{}:player_groups'.format(self.TournamentId))

    def dict_players_by_group(self):
        players = {}
        groups = r.smembers('tournament:{}:player_groups'.format(self.TournamentId))
        group_keys = ['tournament:{}:players'.format(self.TournamentId)]
        for group in groups:
            group_keys.append('tournament:{}:player_group:{}'.format(self.TournamentId, group))
            players[group] = self.list_players(group)
        player_ids = r.sdiff(group_keys)
        players['independent'] = []
        for player_id in player_ids:
            player_id = int(player_id)
            players['independent'].append(Player.get(player_id))
        return players

    @classmethod
    def get(cls, tournament_id):
        tournament_id = int(tournament_id)
        return cls(tournament_id,
                   name=r.hget('tournament:{}'.format(tournament_id), 'name'),
                   location=r.hget('tournament:{}'.format(tournament_id), 'location'),
                   admin_id=r.hget('tournament:{}'.format(tournament_id), 'admin_id'),
                   date=r.hget('tournament:{}'.format(tournament_id), 'date')
                   )

    @classmethod
    def create(cls, name, location, admin_id, date):
        tournament = Tournament(int(r.incr('next_tournament_id')), name, location, admin_id, date)
        r.hmset('tournament:{}'.format(tournament.TournamentId),
                {
                    'name': tournament.Name,
                    'location': tournament.Location,
                    'admin_id': tournament.AdminId,
                    'date': tournament.Date
                })
        score = date - datetime.date(2017, 1, 1)
        r.zadd('tournaments', tournament.TournamentId, score.days)
        r.zadd('user:{}:tournaments'.format(tournament.AdminId), tournament.TournamentId, score.days)
        return tournament

    @classmethod
    def get_all(cls, except_admin_id=None):
        score = datetime.date.today() - datetime.timedelta(days=30) - datetime.date(2017, 1, 1)
        min_score = score.days
        max_score = inf
        tournaments = []
        for tournament_id in r.zrangebyscore('tournaments', min_score, max_score):
            potential = Tournament.get(tournament_id)
            if not except_admin_id or except_admin_id != potential.AdminId:
                tournaments.append(potential)
        return tournaments

    @classmethod
    def get_for_user(cls, admin_id):
        score = datetime.date.today() - datetime.timedelta(days=30) - datetime.date(2017, 1, 1)
        min_score = score.days
        max_score = inf
        tournaments = []
        for tournament_id in r.zrangebyscore('user:{}:tournaments'.format(admin_id), min_score, max_score):
            tournaments.append(Tournament.get(tournament_id))
        return tournaments


class Player:
    def __init__(self, player_id, name, faction, group):
        self.PlayerId = int(player_id)
        self.Name = name
        self.Faction = faction
        self.Group = group

    @classmethod
    def get(cls, player_id):
        player_id = int(player_id)
        return cls(player_id,
                   name=r.hget('player:{}'.format(player_id), 'name'),
                   faction=r.hget('player:{}'.format(player_id), 'faction'),
                   group=r.hget('player:{}'.format(player_id), 'group')
                   )

    @classmethod
    def create(cls, name, faction, group):
        player = Player(int(r.incr('next_player_id')), name, faction, group)
        r.hmset('player:{}'.format(player.PlayerId),
                {
                    'name': player.Name,
                    'faction': player.Faction,
                    'group': player.Group
                })
        r.sadd('players', player.PlayerId)
        return player

    @classmethod
    def list_players(cls, except_tournament_id=None):
        players = []
        if except_tournament_id:
            players_ids = r.sdiff('players', 'tournament:{}:players'.format(except_tournament_id))
        else:
            players_ids = r.smembers('players')
        for player_id in players_ids:
            players.append(Player.get(player_id))
        return players
