import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
import numpy as np
from geopy.geocoders import Nominatim
from flask import send_file
import os
from flask import Flask
import pandas as pd
from flask import request
from flask_migrate import Migrate
from flask import after_this_request
import datetime
import re
import json

from flask_sqlalchemy import SQLAlchemy


# def create_app(test_config=None):
# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    # path to the database, and the sql flavor we are using
    SQLALCHEMY_DATABASE_URI='sqlite:///' +
    os.path.join(app.instance_path, 'crashinfo.db'),
)

import crashinfo.Lecture3_flask_demo  # Add everything from last week's API
import crashinfo.Lecture4_Visualization_demo  # Import visualization routes


# connect to the database
db = SQLAlchemy(app)
# migate the schema from models.py to the sqlite database
migrate = Migrate(app, db)

from crashinfo.models import Crash

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass


# https://www.kaggle.com/saurograndi/airplane-crashes-since-1908
# read data from csv into a pandas dataframe
df = pd.read_csv('Airplane_Crashes_and_Fatalities_Since_1908.csv')

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, World!'

# show a preview of the dataframe
@app.route('/preview')
def preview():
    return df.head().to_html()

# for arbitrary queries on the dataset like Location=X and Date=Y
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

# for adding rows to the SQL database
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


# randomly assign coordinates to each location
# alternate: use google maps/azure maps API
df['coord'] = [(np.random.uniform(-90, 90), np.random.uniform(0, 180))
               for loc in df['Location']]


#########
#
# Data Visualization routines
#

# visualize all crashes for a given year
@app.route('/visualize/<string:lib>')
def visualize(lib='matplotlib'):
    if 'year' in request.args:
        try:
            year = int(request.args['year'])
        except ValueError:
            # invalid request
            return "'year' parameter should be an integer", 422
    else:
        # invalid request
        return "You need to specify a year", 422


    # matplotlib demo
    if lib == 'matplotlib':

        # filter dataframe according to year, group by month, and
        # count the number of dates (to get the number of crashes in that month)
        query_df = df[df['Date'].str.endswith(str(year))].groupby(
            df['Date'].str[:2]).count()['Date']

        import matplotlib.pyplot as plt
        plt.rcdefaults()
        import numpy as np
        import calendar

        # month abbraviations using the 'calendar' inbuilt library 
        objects = calendar.month_abbr[1:]

        # array for positions at which the month names will be placed
        ticks = np.arange(len(objects))

        # bar heights = result of query we computed
        heights = list(query_df)

        # clear plot to start with a fresh canvas
        plt.cla()
        plt.close()

        # make the bar plot
        plt.bar(ticks, heights)

        # set month names as labels
        plt.xticks(ticks, objects)

        # set label for y-axis
        plt.ylabel('Number of crashes')

        # set title
        plt.title(f'Number of crashes by month in {year}')

        # save figure to a temporary file
        plt.savefig('tmp/plot.png')

        # return the file
        response = send_file('../tmp/plot.png')
        return response



    # plotly demo
    if lib == 'plotly':

        import plotly.graph_objects as go

        # keep rows with the requested year
        query_df = df[df['Date'].str.endswith(str(year))]

        # draw the world map scatter plot, with each coordinate lablled with location name
        fig = go.Figure(data=go.Scattergeo(
            lon=list(zip(query_df['coord']))[0],
            lat=list(zip(query_df['coord']))[1],
            text=query_df['Location'],
            mode='markers',
        ))

        # set title of figure
        fig.update_layout(
            title='Crashes',
        )

        # save figure to a temporary file
        fig.write_image("tmp/plot.webp")

        # return the file
        response = send_file('../tmp/plot.webp')
        return response
