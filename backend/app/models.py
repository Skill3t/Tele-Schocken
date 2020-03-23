from app import db
import enum
import uuid

# from sqlalchemy.ext.declarative import declarative_base


# Base = declarative_base()
class Status(enum.Enum):
    WAITING = "waiting"
    STARTED = "started"
    FINISCH = "finish"


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UUID = db.Column(db.String(200), index=True, unique=True)
    users = db.relationship('User')

    firsthalf = db.Column(db.Boolean(), default=False)
    status = db.Column(db.Enum(Status))
    stack = db.Column(db.Integer)
    changs_of_fallling_dice = db.Column(db.Float)

    move_user_id = db.Column(db.Integer)
    first_user_id = db.Column(db.Integer)
    admin_user_id = db.Column(db.Integer)

    def to_dict(self):
        arrayuser = []
        for user in self.users:
            arrayuser.append(user.to_dict())
        data = {
            'stack': self.stack,
            'state': self.status,
            'First_Half': self.firsthalf,
            'Move': self.move_user_id,
            'First': self.first_user_id,
            'Admin': self.admin_user_id,
            'User': arrayuser,
        }
        return data

    def __init__(self):
        self.stack = 13
        self.status = Status.WAITING
        self.firsthalf = True
        self.UUID = str(uuid.uuid1())
        self.changs_of_fallling_dice = 0.01


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)
    chips = db.Column(db.Integer)
    passive = db.Column(db.Boolean(), default=False)
    visible = db.Column(db.Boolean(), default=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    dice1 = db.Column(db.Integer)
    dice2 = db.Column(db.Integer)
    dice3 = db.Column(db.Integer)
    number_dice = db.Column(db.Integer)  # Max Value = 3

    def to_dict(self):
        data = {
            'id': self.id,
            'Name': self.name,
            'Chips': self.chips,
            'passive': self.passive,
            'visible': self.visible
        }
        return data
    '''
    def __init__(self, **kwargs):
        print("user")
        super().__init__(**kwargs)
        self.chips = 0
        self.visible = False
        self.passive = False
    '''
    def __init__(self):
        self.chips = 0
        self.visible = False
        self.passive = False
        self.number_dice = 0
