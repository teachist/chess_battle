from .database import Player, Score
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)

# from chess_battle.db import get_db
from chess_battle.database import db
import random

bp = Blueprint("player", __name__, url_prefix='/player')


@bp.route("/", methods=("GET", "POST"))
def list():
    players = Player.query.all()
    # print(request.args)
    return render_template("player/index.html", players=players)


@bp.route("/<int:player_id>/update", methods=("GET", "POST"))
def update(player_id):
    if request.method == 'POST':
        player = Player.query.filter_by(id=player_id).first()
        if player is None:
            message, category = 'User not found', 'warning'
            flash(message, category=category)
            return redirect(url_for('player.list'))
        else:
            try:
                player.name = request.form["name"]
                player.gender = request.form["gender"]
                player.org = request.form["org"]
                player.phone = request.form["phone"]
                player.showable = request.form['showable']

                db.session.commit()
                flash(f'{player.name} Update successful.', 'success')
                return redirect(url_for('player.list'))
            except db.IntegrityError:
                flash('Very bad happend!', 'danger')
    return render_template("player/index.html")


@bp.route('/<int:player_id>/delete', methods=('GET', 'POST'))
def delete(player_id):
    pass


def read_player_from_csv(filename):
    import csv
    with open(filename, encoding='gbk', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            name, gender, org, phone = row['name'].strip(
            ), row['gender'].strip(), row['org'].strip(), row['phone'].strip()
            # db.execute("INSERT INTO player (name, gender, org, phone) VALUES (?, ?, ?, ?)",
            #            (name, gender, org, phone,))
            # db.commit()
            player = Player(name=name, gender=gender, org=org, phone=phone)
            db.session.add(player)
            db.session.commit()


@bp.route("/add_players", methods=('GET', 'POST'))
def add_players():
    read_player_from_csv(current_app.config['PRE_DEFINED_DATA'])
    flash(f'Add players successful.', 'success')
    return redirect(url_for('player.list'))


@ bp.route("/<int:player_id>/score-detail")
def score_detail(player_id):
    message, category = None, 'warning'
    player = Player.query.filter_by(id=player_id).first()
    if player is None:
        message = 'Player not existed'
        return redirect('/')

    score_detail = Score.query.filter_by(player.id).all()
    flash(message, category=category)
    return render_template("player/score_detail.html", player=player, score_detail=score_detail)


@ bp.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "POST":
        name = request.form["name"].strip()
        gender = request.form["gender"].strip()
        org = request.form["org"].strip()
        phone = request.form["phone"].strip()
        message, category = None, 'warning'

        if not name:
            message = "Name is required."
        if not org:
            message = 'Your orgnization is required.'
        if not phone or len(phone) != 11:
            message = 'Phone number is required or length not equal to 11!'

        if message is None:
            try:
                player = Player(name=name, gender=gender, org=org, phone=phone)
                db.session.add(player)
                db.session.commit()
                message, category = f"{name} is successfully submit to DB.", 'success'
                flash(message, category=category)
                return redirect(url_for('player.list'))
            except db.IntegrityError:
                message, category = f"User {name} is already registered.", 'danger'
        flash(message, category=category)

    return render_template("player/index.html")
