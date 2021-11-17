import connexion
import yaml
import logging, logging.config
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin
import requests
import datetime
import json

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")

    try:
        with open(app_config["datastore"]["filename"], "r") as file_handle:
            data = json.load(file_handle)
    except FileNotFoundError:
            data = {
                'num_temp_readings': 0,
                'max_temp_low_reading': "5°C",
                'max_temp_high_reading': "20°C",
                'max_temp_intermediate_reading': "40°C",
                'num_ap_readings': 0,
                'max_ap_reading': "102.2kPa",
                'last_updated': "2016-08-29T09:12:33Z"
            }
    
    current_datetime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%SZ")
    temperature_request = requests.get(app_config['eventstore']['url']+"data/temperature", params={"timestamp": data['last_updated']})
    air_pressure_request = requests.get(app_config['eventstore']['url']+"data/air-pressure", params={"timestamp": data['last_updated']})

    temperature_data = temperature_request.json()
    air_pressure_data = air_pressure_request.json()

    retrieved_filtered_data = {
        'high_temp_values': [],
        'intermediate_temp_values': [],
        'low_temp_values': [],
        'air_pressure_values': []
    }

    logger.info("Successfully returned temperature data after %s with %d results" %(current_datetime, len(temperature_data))) if temperature_request.status_code == 200 else logger.error("Error while receiving temperature data")
    logger.info("Successfully recieved air pressure data after %s with %d results " %(current_datetime, len(air_pressure_data))) if air_pressure_request.status_code == 200 else logger.error("Error while receiving air pressure data")

    if len(temperature_data) != 0:
        for temperature in temperature_data:
            for key, value in temperature['temperature'].items():
                if key == "high":
                    high_temp_values = retrieved_filtered_data['high_temp_values']
                    high_temp_values.append(value)
                elif key == "intermediate":
                    intermediate_temp_values = retrieved_filtered_data['intermediate_temp_values']
                    intermediate_temp_values.append(value)
                else:
                    low_temp_values = retrieved_filtered_data['low_temp_values']
                    low_temp_values.append(value)
    else:
        print(f"No more temperature data found")
        return
    
    if len(air_pressure_data) != 0:
        for air_pressure in air_pressure_data:
            air_pressure_values = retrieved_filtered_data['air_pressure_values']
            air_pressure_values.append(air_pressure['air_pressure'])
    else:
        print("No more air pressure data found")
        return

    stats_data = {
        'num_temp_readings': len(temperature_data) + data['num_temp_readings'],
        'max_temp_low_reading': min(retrieved_filtered_data['low_temp_values']),
        'max_temp_high_reading': max(retrieved_filtered_data['high_temp_values']),
        'max_temp_intermediate_reading': max(retrieved_filtered_data['intermediate_temp_values']),
        'num_ap_readings': len(air_pressure_data) + data['num_ap_readings'],
        'max_ap_reading': max(retrieved_filtered_data['air_pressure_values']),
        'last_updated': current_datetime
    }

    with open(app_config["datastore"]["filename"], 'w') as json_file:
        json.dump(stats_data, json_file, indent=4)
        logger.debug(f"Updated statistic values: {stats_data}")

    logger.info("Period Processing ended")

def get_stats():
    logger.info("Get stats request started")
    
    try:
        with open(app_config["datastore"]["filename"], "r") as file_handle:
            data = json.load(file_handle)
            logger.debug(f"Contents: {data}")
            logger.info("Get stats request completed")

            return data, 200
    except FileNotFoundError:
        logger.error("Error: Cannot open stastics file")
        return "Statistics do not exist", 404
    
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("swaggerhub37-SpaceAPI-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, debug=True)