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

import functools
import random
from chess_battle.db import get_db


bp = Blueprint("settings", __name__, url_prefix="/settings")


def get_player_number():
    return get_db().execute('SELECT COUNT(*) as player_number FROM player').fetchone()['player_number']


def get_score_register_number_by_round(round):
    return get_db().execute('SELECT COUNT(*) as score_register_number FROM score WHERE round=?', (round,)).fetchone()['score_register_number']


def generate_battle_list(round):
    db = get_db()
    if round == 1:
        players = db.execute("SELECT * FROM player").fetchall()

        print(list(players[0]))
        # Randomly distributing players into groups
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
        # Starting from the second round, the following requirements must be met:
        # 1. The higer score should be front
        # 2. If the socre they have is the same, looking against score
        # 3. If the player have been battled with the current select player, skip it and choose another one
        
        ## Get players by their total score the got now
        players = db.execute(
            "SELECT player.*, sum(score.score) as score, sum(score.against_score) as against_score\
            FROM player LEFT JOIN score\
            ON player.id=score.player_id\
            GROUP BY player.id\
            ORDER BY score DESC, against_score DESC"
        ).fetchall()

        player_count = len(players)
        
        for _ in range( player_count // 2):
            # Choose 2 players in each loop
            current_player_b_pointer = 1
            player_a = players[0]
            player_b = players[current_player_b_pointer]
            # Get player's history battle lists
            history_battle_list = db.execute('SELECT player_b FROM battlelist WHERE player_id=?',( player_a['id'], )).fetchall()

            if  player_b['id'] not in history_battle_list:
                db.execute(
                    "INSERT INTO battlelist(round, player_a, player_b) VALUES(?,?,?)",
                    (round, player_a['id'], player_b['id']),
                )
                db.commit()
                players.remove( player_a )
                players.remove( player_b )
            else: # check by the against score
                db.execute('SELECT * FROM SCORE')



@bp.route("/", methods=("GET", "POST"))
def index():
    return render_template("settings/index.html")


@bp.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "POST":
        db = get_db()
        message, category = None, 'warning'
        setting_name = request.form["setting_name"].strip()
        setting_value = request.form["setting_value"].strip()

        if setting_name != "" and setting_value != "":
            try:
                db.execute(
                    "INSERT INTO setting(name, value) VALUES(?,?)",
                    (setting_name, setting_value),
                )
                db.commit()
                message, category = f'Add Setting: [{setting_name}] to database.', 'success'
                if category=='success' and setting_name == 'current_round' and int(setting_value) == 1:
                    generate_battle_list(int(setting_value))
                return redirect(url_for("battle.battle_list", round=int(setting_value)))
            except db.IntegrityError:
                message = f"{setting_name} is already existed"
        else:
            message, category = "Cannot post empty entries", 'danger'
        flash(message, category=category)
        return redirect(url_for('settings.index'))

    return render_template("settings/index.html")


@bp.route("/update", methods=("GET", "POST"))
def update():
    if request.method == "POST":
        db = get_db()
        message, category = None, 'warning'
        setting_name = request.form["setting_name"].strip()
        setting_value = request.form["setting_value"].strip()

        if setting_name == "current_round" and get_player_number() > get_score_register_number_by_round(g.settings['current_round']):
            message = '还有选手正在比赛，不能更新当前局次！'
            flash(message, category)
            return redirect(url_for('battle.battle_list',
                                    round=g.settings['current_round']))

        if (
            setting_name != ""
            and setting_value != ""
            and g.settings[setting_name] != setting_value
            and message is None
        ):
            try:
                db.execute(
                    "UPDATE setting SET value=? WHERE name = ?",
                    (setting_value, setting_name),
                )
                db.commit()
                message, category = 'Update setting successful.', 'success'
            except db.IntegrityError:
                message = f"{setting_name} is not existed"
        else:
            message, category = "Cannot post empty entries or duplicate entry", 'danger'

        # generate battle list when updae round setting
        if setting_name == "current_round" and category == 'success':
            generate_battle_list(int(setting_value))
            flash(message, category=category)
            return redirect(url_for("battle.battle_list", round=int(setting_value)))

        flash(message, category=category)
        return redirect(url_for("settings.index"))

    return render_template("settings/index.html")


@ bp.before_app_request
def load_settings():
    message, catgory = None, 'error'
    temp_settings = get_db().execute("SELECT * FROM setting").fetchall()
    settings = {}
    if temp_settings is not None:
        for temp_setting in temp_settings:
            settings[temp_setting["name"]] = temp_setting["value"]
    g.settings = settings

    print('anything')
    print(g.settings)
    flash(message, category=catgory)


def settings_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if len(g.settings) == 0:
            flash('You must initialize the project by adding a Setting named:[current_round] firstly.', 'warning')
            return redirect(url_for('settings.add'))
        return view(**kwargs)

    return wrapped_view
