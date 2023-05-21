from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from chess_battle.db import get_db
import random

bp = Blueprint("player", __name__, url_prefix='/player')


@bp.route("/", methods=("GET", "POST"))
def list():
    db = get_db()
    players = db.execute("SELECT * FROM player")
    print(request.args)
    return render_template("player/index.html", players=players)


@bp.route("/update", methods=("GET", "POST"))
def update():
    if request.method == 'POST':
        db = get_db()
        player_id = request.form['id']
        player = db.execute("SELECT * FROM player WHERE id=?",
                            (player_id, )).fetchone()
        if player is None:
            message, category = 'User not found', 'warning'
            flash(message, category=category)
            return redirect(url_for('player.list'))
        try:
            name = request.form["name"]
            id_card = request.form["id_card"]
            project = request.form["project"]
            phone = request.form["phone"]
            db.execute(
                'UPDATE player SET name=?, id_card=?, project=?, phone=? WHERE id=?', (name, id_card, project, phone, player_id,))
            db.commit()
            flash(f'{name} Update successful.', 'success')
            return redirect(url_for('player.list'))
        except db.IntegrityError:
            flash('Very bad happend!', 'danger')
    return render_template("player/index.html")


@bp.route('/<int:player_id>/delete', methods=('GET', 'POST'))
def delete(player_id):
    pass


def read_player_from_csv(filename):
    import csv
    with open(filename, newline='') as csvfile:
        db = get_db()
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            name, id_card, project, phone = row['name'], row['id_card'], row['project'], row['phone']
            db.execute("INSERT INTO player (name, id_card, project, phone) VALUES (?, ?, ?, ?)",
                       (name, id_card, project, phone,))
            db.commit()


@ bp.route("/<int:player_id>/score-detail")
def score_detail(player_id):
    message, category = None, 'warning'
    db = get_db()
    player = db.execute(
        'SELECT name FROM player WHERE id = ?', (player_id,)).fetchone()
    if player is None:
        message = 'Player not existed'
        return redirect('/')
    score_detail = db.execute(
        'SELECT * FROM score WHERE player_id=? ORDER BY created', (player_id,)).fetchall()
    flash(message, category=category)
    return render_template("player/score_detail.html", player=player, score_detail=score_detail)


@ bp.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "POST":
        name = request.form["name"]
        id_card = request.form["id_card"]
        project = request.form["project"]
        phone = request.form["phone"]
        db = get_db()
        message, category = None, 'warning'

        if not name:
            message = "Name is required."
        if not id_card:
            message = 'ID card is required.'
        if not project:
            message = 'Project is required.'
        if not phone:
            message = 'Phone number is required.'

        if message is None:
            try:
                db.execute(
                    "INSERT INTO player(name, id_card, project, phone) VALUES (?, ?, ?, ?)",
                    (name, id_card, project, phone,),
                )
                db.commit()
                message, category = f"{name} is successfully submit to DB.", 'success'
                flash(message, category=category)
                return redirect(url_for('player.list'))
            except db.IntegrityError:
                message, category = f"User {name} is already registered.", 'danger'
        flash(message, category=category)

    return render_template("player/index.html")
