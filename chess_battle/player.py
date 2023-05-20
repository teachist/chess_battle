import functools
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

bp = Blueprint("player", __name__)


def settings_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if len(g.settings) == 0:
            return redirect(url_for('settings.add'))

        return view(**kwargs)

    return wrapped_view


@bp.route("/", methods=("GET",))
@settings_required
def rank():
    db = get_db()
    players = db.execute(
        "SELECT player.*, sum(score.score) as score\
        FROM player LEFT JOIN score\
        ON player.id=score.player_id\
        GROUP BY player.id\
        ORDER BY score DESC"
    )
    return render_template("player/rank.html", players=players)


@bp.route("/<int:player_id>/score-detail")
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


@bp.route("/add", methods=("GET", "POST"))
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
            except db.IntegrityError:
                message, category = f"User {name} is already registered.", 'danger'
        flash(message, category=category)

    return render_template("player/add.html")


@bp.route("/<int:id>/register-score", methods=("GET", "POST"))
def register_score(id):
    # Get Player name by id
    message, category = None, 'warning'
    db = get_db()
    player = db.execute("SELECT * FROM player where id=?", (id,)).fetchone()
    if player is None:
        message = f"Player is not fonud"
        return redirect("/")

    if request.method == "POST":
        player_id = id
        score = request.form["score"]
        round = g.settings["current_round"]
        print(player_id, score, round)

        # Check if the player already had a record for current round
        record_for_current_round = db.execute(
            'SELECT * FROM score WHERE player_id=? and round=?', (id, round,)).fetchone()
        if record_for_current_round is None and message is None:
            db.execute(
                "INSERT INTO score(player_id, score, round) VALUES(?,?,?)",
                (player_id, score, round),
            )
            db.commit()
            message, category = ('Record has been writen to DB', 'success')
            return redirect(url_for('player.battle_list', round=round))
        else:
            message = 'Record for current round has already set, do not submit repeatly'

        flash(message, category=category)
    return render_template("player/register_score.html", player=player)


def generate_battle_list(round):
    db = get_db()
    if round == 1:
        players = db.execute("SELECT * FROM player").fetchall()

        print(list(players[0]))
        for _ in range(len(players) // 2):
            player_a = random.choice(players)
            players.remove(player_a)
            player_b = random.choice(players)
            players.remove(player_b)

            db.execute(
                "INSERT INTO battlelist(round, player_a, player_b) VALUES(?,?,?)",
                (round, player_a["id"], player_b["id"]),
            )
            db.commit()
    else:
        players = db.execute(
            "SELECT player.*, sum(score.score) as score\
            FROM player LEFT JOIN score\
            ON player.id=score.player_id\
            GROUP BY player.id\
            ORDER BY score DESC"
        ).fetchall()
        print(players)
        for _ in range(len(players) // 2):
            db.execute(
                "INSERT INTO battlelist(round, player_a, player_b) VALUES(?,?,?)",
                (round, players[_ * 2]["id"], players[_ * 2 + 1]["id"]),
            )
            db.commit()


@bp.route("/battle-list/<int:round>", methods=("GET", "POST"))
def battle_list(round):
    battle_list = (
        get_db()
        .execute(
            "SELECT b.*, p1.name as name_a, s1.score as score_a, p2.name as name_b, s2.score as score_b\
            FROM battlelist b\
            LEFT JOIN player p1 ON b.player_a = p1.id\
            LEFT JOIN player p2 ON b.player_b = p2.id\
            LEFT JOIN score s1 ON b.player_a = s1.player_id and b.round=s1.round\
            LEFT JOIN score s2 ON b.player_b = s2.player_id and b.round=s2.round\
            WHERE b.round = ?",
            (round,),
        )
        .fetchall()
    )

    return render_template("player/battle_list.html", battle_list=battle_list)


@bp.before_app_request
def load_settings():
    message, catgory = None, 'error'
    try:
        temp_settings = get_db().execute("SELECT * FROM setting").fetchall()
        settings = {}
        if temp_settings is not None:
            for temp_setting in temp_settings:
                settings[temp_setting["name"]] = temp_setting["value"]
        g.settings = settings
    except:
        message = "No settings"
    print(g.settings)
    flash(message, category=catgory)
