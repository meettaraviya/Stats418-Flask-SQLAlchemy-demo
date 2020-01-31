# Import stuff for analysis
import matplotlib.pylab as pl
import matplotlib.gridspec as gridspec
from datetime import datetime
import os
from flask import Flask, escape, request, send_file
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
from crashinfo import app


# Initiate data a bit
Data = pd.read_csv(
    'Airplane_Crashes_and_Fatalities_Since_1908.csv')
np.random.seed(42)
obs, feat = Data.shape


#################
# Print count
#
# > http://$HOSTNAME/counts
@app.route("/counts")
def counts():
    return(str("Dataset consist of " + str(obs) + " observations (crashes) and " + str(feat)))


#################
# Print nulls
#
# > http://$HOSTNAME/counts/nulls
@app.route("/counts/nulls")
def nulls():
    return(str(Data.isnull().sum()))  # calculating missing values in rows)


# cleaning up
Data['Time'] = Data['Time'].replace(np.nan, '00:00')
Data['Time'] = Data['Time'].str.replace('c: ', '')
Data['Time'] = Data['Time'].str.replace('c:', '')
Data['Time'] = Data['Time'].str.replace('c', '')
Data['Time'] = Data['Time'].str.replace('12\'20', '12:20')
Data['Time'] = Data['Time'].str.replace('18.40', '18:40')
Data['Time'] = Data['Time'].str.replace('0943', '09:43')
Data['Time'] = Data['Time'].str.replace('22\'08', '22:08')
Data['Time'] = Data['Time'].str.replace(
    '114:20', '00:00')  # is it 11:20 or 14:20 or smth else?

Data['Time'] = Data['Date'] + ' ' + Data['Time']  # joining two rows


def todate(x):
    return datetime.strptime(x, '%m/%d/%Y %H:%M')


Data['Time'] = Data['Time'].apply(todate)  # convert to date type
print('Date ranges from ' + str(Data.Time.min()) + ' to ' + str(Data.Time.max()))

# just to avoid duplicates like 'British Airlines' and 'BRITISH Airlines'
Data.Operator = Data.Operator.str.upper()


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

#################
#
#
@app.route("/graph/total")
def accidents_total():
    # Temp is going to be temporary data frame
    Temp = Data.groupby(Data.Time.dt.year)[['Date']].count()
    Temp = Temp.rename(columns={"Date": "Count"})

    plt.figure(figsize=(12, 6))
    plt.style.use('bmh')
    plt.plot(Temp.index, 'Count', data=Temp,
             color='blue', marker=".", linewidth=1)
    plt.xlabel('Year', fontsize=10)
    plt.ylabel('Count', fontsize=10)
    plt.title('Count of accidents by Year', loc='Center', fontsize=14)

    plt.savefig('tmp/plot.png')
    response = send_file('../tmp/plot.png')
    return response


#################
#
#
@app.route("/graph/by/year")
def year():
    # Temp is going to be temporary data frame
    Temp = Data.groupby(Data.Time.dt.year)[['Date']].count()
    Temp = Temp.rename(columns={"Date": "Count"})

    plt.figure(figsize=(12, 6))
    plt.style.use('bmh')
    plt.plot(Temp.index, 'Count', data=Temp,
             color='blue', marker=".", linewidth=1)
    plt.xlabel('Year', fontsize=10)
    plt.ylabel('Count', fontsize=10)
    plt.title('Count of accidents by Year', loc='Center', fontsize=14)

    plt.savefig('tmp/plot.png')
    response = send_file('../tmp/plot.png')
    return response


################
#
#
@app.route("/graph/by/month")
def bymonth():
    gs = gridspec.GridSpec(2, 2)
    pl.figure(figsize=(15, 10))
    plt.style.use('seaborn-muted')
    ax = pl.subplot(gs[0, :])  # row 0, col 0
    sns.barplot(Data.groupby(Data.Time.dt.month)[['Date']].count().index, 'Date', data=Data.groupby(
        Data.Time.dt.month)[['Date']].count(), color='lightskyblue', linewidth=2)
    plt.xticks(Data.groupby(Data.Time.dt.month)[['Date']].count().index, [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.xlabel('Month', fontsize=10)
    plt.ylabel('Count', fontsize=10)
    plt.title('Count of accidents by Month', loc='Center', fontsize=14)

    ax = pl.subplot(gs[1, 0])
    sns.barplot(Data.groupby(Data.Time.dt.weekday)[['Date']].count().index, 'Date', data=Data.groupby(
        Data.Time.dt.weekday)[['Date']].count(), color='lightskyblue', linewidth=2)
    plt.xticks(Data.groupby(Data.Time.dt.weekday)[['Date']].count().index, [
        'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    plt.xlabel('Day of Week', fontsize=10)
    plt.ylabel('Count', fontsize=10)
    plt.title('Count of accidents by Day of Week', loc='Center', fontsize=14)

    ax = pl.subplot(gs[1, 1])
    sns.barplot(Data[Data.Time.dt.hour != 0].groupby(Data.Time.dt.hour)[['Date']].count().index, 'Date',
                data=Data[Data.Time.dt.hour != 0].groupby(Data.Time.dt.hour)[['Date']].count(), color='lightskyblue', linewidth=2)
    plt.xlabel('Hour', fontsize=10)
    plt.ylabel('Count', fontsize=10)
    plt.title('Count of accidents by Hour', loc='Center', fontsize=14)
    plt.tight_layout()

    plt.savefig('tmp/plot.png')
    response = send_file('../tmp/plot.png')
    return response


#################
#
#
@app.route("/graph/military")
def military():
    Temp = Data.copy()
    Temp['isMilitary'] = Temp.Operator.str.contains('MILITARY')
    Temp = Temp.groupby('isMilitary')[['isMilitary']].count()
    Temp.index = ['Passenger', 'Military']

    Temp2 = Data.copy()
    Temp2['Military'] = Temp2.Operator.str.contains('MILITARY')
    Temp2['Passenger'] = Temp2.Military == False
    Temp2 = Temp2.loc[:, ['Time', 'Military', 'Passenger']]
    Temp2 = Temp2.groupby(Temp2.Time.dt.year)[
        ['Military', 'Passenger']].aggregate(np.count_nonzero)

    colors = ['yellowgreen', 'lightskyblue']
    plt.figure(figsize=(15, 6))
    plt.subplot(1, 2, 1)
    patches, texts = plt.pie(
        Temp.isMilitary, colors=colors, labels=Temp.isMilitary, startangle=90)
    plt.legend(patches, Temp.index, loc="best", fontsize=10)
    plt.axis('equal')
    plt.title('Total number of accidents by Type of flight',
              loc='Center', fontsize=14)

    plt.subplot(1, 2, 2)
    plt.plot(Temp2.index, 'Military', data=Temp2,
             color='lightskyblue', marker=".", linewidth=1)
    plt.plot(Temp2.index, 'Passenger', data=Temp2,
             color='yellowgreen', marker=".", linewidth=1)
    plt.legend(fontsize=10)
    plt.xlabel('Year', fontsize=10)
    plt.ylabel('Count', fontsize=10)
    plt.title('Count of accidents by Year', loc='Center', fontsize=14)
    plt.tight_layout()

    plt.savefig('tmp/plot.png')
    response = send_file('../tmp/plot.png')
    return response


#################
#
#
@app.route("/graphs/people")
def people():
    Fatalities = Data.groupby(Data.Time.dt.year).sum()
    Fatalities['Proportion'] = Fatalities['Fatalities'] / Fatalities['Aboard']

    plt.figure(figsize=(15, 6))
    plt.subplot(1, 2, 1)
    plt.fill_between(Fatalities.index, 'Aboard',
                     data=Fatalities, color="skyblue", alpha=0.2)
    plt.plot(Fatalities.index, 'Aboard', data=Fatalities,
             marker=".", color="Slateblue", alpha=0.6, linewidth=1)
    plt.fill_between(Fatalities.index, 'Fatalities',
                     data=Fatalities, color="olive", alpha=0.2)
    plt.plot(Fatalities.index, 'Fatalities', data=Fatalities,
             color="olive", marker=".", alpha=0.6, linewidth=1)
    plt.legend(fontsize=10)
    plt.xlabel('Year', fontsize=10)
    plt.ylabel('Amount of people', fontsize=10)
    plt.title('Total number of people involved by Year',
              loc='Center', fontsize=14)

    plt.subplot(1, 2, 2)
    plt.plot(Fatalities.index, 'Proportion', data=Fatalities,
             marker=".", color='red', linewidth=1)
    plt.xlabel('Year', fontsize=10)
    plt.ylabel('Ratio', fontsize=10)
    plt.title('Fatalities / Total Ratio by Year', loc='Center', fontsize=14)
    plt.tight_layout()

    plt.savefig('tmp/plot.png')
    response = send_file('../tmp/plot.png')
    return response
