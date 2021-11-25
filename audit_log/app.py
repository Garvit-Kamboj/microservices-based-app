from yaml import events
import connexion
import yaml
import logging, logging.config
from connexion import NoContent
from flask_cors import CORS, cross_origin
import requests
import os
import datetime, json
from pykafka import KafkaClient

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(os.path.join(os.path.dirname(__file__), app_conf_file), 'r') as f:
   app_config = yaml.safe_load(f.read())

# External Logging configuration 
with open(os.path.join(os.path.dirname(__file__), log_conf_file), 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf file: %s" % app_conf_file)
logger.info("Log Conf file: %s" % log_conf_file)

def get_temperature_data(index):
    """ Get Temperature Data in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue. 
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving temperature at index %d" % index)
    temperature_events= []
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # Find the event at the index you want and 
            # return code 200
            # i.e., return event, 200
            if msg['type'] == 'temperature': 
                # print("TYPE;",msg['type'])
                temperature_events.append(msg)
                
        print("Temperature Events:", len(temperature_events))

        if index < len(temperature_events):
            return temperature_events[index], 200

    except: 
        logger.error("No more messages found")

    logger.error("Could not find temperature at index %d" % index)
    return { "message": "Not Found"}, 404


def get_air_pressure_data(index):
    # """ Get Air Pressure Details in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # # Here we reset the offset on start so that we retrieve
    # # messages at the beginning of the message queue. 
    # # To prevent the for loop from blocking, we set the timeout to
    # # 100ms. There is a risk that this loop never stops if the
    # # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving air pressure details at index %d" % index)
    air_pressure_events = []
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            # Find the event at the index you want and 
            # return code 200
            # i.e., return event, 200

            if msg['type'] == "air-pressure": 
                air_pressure_events.append(msg['payload'])
        
        print("Air Pressure Events:", len(air_pressure_events))

        if index < len(air_pressure_events):
            return air_pressure_events[index]
            
    except: 
        logger.error("No more messages found")

    logger.error("Could not find air pressure details at index %d" % index)
    return { "message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110, debug=True)
