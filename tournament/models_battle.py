from tournament import r


class Battle:
    def __init__(self, battle_id, tournament_id, round_id, player_a, player_b, winner, winner_mov):
        self.BattleId = int(battle_id),
        self.TournamentId = int(tournament_id),
        self.RoundId = int(round_id),
        self.PlayerA = player_a,
        self.PlayerB = player_b,
        self.Winner = winner,
        self.WinnerMOV = winner_mov

    @classmethod
    def get(cls, tournament_id, round_id, battle_id):
        tournament_id = int(tournament_id)
        round_id = int(round_id)
        battle_id = int(battle_id)
        return cls(tournament_id,
                   round_id,
                   battle_id,
                   player_a=r.hget(
                       'tournament:{}:round:{}:battle:{}'.format(tournament_id, round_id, battle_id),
                       'player_a'),
                   player_b=r.hget(
                       'tournament:{}:round:{}:battle:{}'.format(tournament_id, round_id, battle_id),
                       'player_b'),
                   winner=r.hget(
                       'tournament:{}:round:{}:battle:{}'.format(tournament_id, round_id, battle_id),
                       'winner'),
                   winner_mov=r.hget(
                       'tournament:{}:round:{}:battle:{}'.format(tournament_id, round_id, battle_id),
                       'winner_mov')
                   )

    @classmethod
    def create(cls, tournament_id, round_id, player_a, player_b, winner, winner_mov):
        battle = Battle(
            int(r.incr('tournament:{}:round:{}:next_battle_id'.format(tournament_id, round_id))),
            tournament_id,
            round_id,
            player_a,
            player_b,
            winner,
            winner_mov
        )
        r.hmset(
            'tournament:{}:round:{}:battle:{}'.format(battle.TournamentId, battle.RoundId, battle.BattleId),
            {
                'player_a': battle.PlayerA,
                'player_b': battle.PlayerB,
                'winner': battle.Winner,
                'winner_mov': battle.WinnerMOV
            }
        )
        r.sadd('tournament:{}:round:{}:battles'.format(battle.TournamentId, battle.RoundId), battle.BattleId)

    @classmethod
    def list_battles(cls, tournament_id, round_id):
        battles = []
        for i in range(1, Battle.count(tournament_id, round_id)):
            battles.append(Battle.get(tournament_id, round_id, i))
        return battles

    @classmethod
    def count(cls, tournament_id, round_id):
        return int('tournament:{}:round:{}:next_battle_id'.format(tournament_id, round_id)) - 1
