import click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime

db = SQLAlchemy()


class Player(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(10), nullable=False)
    gender = Column(String(4), nullable=False)
    org = Column(String, nullable=False)
    phone = Column(String(11), nullable=False)
    showable = Column(Boolean, default=True)

    scores = db.relationship('Score', backref='player')


class Score(db.Model):
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    round = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    against_score = Column(Integer, nullable=False)
    notes = Column(String, default='-')
    created = Column(DateTime, default=datetime.now())


class Settings(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, default='Input')
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.now())


class Battlelist(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    round = Column(Integer, nullable=False)
    player_a = Column(Integer, ForeignKey('player.id'), nullable=False)
    player_b = Column(Integer, ForeignKey('player.id'), nullable=False)

    player_a_t = db.relationship(
        'Player', backref='player_a', foreign_keys=[player_a])
    player_b_t = db.relationship(
        'Player', backref='player_b', foreign_keys=[player_b])
