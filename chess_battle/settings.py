from chess_battle.db import get_db
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

from .player import generate_battle_list

bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "POST":
        db = get_db()
        error = None
        setting_name = request.form["setting_name"].strip()
        setting_value = request.form["setting_value"].strip()

        if setting_name != "" and setting_value != "":
            try:
                db.execute(
                    "INSERT INTO setting(name, value) VALUES(?,?)",
                    (setting_name, setting_value),
                )
                db.commit()
            except db.IntegrityError:
                error = f"{setting_name} is already existed"
        else:
            error = "Cannot post empty entries"
        flash(error)

    return render_template("player/add_setting.html")


@bp.route("/update", methods=("GET", "POST"))
def update():
    if request.method == "POST":
        db = get_db()
        error = None
        setting_name = request.form["setting_name"].strip()
        setting_value = request.form["setting_value"].strip()

        if (
            setting_name != ""
            and setting_value != ""
            and g.settings[setting_name] != setting_value
        ):
            try:
                db.execute(
                    "UPDATE setting SET value=? WHERE name = ?",
                    (setting_value, setting_name),
                )
                db.commit()
            except db.IntegrityError:
                error = f"{setting_name} is not existed"
        else:
            error = "Cannot post empty entries or duplicate entry"

        # generate battle list when updae round setting
        if setting_name == "current_round" and error is None:
            generate_battle_list(int(setting_value))
            return redirect(url_for("player.battle_list", round=int(setting_value)))

        flash(error)

    return render_template("player/update_setting.html")
