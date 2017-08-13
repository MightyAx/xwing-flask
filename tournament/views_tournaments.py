from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from tournament import app, flask_login
from tournament.forms import CreateTournament
from tournament.models import Tournament


@app.route('/tournaments')
def tournament_list():
    my_list = []
    if flask_login.current_user.is_authenticated:
        all_list = Tournament.get_all(except_id=flask_login.current_user.UserId)
        my_list = Tournament.get_for_user(flask_login.current_user.UserId)
    else:
        all_list = Tournament.get_all()
    return render_template('tournaments.html', all_tournaments=all_list, my_tournaments=my_list)


@app.route('/tournament', methods=['GET', 'POST'])
@login_required
def create_tournament():
    form = CreateTournament(request.form)
    if form.validate_on_submit():
        new_tournament = Tournament.create(form.name.data,
                                           form.location.data,
                                           flask_login.current_user.UserId,
                                           form.date.data)
        flash('New Tournament Created')
        return redirect(url_for('tournament_detail', tournament_id=new_tournament.TournamentId))
    return render_template('tournament.html', form=form)


@app.route('/tournament/<tournament_id>')
def tournament_detail(tournament_id=None):
    if tournament_id:
        return render_template('tournament.html', tournament=Tournament.get(int(tournament_id)))
    return redirect(url_for('create_tournament'))
