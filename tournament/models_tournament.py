import datetime
from math import inf

from tournament.models_player import Player
from tournament import r


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
        r.sadd('tournament:{}:players'.format(self.TournamentId), player.PlayerId)
        if player.Group:
            r.sadd('tournament:{}:player_groups'.format(self.TournamentId), player.Group)
            r.sadd('tournament:{}:player_group:{}'.format(self.TournamentId, player.Group), player.PlayerId)

    def remove_player(self, player_id):
        player_id = int(player_id)
        player = Player.get(player_id)
        r.srem('tournament:{}:players'.format(self.TournamentId), player.PlayerId)
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
        players['Independent'.encode('utf-8')] = []
        for player_id in player_ids:
            player_id = int(player_id)
            players['Independent'.encode('utf-8')].append(Player.get(player_id))
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
