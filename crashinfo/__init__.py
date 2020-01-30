from crashinfo.models import Crash
import os
from flask import Flask
import pandas as pd
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
import re
import json


# def create_app(test_config=None):
# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_DATABASE_URI='sqlite:///' +
    os.path.join(app.instance_path, 'crashinfo.db'),
)


# if test_config is None:
#     # load the instance config, if it exists, when not testing
#     app.config.from_object(Config)
# else:
#     # load the test config if passed in
#     app.config.from_mapping(test_config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

df = pd.read_csv('Airplane_Crashes_and_Fatalities_Since_1908.csv')

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, World!'


@app.route('/preview')
def preview():
    # return str(df[['Date','Location','Fatalities']].head())
    return df.head().to_html()


@app.route('/filter', methods=['POST', 'GET'])
def filter():
    if request.method == 'GET':
        query_df = df

        for k, v in request.args.items():
            if k in df.columns:
                query_df = query_df[query_df[k] == v]
        return query_df.to_html()
    else:
        return 'I am a teapot!', 418


@app.route('/populatedb', methods=['GET'])
def populatedb():
    pattern = re.compile('\d\d:\d\d')

    for ix, row in df.iterrows():
        month, day, year = map(int, row['Date'].split('/'))

        if pd.notna(row['Time']) and pattern.search(row['Time']):
            hour, minute = map(int, pattern.search(
                row['Time']).group(0).split(':'))
        else:
            hour, minute = 0, 0

        crash = Crash(
            aboard=row['Aboard'],
            datetime=datetime.datetime(year, month, day, hour, minute),
            fatalities=row['Fatalities'],
            ground=row['Ground'],
            location=row['Location'],
            summary=row['Summary']
        )
        db.session.add(crash)
    db.session.commit()
    return 'Done!'


@app.route('/api/filter', methods=['POST', 'GET'])
def filterdb():
    if request.method == 'GET':
        if 'Location' in request.args:
            rs = db.session.query(Crash).filter_by(
                location=request.args['Location']
            )
        else:
            rs = db.session.query(Crash).all()
        return json.dumps([item.as_dict() for item in rs], indent=4)
    else:
        return 'I am a teapot!', 418
