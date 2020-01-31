import numpy as np
from geopy.geocoders import Nominatim
from flask import send_file
import crashinfo.Lecture3_flask_demo  # Add everything from last week's API
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
from crashinfo.models import Crash

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass


# https://www.kaggle.com/saurograndi/airplane-crashes-since-1908
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


geolocator = Nominatim()
# df['coord'] = [geolocator.geocode(loc)[-1] for loc in df['Location']]
df['coord'] = [(np.random.uniform(-90, 90), np.random.uniform(0, 180))
               for loc in df['Location']]


#########
#
# Data Visualization routines
#
@app.route('/visualize/<string:lib>')
def visualie(lib='matplotlib'):
    if 'year' in request.args:
        try:
            year = int(request.args['year'])
        except ValueError:
            return "'year' parameter should be an integer", 422
    else:
        return "You need to specify a year", 422

    if lib == 'matplotlib':

        query_df = df[df['Date'].str.endswith(str(year))].groupby(
            df['Date'].str[:2]).count()['Date']

        import matplotlib.pyplot as plt
        plt.rcdefaults()
        import numpy as np
        import calendar

        objects = calendar.month_abbr[1:]
        ticks = np.arange(len(objects))
        heights = list(query_df)

        plt.cla()
        plt.close()
        plt.bar(ticks, heights, align='center', alpha=0.5)
        plt.xticks(ticks, objects)
        plt.ylabel('Number of crashes')
        plt.title(f'Number of crashes by month in {year}')

        plt.savefig('tmp/plot.png')

        response = send_file('../tmp/plot.png')

        return response

    if lib == 'plotly':

        import plotly.graph_objects as go

        query_df = df[df['Date'].str.endswith(year)].groupby(
            df['Date'].str[:2]).count()

        fig = go.Figure(data=go.Scattergeo(
            lon=list(zip(query_df['coord']))[0],
            lat=list(zip(query_df['coord']))[1],
            text=query_df['Location'],
            mode='markers',
            # marker_color = query_df['cnt'],
        ))

        fig.update_layout(
            title='Crashes',
            # geo_scope='usa',
        )
        fig.write_image("tmp/plot.webp")

        response = send_file('../tmp/plot.webp')

        return response
