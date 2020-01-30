from crashinfo import db



# Date  Time    Location    Operator    Flight No       Route   Type    Registration    cn/In   Aboard  Fatalities  Ground  Summary

class Crash(db.Model):

    __tablename__ = 'Crash'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    aboard = db.Column(db.Integer)
    fatalities = db.Column(db.Integer)
    ground = db.Column(db.Integer)
    datetime = db.Column(db.DateTime)
    location = db.Column(db.String(128))
    summary = db.Column(db.String(1000))

    def __repr__(self):
        return '<Crash at time {}>'.format(self.datetime)

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


def init_db():

    db.create_all()
    db.session.commit()

if __name__ == '__main__':
    init_db()