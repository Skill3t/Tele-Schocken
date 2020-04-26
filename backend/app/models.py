"""
models.py
====================================
The Models Packages withe the Entities Game, User and Status.
A Game Class represent a hole Schocken game
"""
from app import db
import enum
import uuid


class Status(enum.Enum):
    WAITING = "waiting"
    STARTED = "started"
    ROUNDFINISCH = "roundfinish"
    GAMEFINISCH = "gamefinish"


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UUID = db.Column(db.String(200), index=True, unique=True)
    users = db.relationship('User')

    firsthalf = db.Column(db.Boolean(), default=False)
    secondhalf = db.Column(db.Boolean(), default=False)
    message = db.Column(db.String(300))
    status = db.Column(db.Enum(Status))
    stack = db.Column(db.Integer)
    changs_of_fallling_dice = db.Column(db.Float)

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
            'Stack': self.stack,
            'State': self.status.value,
            'First_Half': self.firsthalf,
            'Move': self.move_user_id,
            'First': self.first_user_id,
            'Admin': self.admin_user_id,
            'User': arrayuser,
        }
        return data

    def __init__(self):
        """
        Init a Game with 13 chips on the Stack an a changs of 1 % that a dice cann fall frome the table (Liquer round)
        """
        self.stack = 13
        self.status = Status.WAITING
        self.firsthalf = True
        self.UUID = str(uuid.uuid1())
        self.changs_of_fallling_dice = 0.005

    def moveName(self, id):
        if id is not None:
            user = User.query.filter_by(id=id).first()
            return user.name
        return ''


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)
    chips = db.Column(db.Integer)
    passive = db.Column(db.Boolean(), default=False)
    # visible = db.Column(db.Boolean(), default=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    dice1 = db.Column(db.Integer)
    dice1_visible = db.Column(db.Boolean(), default=False)
    dice2 = db.Column(db.Integer)
    dice2_visible = db.Column(db.Boolean(), default=False)
    dice3 = db.Column(db.Integer)
    dice3_visible = db.Column(db.Boolean(), default=False)
    number_dice = db.Column(db.Integer)  # Max Value = 3
    firsthalf = db.Column(db.Boolean(), default=False)

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
        '''
        dice = [
            {'Dice1': self.dice1},
            {'Dice2': self.dice2},
            {'Dice3': self.dice3},
        ]
        '''
        data = {
            'Id': self.id,
            'Name': self.name,
            'Chips': self.chips,
            'Passive': self.passive,
            'First_Half': self.firsthalf,
            # 'Visible': self.visible,
            'Number_Dice': self.number_dice,
            'Dices': dice
        }
        '''
        if self.visible:
            data = {
                'Id': self.id,
                'Name': self.name,
                'Chips': self.chips,
                'Passive': self.passive,
                'First_Half': self.firsthalf,
                # 'Visible': self.visible,
                'Number_Dice': self.number_dice,
                'Dices': dice
            }
        else:
            data = {
                'Id': self.id,
                'Name': self.name,
                'Chips': self.chips,
                'Passive': self.passive,
                'First_Half': self.firsthalf,
                'Number_Dice': self.number_dice,
                # 'Visible': self.visible
            }
        '''
        return data

    def __init__(self):
        self.chips = 0
        # self.visible = False
        self.dice1_visible = False
        self.dice2_visible = False
        self.dice3_visible = False
        self.passive = False
        self.number_dice = 0
        self.firsthalf = False
