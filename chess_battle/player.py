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


@bp.route("/update", methods=("POST",))
def update():
    if request.method == 'POST':
        player_id = int(request.form['id'].strip())
        player = Player.query.filter_by(id=player_id).first()
        if player is None:
            message, category = 'Player not found!', 'warning'
            flash(message, category=category)
            return redirect(url_for('player.list'))
        else:
            try:
                player.name = request.form["name"].strip()
                player.gender = request.form["gender"].strip()
                player.org = request.form["org"].strip()
                player.phone = request.form["phone"].strip()
                player.is_active = True if int(
                    request.form['status']) == 0 else False

                db.session.commit()
                flash(f'{player.name} Update successful.', 'success')
                return redirect(url_for('player.list'))
            except db.IntegrityError:
                flash('Very bad happend!', 'danger')
    return render_template("player/index.html")


@bp.route('/<int:player_id>/delete', methods=('GET', 'POST'))
def delete(player_id):
    if request.method == 'POST':
        message, category = None, 'warning'
        try:
            player = Player.query.filter_by(id=player_id).one()
            if player:
                db.session.delete(player)
                db.session.commit()
                message, category = f"{player.name} is successfully deleted!", 'success'
                flash(message, category=category)
            else:
                message, category = f"Delete fail!", 'danger'
                flash(message, category=category)
        except:
            message, category = f"Delete fail!", 'danger'
            flash(message, category=category)

            redirect(url_for('player.list'))


@ bp.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "POST":
        name = request.form["name"].strip()
        gender = request.form["gender"].strip()
        org = request.form["org"].strip()
        phone = request.form["phone"].strip()
        status = True if int(request.form["status"].strip()) == 0 else False
        message, category = None, 'warning'

        print(request.form)

        if not name:
            message = "Name is required."
        if not org:
            message = 'Your orgnization is required.'
        if not phone or len(phone) != 11:
            message = 'Phone number is required or length not equal to 11!'

        may_exist = Player.query.filter_by(
            name=name, org=org, gender=gender, phone=phone).first()

        if message is None and not may_exist:
            try:
                print(name, gender, org, phone, status)
                player = Player(name=name, gender=gender,
                                org=org, phone=phone, is_active=status)
                db.session.add(player)
                db.session.commit()

                message, category = f"{name} is successfully submit to DB.", 'success'
                flash(message, category=category)
                return redirect(url_for('player.list'))
            except db.IntegrityError:
                message, category = f"User {name} may be already registered.", 'danger'
        flash(message, category=category)

    return render_template("player/index.html")
