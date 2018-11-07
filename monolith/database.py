# encoding: utf8
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), unique=True, nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    strava_token = db.Column(db.String(128))
    age = db.Column(db.Integer)
    weight = db.Column(db.Numeric(4, 1))
    max_hr = db.Column(db.Integer)
    rest_hr = db.Column(db.Integer)
    vo2max = db.Column(db.Numeric(4, 2))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    run = relationship('Run', cascade='delete')
    objective = relationship('Training_Objective', cascade='delete')
    challenge = relationship('Challenge', cascade='delete')

    is_anonymous = False

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        print(password, " ", self.password)
        #checked = self.password == password
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id


class Run(db.Model):
    __tablename__ = 'run'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Unicode(128))
    strava_id = db.Column(db.Integer)
    distance = db.Column(db.Float)
    start_date = db.Column(db.DateTime)
    elapsed_time = db.Column(db.Float)
    average_speed = db.Column(db.Float)
    average_heartrate = db.Column(db.Float)
    total_elevation_gain = db.Column(db.Float)
    runner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    runner = relationship('User', foreign_keys='Run.runner_id')

class Training_Objective(db.Model):
    __tablename__ = 'training_objective'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    kilometers_to_run = db.Column(db.Float)
    runner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    runner = relationship('User', foreign_keys='Training_Objective.runner_id')
    
class Challenge(db.Model):
    __tablename__ = 'challenge'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    run_challenged_id = db.Column(db.Integer, db.ForeignKey('run.id'))
    challenged = relationship('Run', foreign_keys='Challenge.run_challenged_id')
    run_challenger_id = db.Column(db.Integer, db.ForeignKey('run.id'))
    challenger = relationship('Run', foreign_keys='Challenge.run_challenger_id')
    runner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    runner = relationship('User', foreign_keys='Challenge.runner_id') 
    start_date = db.Column(db.DateTime)
    result = db.Column(db.Boolean, default=False)
