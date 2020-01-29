from crashinfo import db

# Date 	Time 	Location 	Operator 	Flight No   	Route 	Type 	Registration 	cn/In 	Aboard 	Fatalities 	Ground 	Summary

class Crash(db.Model):

    aboard = db.Column(db.Integer)
    fatalities = db.Column(db.Integer)
    ground = db.Column(db.Integer)
    datetime = db.Column(db.DateTime,  primary_key=True)
    location = db.Column(db.String(128))
    summary = db.Column(db.String(1000))

    def __repr__(self):
        return '<Crash at time {}>'.format(self.datetime)
