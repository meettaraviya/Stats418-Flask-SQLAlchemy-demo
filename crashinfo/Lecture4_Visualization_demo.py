# Import stuff for analysis
from datetime import datetime
import os
from flask import Flask, escape, request
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime


# Initiate data a bit
Data = pd.read_csv(
    'Airplane_Crashes_and_Fatalities_Since_1908.csv')
np.random.seed(42)
obs, feat = Data.shape

# This is how we initiate a flask app to then build it
app = Flask(__name__)


#################
# Print count
#
# > http://$HOSTNAME/counts
@app.route("/counts")
def counts():
    return "x"
    return(str("Dataset consist of " + str(obs) + " observations (crashes) and " + str(feat) + " features. Features are following:"))


#################
# Lets start with building a hello world API
#
# > http://$HOSTNAME/v3 --  Hello world
# > http://$HOSTNAME/v3/$some_name -- Hello $some_name
# > http://$HOSTNAME/test/hello-world -- Hello World
# @app.route("/v3", methods=["GET"])
# @app.route("/test/hello-world", methods=["GET"])
# @app.route("/v3/<string:name>", methods=["GET"])
# def hello3(name="World"):
#    return f"Hello, {escape(name)} (v3)"


###################
# What about building an API ontop of a pandas dataset?
#
# Lets use Airplane crash data: https://www.kaggle.com/saurograndi/airplane-crashes-since-1908
#
Data = pd.read_csv("Airplane_Crashes_and_Fatalities_Since_1908.csv")

# Cleanup
Data["Time"] = Data["Time"].replace(np.nan, "00:00")
Data["Time"] = Data["Time"].str.replace("c: ", "")
Data["Time"] = Data["Time"].str.replace("c:", "")
Data["Time"] = Data["Time"].str.replace("c", "")
Data["Time"] = Data["Time"].str.replace("12'20", "12:20")
Data["Time"] = Data["Time"].str.replace("18.40", "18:40")
Data["Time"] = Data["Time"].str.replace("0943", "09:43")
Data["Time"] = Data["Time"].str.replace("22'08", "22:08")
Data["Time"] = Data["Time"].str.replace(
    "114:20", "00:00"
)  # is it 11:20 or 14:20 or smth else?
Data["Time"] = Data["Date"] + " " + Data["Time"]  # joining two rows


def todate(x):
    return datetime.strptime(x, "%m/%d/%Y %H:%M")


Data["Time"] = Data["Time"].apply(todate)  # convert to date type
print("Date ranges from " + str(Data.Time.min()) + " to " + str(Data.Time.max()))
# just to avoid duplicates like 'British Airlines' and 'BRITISH Airlines'
Data.Operator = Data.Operator.str.upper()
