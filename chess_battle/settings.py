from datetime import datetime
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
from chess_battle.database import db, Player, BattleList, Score, Settings
from sqlalchemy import func
from sqlalchemy import union


bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/", methods=("GET", "POST"))
def index():
    return render_template("settings/index.html")


@bp.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "POST":
        message, category = None, 'warning'
        setting_name = request.form["setting_name"].strip()
        setting_value = request.form["setting_value"].strip()

        if setting_name != "" and setting_value != "":
            try:
                new_setting = Settings(name=setting_name, value=setting_value)
                db.session.add(new_setting)
                db.session.commit()
                message, category = f'Add Setting: [{setting_name}] to database.', 'success'
                if category == 'success' and setting_name == 'current_round' and setting_value == '1':
                    from chess_battle.battles import generate_battle_list
                    generate_battle_list(int(setting_value))
                    return redirect(url_for("battle.battle_list", round=int(setting_value)))
            except db.IntegrityError:
                message = f"{setting_name} is already existed"
        else:
            message, category = "Cannot post empty entries", 'danger'
        flash(message, category=category)
        return redirect(url_for('settings.index'))

    return render_template("settings/index.html")


def get_player_number():
    return len(Player.query.all())


def get_score_register_number_by_round(round):
    return len(Score.query.filter_by(round=round).all())


@bp.route("/update", methods=("GET", "POST"))
def update():
    if request.method == "POST":
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

                current_setting_obj = Settings.query.filter_by(
                    name=setting_name).one()
                current_setting_obj.value = setting_value

                db.session.commit()
                message, category = 'Update setting successful.', 'success'
            except db.IntegrityError:
                message = f"{setting_name} is not existed"
        else:
            message, category = "Cannot post empty entries or duplicate entry", 'danger'

        # generate battle list when updae round setting
        if setting_name == "current_round" and category == 'success':
            from chess_battle.battles import generate_battle_list
            generate_battle_list(int(setting_value))
            flash(message, category=category)
            return redirect(url_for("battle.battle_list", round=int(setting_value)))

        flash(message, category=category)
        return redirect(url_for("settings.index"))

    return render_template("settings/index.html")


@ bp.before_app_request
def load_settings():
    message, catgory = None, 'error'
    temp_settings = Settings.query.all()
    print(temp_settings)
    settings = {}
    if temp_settings is not None:
        for temp_setting in temp_settings:
            print(temp_setting)
            settings[temp_setting.name] = temp_setting.value
    g.settings = settings

    print(g.settings)
    flash(message, category=catgory)


def settings_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if len(g.settings) == 0:
            flash(
                'You must initialize the project by adding a Setting named:[current_round] firstly.', 'warning')
            return redirect(url_for('settings.add'))
        return view(**kwargs)

    return wrapped_view
