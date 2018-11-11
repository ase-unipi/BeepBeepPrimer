# encoding: utf8
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128), nullable=False)
    strava_token = db.Column(db.String(128))
    age = db.Column(db.Integer)
    weight = db.Column(db.Numeric(4, 1))
    max_hr = db.Column(db.Integer)
    rest_hr = db.Column(db.Integer)
    vo2max = db.Column(db.Numeric(4, 2))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

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

class Objective(db.Model):
    __tablename__ = 'objective'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Unicode(128))
    target_distance = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    runner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    runner = relationship('User', foreign_keys='Objective.runner_id')

    @property
    def completion(self):
        runs = db.session.query(Run) \
                         .filter(Run.start_date > self.start_date) \
                         .filter(Run.start_date <= self.end_date) \
                         .filter(Run.runner_id == self.runner_id)

        return min(round(100 * (sum([run.distance for run in runs]) / (self.target_distance)), 2), 100)

# Database for the report (mail)
# I change the name Mail because there was a conflict in background.py
class Report(db.Model):
    __tablename__ = 'mail'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', foreign_keys='Report.id_user')
    timestamp = db.Column(db.DateTime)
    choice_time = db.Column(db.Float)

    def set_user(self,id_usr):
        self.id_user = id_usr

    def set_timestamp(self):
        self.timestamp = datetime.now()

    def set_decision(self,choice):
        self.choice_time = (float(choice)*3600.0)


class Challenge(db.Model):
    __tablename__ = 'challenge'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Unicode(128))
    confront = db.Column(db.Integer)
    distance = db.Column(db.Float)
    elapsed_time = db.Column(db.Float)
    average_speed = db.Column(db.Float)
    runner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    runner = relationship('User', foreign_keys='Challenge.runner_id')

    def setname(self,name):
        self.name = name

    def setconfront(self,idconf):
        self.confront = idconf

    def setdistance(self,dist):
        self.distance = dist

    def setelapsedtime(self,elapstime):
        self.elapsed_time = elapstime

    def setaveragespeed(self,avgspeed):
        self.average_speed = avgspeed

    def setrunner(self,iduserrun):
        self.runner_id = iduserrun