# Import flash and other stuff we will need
import pandas as pd
import numpy as np
from flask import Flask, escape, request
import os
from datetime import datetime

# This is how we initiate a flask app to then build it
app = Flask(__name__)


#################
# Lets start with building a hello world API
#
# > http://$HOSTNAME/v1 -- return Hello World!
# > http://$HOSTNAME/v1?name=some_name -- return Hello $some_name
@app.route("/v1")
def hello():
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)}!"


# Let's make the API more RESTful
#
# > http://$HOSTNAME/v2/some_name -- return Hello $some_name
@app.route("/v2/<name>", methods=["GET"])
def hello2(name):
    return f"Hello, {escape(name)} (v2)"


# Let's add some basic things:
#
# > http://$HOSTNAME/v3 --  Hello world
# > http://$HOSTNAME/v3/$some_name -- Hello $some_name
# > http://$HOSTNAME/test/hello-world -- Hello World
@app.route("/v3", methods=["GET"])
@app.route("/test/hello-world", methods=["GET"])
@app.route("/v3/<string:name>", methods=["GET"])
def hello3(name="World"):
    return f"Hello, {escape(name)} (v3)"


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


##################
# Lets build API functionality to provide number of airplane crashes by year
#
# > http://$HOSTNAME/airplane/total -- number of crashes for every year
# > http://$HOSTNAME/airplane/total/$year -- number of crashes for a given year
#

# Report error if they pass us a string for year
@app.route("/airplane/total/<string:year>")
def foo(year):
    return f"Sorry I can only handle integers"


# handle /airplane/total and /airplane/total/$year
@app.route("/airplane/total", methods=["GET", "POST"])
@app.route("/airplane/total/<int:year>", methods=["GET", "POST"])
def total_crashes(year=False):
    # Build a pandas dataframe of number of plane crashes by year
    df = (
        Data.groupby(Data.Time.dt.year)[["Date"]]
        .count()
        .rename(columns={"Date": "Year"})
    )

    # For now we are only supporting GET returns...
    if request.method == "GET":
        # If they they did not provide a year return a JSON dictionary of plane
        # crashes for every year we have available
        if year is False:
            return df.to_dict()

        # If they requested a year we have, return the number of plane crashes
        # for that year
        if year <= 2009 and year >= 1908:
            return str(df["Year"][year])
        # If they requested a year we don't have, report a 404 error
        else:
            return "ERROR 404: Our dataset only contains data for 1908-2009", 404

    # FIXME: Evetually we might also want to support POST requests so people
    # can send us information on new plane crashes we do not yet know about
    if request.method == "POST":
        # save_data()
        return "ERROR 404: We do not yet know how to save", 404


##################
# Main method to launch Flask server
#
# --> host: makes it bind publically (could have als been 0.0.0.0 instead). If
# we did not specify this it would only bind to 127.0.0.1 which means it would
# only be accessible from the local computer
#
# --> port: set the "port" we bind to to be based on our Linux user ID. This
# way if multiple users try to launch flask servers each will run on a
# different port to avoid conflicts
#
# --> debug: enable debugging and more verbose information since we are still
# developing the app and not running it in a production environment
if __name__ == "__main__":
    app.run(host="stats418.thevelozgroup.com",
            port=os.getuid() + 50000, debug=True)
