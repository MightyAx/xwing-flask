from tournament import r


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