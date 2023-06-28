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
import random
from chess_battle.database import db, Player, Battlelist, Score, Settings
from sqlalchemy import func
from sqlalchemy import union


bp = Blueprint("settings", __name__, url_prefix="/settings")


def get_player_number():
    return len(Player.query.all())


def get_score_register_number_by_round(round):
    return len(Score.query.filter_by(round=round).all())


def generate_battle_list(round):
    if round == 1:
        players = Player.query.all()

        print(players)
        # Randomly distributing players into groups
        for _ in range(len(players) // 2):
            player_a = random.choice(players)
            players.remove(player_a)
            player_b = random.choice(players)
            players.remove(player_b)

            bl = Battlelist(round=round, player_a=player_a.id,
                            player_b=player_b.id)
            db.session.add(bl)
            db.session.commit()

        # Check if the total playes is an odd number
        if players:
            player_score = Score(
                player_id=players[0]['id'], round=round, score=2, against_score=0, notes='轮空')
            db.session.add(player_score)
            db.session.commit()
    else:
        # Starting from the second round, the following requirements must be met:
        # 1. The higer score should be front
        # 2. If the socre they have is the same, looking against score
        # 3. If the player have been battled with the current select player, skip it and choose another one
        # 4. Same org should not be battled with, with randomize it should work fine
        # 5. Consider the player could not show up, and choose a lucky player
        # TODO 6. player A and player B should show up exchangable

        # ============= SOLVED PROBLEM 1 AND 2
        # Get players by their total score order from higer to lower
        # if it is them same score re-order by their against score
        # players = db.session.execute(
        #     "SELECT player.*, sum(score.score) as score, sum(score.against_score) as against_score\
        #     FROM player LEFT JOIN score\
        #     ON player.id=score.player_id\
        #     GROUP BY player.id\
        #     ORDER BY score DESC, against_score DESC"
        # ).all()

        players = db.session.query(Player, func.sum(Score.score), func.sum(Score.against_score))\
            .join(Score, Player.id == Score.player_id)\
            .group_by(Player.id)\
            .order_by(func.sum(Score.score).desc())\
            .order_by(func.sum(Score.against_score).desc())\
            .all()

        player_count = len(players)

        # ============= SOLVED PROBLEM 5
        # Check if the total playes is an odd number
        # randomly choose a player as lucky player and add +2 points to it
        # This lucky player can only choosed once
        if player_count % 2 == 1:
            lucky_players = Score.query.filter_by(notes='轮空').all()
            lucky_players_idx = []
            for _ in lucky_players:
                lucky_players_idx.append(_[0])

            print(lucky_players_idx)
            lucky_player = random.choice(players)
            while (lucky_player[0] in lucky_players_idx):
                lucky_player = random.choice(players)

            luky_player_in_current_round = Score(
                player_id=lucky_player[0], round=round, score=2, against_score=0, notes='轮空')
            db.session.add(luky_player_in_current_round)

            db.session.commit()

            players.remove(lucky_player)

        # ============= SOLVED PROBLEM 3 AND 4
        for _ in range(player_count // 2):
            # Choose 2 players in each loop
            current_player_b_pointer = 1
            player_a = players[0]
            player_b = players[current_player_b_pointer]

            # Get player's history battle list
            # history_battle_list = db.session.execute(
            #     'SELECT player_b FROM battlelist WHERE player_a=?\
            #     UNION \
            #     SELECT player_a FROM battlelist WHERE player_b=?', (player_a['id'], player_a['id'], )).fetchall()

            history_battle_list = union(db.session.query(Battlelist.player_b).filter_by(player_a=player_a.id).all(),
                                        db.session.query(Battlelist.player_a).filter_by(player_b=player_a.id).all())

            history_battle_list_idx = []
            for _idx in history_battle_list:
                history_battle_list_idx.append(_idx[0])

            # print(list(history_battle_list_idx))
            # Check the 3rd condtion
            flag = True
            while (flag and len(players) > 2):  # when player less 2 just insert it

                # ============= SOLVED PROBLEM 6
                # Change the order who play first
                player_a_first_query = db.session.execute('SELECT player_a FROM battlelist \
                                            WHERE player_a=? AND round=? UNION \
                                            SELECT player_a FROM battlelist \
                                            WHERE player_a=? AND round=?',
                                                          (player_a[0], round-1, player_b[0], round-1, )).fetchall()
                player_a_first_idx_set = set()
                for _ in player_a_first_query:
                    player_a_first_idx_set.add(_[0])

                player_ab_set = set({player_a[0], player_b[0]})

                # print(player_a_first_idx_set, player_ab_set,
                #       current_player_b_pointer)

                # Every one should only be the 1st once in conjuction round
                # But if the players is odd there may be times that both of them can be the 1st to play
                if (len(player_ab_set - player_a_first_idx_set) == 1 and player_b['id'] not in history_battle_list_idx):
                    player_a, player_b = player_b, player_a
                    # print('Changed Successful')
                    flag = False
                else:
                    current_player_b_pointer += 1
                    player_b = players[current_player_b_pointer]
                    # print('PLAYER B INDEX:', current_player_b_pointer)

            # At this stage player_b should not in the battled with group,
            # So it should be choosed
            db.session.execute(
                "INSERT INTO battlelist(round, player_a, player_b) VALUES(?,?,?)",
                (round, player_a['id'], player_b['id']),
            )
            db.session.commit()
            # print('INSERT ONE RECORD:', len(players))

            # delete from the whole group if it add to the current battle
            players.remove(player_a)
            players.remove(player_b)


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
                    "UPDATE settings SET value=? WHERE name = ?",
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
