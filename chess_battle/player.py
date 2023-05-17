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


@bp.route("/", methods=("GET",))
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


@bp.route("/add", methods=("GET", "POST"))
def add_player():
    if request.method == "POST":
        username = request.form["username"]
        school = request.form["school"]
        age = request.form["age"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO player(username, school, age) VALUES (?, ?, ?)",
                    (username, school, age),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # return redirect(url_for("index"))
                return redirect("/")
        flash(error)

    return render_template("player/add.html")


@bp.route("/<int:id>/register-score", methods=("GET", "POST"))
def register_score(id):
    # Get Player name by id
    error = None
    db = get_db()
    player = db.execute("SELECT * FROM player where id=?", (id,)).fetchone()
    if player is None:
        error = f"Player is not fonud"
        return redirect("/")

    if request.method == "POST":
        player_id = id
        score = request.form["score"]
        round = g.settings["current_round"]

        db.execute(
            "INSERT INTO score(player_id, score, round) VALUES(?,?,?)",
            (player_id, score, round),
        )
        db.commit()
        return redirect("/")
        flash(error)
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


@bp.route("/battle-list", methods=("GET", "POST"))
def battle_list():
    current_round = int(g.settings["current_round"])
    battle_list = (
        get_db()
        .execute("SELECT * FROM battlelist WHERE round=?", (current_round,))
        .fetchall()
    )
    if current_round == 1 and battle_list == []:
        generate_battle_list(current_round)

    if request.method == "POST":
        round = request.form["round"]
        battle_list = (
            get_db()
            .execute("SELECT * FROM battlelist WHERE round=?", (round,))
            .fetchall()
        )
    return render_template("player/battle_list.html", battle_list=battle_list)


@bp.before_app_request
def load_settings():
    error = None
    try:
        temp_settings = get_db().execute("SELECT * FROM setting").fetchall()
        settings = {}
        if temp_settings is not None:
            for temp_setting in temp_settings:
                settings[temp_setting["name"]] = temp_setting["value"]
        g.settings = settings
    except:
        error = "No settings"
    print(g.settings)
    flash(error)
