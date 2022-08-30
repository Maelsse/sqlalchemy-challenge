#################################################
# Import Dependencies
#################################################
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Saving Keys
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup and Routes
#################################################

# Create an app, being sure to pass __name__
app = Flask(__name__)


# Index Route
@app.route("/")
def home():
    """List all available api routes."""
    return(
        f"<strong>Hawaii Climate Analysis</strong></br>"
        f"Available Routes:</br>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/start</br>" 
        f"/api/v1.0/start/end <--- Use this to search for start and end dates </br>"
        f"<strong> Start:</strong> YYYY-MM-DD / <strong>End:</strong> YYYY-MM-DD"
    )

#################################################

# Prcp Route
@app.route("/api/v1.0/precipitation")
def prcp():
    
    # Creating Session Link
    session = Session(engine)
    # Querying for Date and Prcp
    prcp = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    
    all_prcp_data = []
    for date, prcp in prcp:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp_data.append(prcp_dict)
        
    return jsonify(all_prcp_data)

 #################################################   
    
# Stations Route
@app.route("/api/v1.0/stations")
def stations():
    
    # Creating Session Link
    session = Session(engine)
    # Querying for Statiions
    stations = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()
    
    all_stations = list(np.ravel(stations))
    return jsonify(all_stations)

#################################################

# Tobs Route
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Creating Session Link
    session = Session(engine)
    # Querying for Tobs
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)

    active_station = session.query(Measurement.station).group_by(Measurement.station).\
    order_by(func.count(Measurement.date).desc()).first()
    active_station = active_station[0]
    
    tobs = session.query(Measurement.station, Measurement.tobs).filter(Measurement.station==active_station).\
    filter(Measurement.date >= query_date).all()
    
    session.close()
    
    all_tobs = list(np.ravel(tobs))
    return jsonify(all_tobs)

#################################################

# START
@app.route("/api/v1.0/<start>")
def start_dates(start):
    # Create Engine
    session = Session(engine)
    # Convert Start Date to yyyy-mm-dd
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    # Query 

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    # Create a list 
    dt_list = []
    for result in results:
        dates = {}
        dates["Start Date"] = start_date
        dates["TMIN"] = result[0]
        dates["TAVG"] = result[1]
        dates["TMAX"] = result[2]
        dt_list.append(dates)
    
    #Jsonify result

    return jsonify(dt_list)
#################################################

#START/END
@app.route("/api/v1.0/<start>/<end>")
def dates(start, end):
    # Creating Session Link
    session = Session(engine)

    # Receive a date and convert it to yyyy-mm-dd format
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end,'%Y-%m-%d')

    # Query Data for the start date value

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)
    
    session.close()

    # Create a list
    dt_list = []
    for result in results:
        dates = {}
        dates["Start Date"] = start_date
        dates["End Date"] = end_date
        dates["TMIN"] = result[0]
        dates["TAVG"] = result[1]
        dates["TMAX"] = result[2]
        dt_list.append(dates)
        if ((dates["TMIN"] =="null") and (dates["TAVG"] == "null") and (dates["TMAX"] == "null")):
            print("Sorry, that date does not appear in this dataset")

    return jsonify(dt_list)


#################################################
# Run Flask App

if __name__ == '__main__':
    app.run(debug=True)




