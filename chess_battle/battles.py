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
from chess_battle.settings import settings_required
import random

bp = Blueprint("battle", __name__)


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
    return render_template("battle/rank.html", players=players)


@ bp.route("/<int:id>/register-score", methods=("GET", "POST"))
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
            return redirect(url_for('battle.battle_list', round=round))
        else:
            message = 'Record for current round has already set, do not submit repeatly'

        flash(message, category=category)
    return render_template("battle/register_score.html", player=player)


@ bp.route("/battle-list/<int:round>", methods=("GET", "POST"))
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

    return render_template("battle/battle_list.html", battle_list=battle_list)
