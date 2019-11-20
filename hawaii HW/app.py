import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite") 

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    query = '''SELECT date, prcp
               FROM measurement 
               WHERE date >= "2016-07-15"
            '''
    df = pd.read_sql(query, con=engine)

    df_to_dict = df.to_dict(orient='split')
    prcp_dict = {date:prcp for date, prcp in df_to_dict['data']}


    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():

    query = '''SELECT station
               FROM station
            '''
    df = pd.read_sql(query, con=engine)

    df_to_dict = df.to_dict(orient='split')
    station_dict = [station[0] for station in df_to_dict['data']]

    return jsonify(station_dict)


@app.route("/api/v1.0/tobs")
def temp_monthly():

    query = '''SELECT tobs
                FROM measurement
                WHERE station == "USC00519281"
                AND date >= "2016-07-15"
            '''
    df = pd.read_sql(query, con=engine)
    df_to_dict = df.to_dict(orient='split')
    tobs_dict = [tobs[0] for tobs in df_to_dict['data']]
    

 
    return jsonify(tobs_dict)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

   
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # start date only
    if not end:
        query = f'''SELECT MIN(tobs), AVG(tobs), MAX(tobs)
                FROM measurement
                WHERE date >= "{start}"
            '''
        df = pd.read_sql(query, con=engine)
        df_to_dict = df.to_dict(orient='split')
        stats_list = df_to_dict['data'][0]

        return jsonify(stats_list)
    
   
    query = f'''SELECT MIN(tobs), AVG(tobs), MAX(tobs)
                FROM measurement
                WHERE date >= "{start}"
                AND date <= "{end}"
            '''
    df = pd.read_sql(query, con=engine)
    df_to_dict = df.to_dict(orient='split')
    stats_list = df_to_dict['data'][0]

    return jsonify(stats_list)


if __name__ == '__main__':
    app.run(debug=True)
