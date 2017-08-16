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
        tournament=Tournament.get(int(tournament_id))
        create_form = CreatePlayer(request.form)
        if create_form.validate_on_submit():
            new_player = Player.create(create_form.name.data, create_form.faction.data, create_form.group.data)
            flash('{} Created'.format(new_player.Name))
            tournament.add_player(new_player.PlayerId)
            flash('{} Added'.format(new_player.Name))
            return redirect(url_for('tournament_detail', tournament_id=tournament_id))

        add_form = AddPlayer(request.form)
        players = tournament.list_players()
        add_form.player.choices = [('{}'.format(p.PlayerId), p.Name.decode('utf-8')) for p in Player.list_players(tournament.TournamentId)]
        return render_template('tournament.html', tournament=tournament, c_form=create_form, a_form=add_form, tournament_players=players)
    return redirect(url_for('create_tournament'))
