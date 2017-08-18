from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from tournament import app, flask_login
from tournament.forms import CreateTournament, CreatePlayer, AddPlayer
from tournament.models_player import Player
from tournament.models_tournament import Tournament


@app.route('/tournaments')
def tournament_list():
    my_list = []
    if flask_login.current_user.is_authenticated:
        all_list = Tournament.get_all(except_admin_id=flask_login.current_user.UserId)
        my_list = Tournament.get_for_user(flask_login.current_user.UserId)
    else:
        all_list = Tournament.get_all()
    return render_template('tournaments.html', all_tournaments=all_list, my_tournaments=my_list)


@app.route('/tournament', methods=['GET', 'POST'])
@login_required
def create_tournament():
    tournament_form = CreateTournament(request.form)
    if tournament_form.validate_on_submit():
        new_tournament = Tournament.create(tournament_form.name.data,
                                           tournament_form.location.data,
                                           flask_login.current_user.UserId,
                                           tournament_form.date.data)
        flash('New Tournament Created')
        return redirect(url_for('tournament_detail', tournament_id=new_tournament.TournamentId))
    return render_template('tournament.html', t_form=tournament_form)


@app.route('/tournament/<tournament_id>', methods=['GET', 'POST'])
def tournament_detail(tournament_id=None):
    if tournament_id:
        tournament = Tournament.get(int(tournament_id))
        group_players = tournament.dict_players_by_group()
        return render_template('tournament.html',
                               user=flask_login.current_user,
                               tournament=tournament,
                               group_players=group_players)
    return redirect(url_for('create_tournament'))


@app.route('/tournament/<tournament_id>/players', methods=['GET', 'POST'])
@login_required
def tournament_players(tournament_id=None):
    if tournament_id:
        tournament = Tournament.get(int(tournament_id))
        create_form = CreatePlayer(request.form)
        if create_form.validate_on_submit():
            new_player = Player.create(create_form.name.data, create_form.faction.data, create_form.group.data)
            flash('{} Created'.format(new_player.Name))
            tournament.add_player(new_player.PlayerId)
            flash('{} Added'.format(new_player.Name))
            return redirect(url_for('tournament_detail', tournament_id=tournament.TournamentId))

        add_form = AddPlayer(request.form)
        add_form.player.choices = [
            (
                p.PlayerId,
                '{} ({}), {}'.format(
                    p.Name.decode('utf-8'),
                    p.Group.decode('utf-8'),
                    p.Faction.decode('utf-8')
                )
            ) for p in Player.list_players(tournament.TournamentId)
        ]
        if add_form.is_submitted():
            tournament.add_player(int(add_form.player.data))
            flash('{} Added'.format(dict(add_form.player.choices).get(int(add_form.player.data))))
            return redirect(url_for('tournament_players', tournament_id=tournament.TournamentId))

        return render_template('tournament_players.html',
                               tournament=tournament,
                               create_form=create_form,
                               add_form=add_form)
    return redirect(url_for('create_tournament'))

@app.route('/tournament/<tournament_id>/remove_player/<player_id>', methods=['GET', 'POST'])
@login_required
def remove_player(tournament_id=None, player_id=None):
    if tournament_id and player_id:
        tournament = Tournament.get(int(tournament_id))
        player = Player.get(int(player_id))
        if tournament and player:
            tournament.remove_player(player_id)
            flash('Removed {}'.format(player.Name))
    return redirect(url_for('tournament_detail', tournament_id=tournament_id))
