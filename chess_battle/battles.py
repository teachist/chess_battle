from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    send_file,
    current_app,
)

from chess_battle.db import get_db
from chess_battle.settings import settings_required
import random
import csv
import os

bp = Blueprint("battle", __name__)


@bp.route('/battle-list/<int:round>/export', methods=("POST", "GET"))
def csv_export_battlelist(round=1):
    battle_list = (
        get_db()
        .execute(
            "SELECT p1.name as name_a, p1.org as org_a, s1.score, p2.name as name_b, p2.org as org_b, s2.score\
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
    filename = os.path.join(current_app.instance_path,
                            'battlelist_round_{}.csv'.format(round))
    with open(filename, 'w', encoding='gbk') as fh:
        csvwriter = csv.writer(fh)
        csvwriter.writerow(['象棋比赛第{}轮对阵情况表'.format(round)])
        csvwriter.writerow(['先手', '来自单位', '本局得分', '后手', '来自单位', '本局得分'])
        csvwriter.writerows(battle_list)
    flash(f'对阵表：第{round}轮导出成功！', category='success')
    return send_file(filename, mimetype='text/csv',  download_name=os.path.basename(filename), as_attachment=True)


@bp.route("/export", methods=("POST", "GET"))
def summary_export():
    db = get_db()
    players = db.execute(
        "SELECT player.name, player.gender, player.org, player.phone, sum(score.score) as score\
        FROM player LEFT JOIN score\
        ON player.id=score.player_id\
        GROUP BY player.id\
        ORDER BY score DESC"
    ).fetchall()

    filename = os.path.join(current_app.instance_path, 'player_export.csv')
    with open(filename, 'w', encoding='gbk') as fh:
        csvwriter = csv.writer(fh)
        csvwriter.writerow(['姓名', '性别', '单位', '电话', '累计得分'])
        csvwriter.writerows(players)
    flash(f'当前选手数据导出成功！', category='success')
    return send_file(filename, mimetype='text/csv',  download_name=os.path.basename(filename), as_attachment=True)


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

    lucky_players = db.execute(
        'SELECT player_id, round FROM score WHERE notes=?', ('轮空', )).fetchall()

    lucky_players_id = {}
    for lucky_player in lucky_players:
        lucky_players_id[lucky_player['player_id']] = lucky_player['round']

    return render_template("battle/rank.html", players=players, lucky_players=lucky_players_id)


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
        score = int(request.form["score"])
        against_score = 2 - score  # against player score
        round = g.settings["current_round"]
        print(player_id, score, round)

        # Check if the player already had a record for current round
        record_for_current_round = db.execute(
            'SELECT * FROM score WHERE player_id=? and round=?', (id, round,)).fetchone()
        if record_for_current_round is None and message is None:
            db.execute(
                "INSERT INTO score(player_id, round, score, against_score) VALUES(?,?,?,?)",
                (player_id, round, score, against_score),
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
            "SELECT b.*, p1.name as name_a, p1.org as org_a, s1.score as score_a, p2.name as name_b, p2.org as org_b, s2.score as score_b\
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


@bp.route("/battle-list/<int:round>/automation", methods=("GET", "POST"))
def automation_for_score_register(round):
    db = get_db()
    round = g.settings['current_round']
    player_groups = db.execute(
        'SELECT player_a, player_b FROM battlelist WHERE round=?', (round, ))

    for player_group in player_groups:
        random_score = random.randint(0, 2)
        against_socre = 2 - random_score

        db.execute(
            "INSERT INTO score(player_id, round, score, against_score) VALUES(?,?,?,?)",
            (player_group['player_a'], round, random_score, against_socre),
        )
        db.execute(
            "INSERT INTO score(player_id, round, score, against_score) VALUES(?,?,?,?)",
            (player_group['player_b'], round, against_socre, random_score),
        )
        db.commit()
    return redirect('/')
