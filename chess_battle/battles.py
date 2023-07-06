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

from chess_battle.database import db, Player, Score, BattleList
from chess_battle.settings import settings_required
import random
import csv
import os
from sqlalchemy import func

bp = Blueprint("battle", __name__)


def generate_battle_list(round):
    if round == 1:
        players = Player.query.all()
        # Randomly distributing players into groups
        for _ in range(len(players) // 2):
            first_player = random.choice(players)
            players.remove(first_player)
            second_player = random.choice(players)
            players.remove(second_player)

            bl = BattleList(round=round, player_id=first_player.id,
                            opponent_id=second_player.id, is_first=True)
            db.session.add(bl)
            db.session.commit()

        # Check if the total playes is an odd number
        if players:
            player_score = Score(
                player_id=players[0].id, round=round, score=2, notes='轮空')
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

        players = get_sorted_players(sorted_by_small=False)

        player_count = len(players)

        # ============= SOLVED PROBLEM 5
        # Check if the total playes is an odd number
        # randomly choose a player as lucky player and add +2 points to it
        # This lucky player can only choosed once
        if player_count % 2 == 1:
            lucky_players = Score.query.filter_by(notes='轮空').all()
            lucky_players_idx = []
            for lucky_player in lucky_players:
                lucky_players_idx.append(lucky_player.player_id)

            print('lUCKY PLAYER ID:', lucky_players_idx)

            lucky_player = random.choice(players)
            while (lucky_player.id in lucky_players_idx):
                lucky_player = random.choice(players)

            # Store lucky player and give it 2 score
            luky_player_in_current_round_score = Score(
                player_id=lucky_player.id, round=round, score=2, notes='轮空')
            db.session.add(luky_player_in_current_round_score)

            db.session.commit()

            players.remove(lucky_player)

        # ============= SOLVED PROBLEM 3 AND 4
        for _ in range(player_count // 2):
            # Choose 2 players in each loop
            second_player_idx = 1
            first_player = players[0]
            second_player = players[second_player_idx]

            history_battle_with_idxs = first_player.battle_with_idxs

            print('HISTORY BATTLES ID:', history_battle_with_idxs)

            # Check the 3rd condtion
            flag = True
            while (flag and len(players) > 2):  # when player less 2 just insert it
                print('BEFORE CHANGED:', first_player.id, second_player.id)
                # ============= SOLVED PROBLEM 6
                # Change the order who play first
                is_first_player_play_first = first_player.battle_first_idx.get(
                    round-1)
                is_second_player_player_first = second_player.battle_first_idx.get(
                    round-1)

                is_second_player_avaliable = True if second_player.id not in history_battle_with_idxs else False

                if is_second_player_avaliable:
                    if is_first_player_play_first == 1 and is_second_player_player_first == 0:
                        first_player, second_player = second_player, first_player
                        print('CHANGED:', first_player.id, second_player.id)
                        flag = False
                    if is_first_player_play_first == 0 and is_second_player_player_first == 0:
                        if first_player.id > second_player.id:
                            first_player, second_player = second_player, first_player
                            print('CHANGED:', first_player.id, second_player.id)
                            flag = False
                    if is_first_player_play_first == 1 and is_second_player_player_first == 1:
                        if first_player.id > second_player.id:
                            first_player, second_player = second_player, first_player
                            print('CHANGED:', first_player.id, second_player.id)
                            flag = False

                    break
                else:
                    second_player_idx += 1
                    second_player = players[second_player_idx]

                # Every one should only be the 1st once in conjuction round
                # But if the players is odd there may be times that both of them can be the 1st to play

            # At this stage player_b should not in the battled with group,
            # So it should be choosed
            battle_pair = BattleList(
                player_id=first_player.id, opponent_id=second_player.id, is_first=True, round=round)
            db.session.add(battle_pair)
            db.session.commit()

            # delete from the whole group if it add to the current battle
            players.remove(first_player)
            players.remove(second_player)


def get_sorted_players(sorted_by_small=True):
    players = Player.query.all()
    if sorted_by_small:
        sorted_players = sorted(
            players, key=lambda row: (row.score_sum, row.score_sum_opponent), reverse=True)
    else:
        sorted_players = sorted(
            players, key=lambda row: (row.score_sum), reverse=True)
    return sorted_players


@bp.route("/export", methods=("POST", "GET"))
def rank_export():
    players = get_sorted_players()

    filename = os.path.join(current_app.instance_path, 'player_export.csv')
    with open(filename, 'w', encoding='gbk') as fh:
        csvwriter = csv.writer(fh)
        csvwriter.writerow(
            ['排名', '姓名', '性别', '单位', '电话', '状态', '累计得分', '对手分', '备注'])
        for idx, player in enumerate(players):
            csvwriter.writerow([idx+1, player.name, player.gender, player.org, player.phone,
                               '-' if player.is_active else '缺席', player.score_sum, player.score_sum_opponent, player.lucky_in_round])
    flash(f'当前选手数据导出成功！', category='success')
    return send_file(filename, mimetype='text/csv',  download_name=os.path.basename(filename), as_attachment=True)


@bp.route("/", methods=("GET",))
@settings_required
def rank():
    players = get_sorted_players()
    all_players_score_details = []
    for player in players:
        all_players_score_details.append((
            player, Score.query.filter_by(player_id=player.id).all()))

    return render_template("battle/rank.html", players=players, all_players_score_details=all_players_score_details)


def get_group_rank_list():

    groups = db.session.query(Player, func.sum(Score.score))\
        .join(Score, Player.id == Score.player_id)\
        .group_by(Player.org)\
        .order_by(func.sum(Score.score).desc()).all()
    return groups


@bp.route("/group-rank", methods=("GET",))
@settings_required
def rank_group():
    groups = get_group_rank_list()
    return render_template("battle/rank_group.html", groups=groups)


@bp.route("/group-rank/export", methods=("GET", "POST"))
@settings_required
def rank_group_export():
    groups = get_group_rank_list()

    filename = os.path.join(current_app.instance_path,
                            'group_summary_export.csv')
    with open(filename, 'w', encoding='gbk') as fh:
        csvwriter = csv.writer(fh)
        csvwriter.writerow(['排名', '团体名称', '累计得分'])

        for idx, group in enumerate(groups):
            csvwriter.writerow([idx+1] + [group[0].org] + [group[1]])

    flash(f'当前团体积分排名数据导出成功！', category='success')
    return send_file(filename, mimetype='text/csv',  download_name=os.path.basename(filename), as_attachment=True)


@ bp.route("/<int:first_player_id>/<int:second_player_id>/register-score", methods=("GET", "POST"))
def register_score_bulk(first_player_id, second_player_id):
    # Get Player name by id
    message, category = None, 'warning'
    first_player = Player.query.filter_by(id=first_player_id).first()
    second_player = Player.query.filter_by(id=second_player_id).first()

    if request.method == "POST":
        score_for_a = int(request.form["score_for_a"])
        score_for_b = int(request.form['score_for_b'])
        notes_for_a = request.form['notes_for_a']
        notes_for_b = request.form['notes_for_b']
        round = g.settings["current_round"]

        score_is_correct = score_for_a + score_for_b

        if message is None and (score_is_correct == 2 or score_is_correct == 0):
            if 'add' in request.form:
                first_player_score = Score(
                    player_id=first_player_id, round=round, notes=notes_for_a, score=score_for_a)
                second_player_score = Score(
                    player_id=second_player_id, round=round, notes=notes_for_b, score=score_for_b)
                db.session.add(first_player_score)
                db.session.add(second_player_score)
                db.session.commit()
                message, category = ('Record has been writen to DB', 'success')
                return redirect(url_for('battle.battle_list', round=round))
            elif 'update' in request.form:
                first_player_score_update = Score.query.filter_by(
                    round=round, player_id=first_player_id).first()
                first_player_score_update.score = score_for_a
                first_player_score_update.notes = notes_for_a

                second_player_score_update = Score.query.filter_by(
                    round=round, player_id=second_player_id).first()
                second_player_score_update.score = score_for_b
                second_player_score_update.notes = notes_for_b

                db.session.commit()

                message, category = (
                    'Record has been Updated to DB', 'success')
                return redirect(url_for('battle.battle_list', round=round))
        else:
            message = 'Record for current round has already set, do not submit repeatly'

        flash(message, category=category)
    return render_template("battle/register_score_bulk.html", first_player=first_player, second_player=second_player)


def get_battle_list(round):
    battle_list = BattleList.query.filter_by(round=round).all()
    lucky_player = Score.query.filter_by(round=round, notes='轮空').first()
    return battle_list, lucky_player


@ bp.route("/battle-list/<int:round>", methods=("GET", "POST"))
def battle_list(round):
    battle_list, lucky_player = get_battle_list(round)

    return render_template("battle/battle_list.html", battle_list=battle_list, lucky_player=lucky_player)


@bp.route('/battle-list/<int:round>/export', methods=("POST", "GET"))
def csv_export_BattleList(round=1):
    battle_list, lucky_player = get_battle_list(round)
    filename = os.path.join(current_app.instance_path,
                            'BattleList_round_{}.csv'.format(round))
    with open(filename, 'w', encoding='gbk') as fh:
        csvwriter = csv.writer(fh)
        csvwriter.writerow(['象棋比赛第{}轮对阵情况表'.format(round)])
        csvwriter.writerow(
            ['{}(来自{})：在第{}轮中轮空'.format(lucky_player.player.name, lucky_player.player.org, round)])
        csvwriter.writerow(['桌号', '先手', '来自单位', '本局得分', '后手', '来自单位', '本局得分'])
        for idx, battle in enumerate(battle_list):
            csvwriter.writerow([idx+1, battle.player.name, battle.player.org, battle.first_score,
                               battle.opponent.name, battle.opponent.org, battle.opponent_score])
    flash(f'对阵表：第{round}轮导出成功！', category='success')
    return send_file(filename, mimetype='text/csv',  download_name=os.path.basename(filename), as_attachment=True)


@bp.route("/battle-list/<int:round>/automation", methods=("GET", "POST"))
def automation_for_score_register(round):
    player_groups = BattleList.query.filter_by(round=round).all()
    for player_pair in player_groups:
        random_score = random.randint(0, 2)
        against_score = 2 - random_score

        first_player_score = Score(
            player_id=player_pair.player_id, round=round, score=random_score)
        second_player_score = Score(
            player_id=player_pair.opponent_id, round=round, score=against_score)

        db.session.add(first_player_score)
        db.session.add(second_player_score)
        db.session.commit()
    return redirect('/')
