from crashinfo import db


# this class corresponds to a table in the SQLite database
class Crash(db.Model):

    __tablename__ = 'Crash'

    ## fields of the table

    # primary key. Since no column is unique, we add an autoincrement primary key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # these 5 fields are from the datafra
    aboard = db.Column(db.Integer)
    fatalities = db.Column(db.Integer)
    ground = db.Column(db.Integer)
    datetime = db.Column(db.DateTime)
    # we need to specify the max string length for string fields
    location = db.Column(db.String(128))
    summary = db.Column(db.String(1000))

    def __repr__(self):
        return '<Crash at time {}>'.format(self.datetime)

    # required for converting to json in our code
    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

# initialize the database
def init_db():

    # creates the database schema when run
    # REQUIRED when you create the database for the first time
    db.create_all()

    # 'save' all changes
    db.session.commit()

if __name__ == '__main__':
    # initialize the database if run as the main file
    init_db()