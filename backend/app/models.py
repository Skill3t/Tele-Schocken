"""
models.py
====================================
The Models Packages withe the Entities Game, User and Status.
A Game Class represent a hole Schocken game
"""
from app import db
import enum
import uuid
from datetime import datetime
from markupsafe import Markup


class Status(enum.Enum):
    WAITING = "waiting"
    STARTED = "started"
    ROUNDFINISCH = "roundfinish"
    PLAYFINAL = "playfinal"
    GAMEFINISCH = "gamefinish"


class BaseGameData():
    halfcount = db.Column(db.Integer)
    finalcount = db.Column(db.Integer)
    started = db.Column(db.DateTime())
    refreshed = db.Column(db.DateTime())
    schockoutcount = db.Column(db.Integer)
    fallling_dice_count = db.Column(db.Integer)
    throw_dice_count = db.Column(db.Integer)
    changs_of_fallling_dice = db.Column(db.Float)
    stack_max = db.Column(db.Integer)
    play_final = db.Column(db.Boolean(), default=True)

    def __init__(self):
        """
        Init a Game with 13 chips on the Stack an a changs of 0,3 % that a dice cann fall frome the table (Liquer round)
        """
        self.halfcount = 0
        self.finalcount = 0
        self.fallling_dice_count = 0
        self.schockoutcount = 0
        self.throw_dice_count = 0
        self.changs_of_fallling_dice = 0.003
        self.stack_max = 13
        self.play_final = True


class Statistic(BaseGameData, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usercount = db.Column(db.Integer)


class Game(BaseGameData, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UUID = db.Column(db.String(200), index=True, unique=True)
    users = db.relationship('User')
    message = db.Column(db.String(300))
    status = db.Column(db.Enum(Status))
    stack = db.Column(db.Integer)
    move_user_id = db.Column(db.Integer)
    first_user_id = db.Column(db.Integer)
    admin_user_id = db.Column(db.Integer)

    def to_dict(self):
        """
        return a API conform Key Value Store that can convert to JSON
        """
        arrayuser = []
        for user in self.users:
            arrayuser.append(user.to_dict())
        data = {
            'Stack_Max': self.stack_max,
            'Stack': self.stack,
            'State': self.status.value,
            'Move': self.move_user_id,
            'Message': self.message,
            'First': self.first_user_id,
            'Admin': self.admin_user_id,
            'Game_Half_Count': self.halfcount,
            'Game_Final_Count': self.finalcount,
            'User': arrayuser,
        }
        return data

    def __init__(self):
        """
        Init a Game with 13 chips on the Stack an a changs of 1 % that a dice cann fall frome the table (Liquer round)
        """
        super().__init__()
        self.stack = 13
        self.status = Status.WAITING
        self.UUID = str(uuid.uuid1())

        self.started = datetime.now()
        self.refreshed = datetime.now()

    def moveName(self, id):
        if id is not None:
            user = User.query.filter_by(id=id).first()
            if user is not None:
                return user.name
            else:
                return ''
        return ''


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)
    chips = db.Column(db.Integer)
    passive = db.Column(db.Boolean(), default=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    dice1 = db.Column(db.Integer)
    dice1_visible = db.Column(db.Boolean(), default=False)
    dice2 = db.Column(db.Integer)
    dice2_visible = db.Column(db.Boolean(), default=False)
    dice3 = db.Column(db.Integer)
    dice3_visible = db.Column(db.Boolean(), default=False)
    number_dice = db.Column(db.Integer)  # Max Value = 3
    halfcount = db.Column(db.Integer)
    finalcount = db.Column(db.Integer)

    def user_name(self):
        return Markup(self.name)

    def to_dict(self):
        dice = []
        if self.dice1_visible:
            dice1 = {'Dice1': self.dice1}
            dice.append(dice1)
        if self.dice2_visible:
            dice2 = {'Dice2': self.dice2}
            dice.append(dice2)
        if self.dice3_visible:
            dice3 = {'Dice3': self.dice3}
            dice.append(dice3)

        data = {
            'Id': self.id,
            'Name': self.name,
            'Chips': self.chips,
            'Passive': self.passive,
            'Halfcount': self.halfcount,
            'Finalcount': self.finalcount,
            'Number_Dice': self.number_dice,
            'Dices': dice
        }
        return data

    def __init__(self):
        self.chips = 0
        self.dice1_visible = False
        self.dice2_visible = False
        self.dice3_visible = False
        self.passive = False
        self.number_dice = 0
        self.halfcount = 0
        self.finalcount = 0
