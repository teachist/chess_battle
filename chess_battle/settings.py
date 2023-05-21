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
                message, category = f'Add setting:{setting_name} to database.', 'success'
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
            message = 'There are still have battle in working. You can not update CURRENT ROUND!'
            flash(message, category)
            return redirect(url_for('player.battle_list',
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
            return redirect(url_for("player.battle_list", round=int(setting_value)))

        flash(message, category=category)
        return redirect(url_for("settings.index"))

    return render_template("settings/index.html")


@ bp.before_app_request
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


def settings_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if len(g.settings) == 0:
            return redirect(url_for('settings.add'))

        return view(**kwargs)

    return wrapped_view
