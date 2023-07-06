from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy import func


db = SQLAlchemy()


class Player(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(10), nullable=False)
    gender = Column(String(4), nullable=False)
    org = Column(String, nullable=False)
    phone = Column(String(11), nullable=False)
    is_active = Column(Boolean, default=True)

    scores = db.relationship('Score', backref='player')
    battle_with = db.relationship(
        'BattleList', backref='player')

    def __repr__(self):
        return '{}-{}-{}'.format(self.name, self.org, self.phone)

    @property
    def battle_with_idxs(self):
        battle_with_idxs = []
        for battle in self.battle_with:
            battle_with_idxs.append(battle.opponent_id)

        query_battles_from_opponent = BattleList.query.filter_by(
            opponent_id=self.id).all()
        for opponent_battle in query_battles_from_opponent:
            battle_with_idxs.append(opponent_battle.player_id)
        return battle_with_idxs

    @property
    def battle_first_idx(self):
        first_idx = {}
        for battle in self.battle_with:
            first_idx[battle.round] = 1

        query_battles_from_opponent = BattleList.query.filter_by(
            opponent_id=self.id).all()
        for opponent_battle in query_battles_from_opponent:
            first_idx[opponent_battle.round] = 0
        return [(x, first_idx[x]) for x in sorted(first_idx)]

    @property
    def score_sum(self):
        score_sum = 0
        for score in self.scores:
            score_sum += score.score
        return score_sum

    @property
    def lucky_in_round(self):
        for score in self.scores:
            if score.notes == '轮空':
                return '第{}轮轮空'.format(score.round)
        return '-'

    @property
    def score_sum_opponent(self):
        score_sum = 0
        for opponet in self.battle_with:
            score_sum += opponet.opponent.score_sum
        return score_sum


class Score(db.Model):
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    round = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    notes = Column(String, default='-')
    created = Column(DateTime, default=datetime.now())


class Settings(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, default='Input')
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.now())


class BattleList(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    round = Column(Integer, nullable=False)
    player_id = Column(Integer, ForeignKey('player.id'), nullable=False)
    opponent_id = Column(Integer)
    is_first = Column(Boolean, default=False)

    # first_player = db.relationship('Player', backref='first_player', )
    @property
    def opponent(self):
        return Player.query.filter_by(id=self.opponent_id).first()

    @property
    def first_score(self):
        first_score_obj = Score.query.filter_by(
            player_id=self.player_id, round=self.round).first()
        if first_score_obj:
            return first_score_obj.score
        else:
            return '比赛中……'

    @property
    def opponent_score(self):
        opponent_score_obj = Score.query.filter_by(
            player_id=self.opponent_id, round=self.round).first()
        if opponent_score_obj:
            return opponent_score_obj.score
        else:
            return '比赛中……'
