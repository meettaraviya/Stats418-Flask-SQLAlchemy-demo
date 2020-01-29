import os

from flask import Flask

import pandas as pd

from flask import request


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'crashinfo.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

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
            params = {}
            query_df = df
            
            for k,v in request.args.items():

                if k in df.columns:

                    query_df = query_df[query_df[k] == v]

            return query_df.to_html()
        else:
            return 'I am a teapot!', 418


    return app