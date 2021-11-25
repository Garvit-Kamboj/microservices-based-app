from yaml import events
import connexion
import yaml
import logging, logging.config
from connexion import NoContent
import requests
import datetime, json
import time
import os
from threading import Thread
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

current_retry_count = 0

hostname = "%s:%d" % (app_config["events"]["hostname"], 
                        app_config["events"]["port"])
max_retry_count = app_config["events"]["max_allowed_retries"]

while current_retry_count < max_retry_count:
    try:
        logger.info(f"Connecting to kafka...Attempt {current_retry_count}")
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        producer = topic.get_sync_producer()
        logger.info(f"Connected to kafka...Attempt {current_retry_count}")
        current_retry_count = max_retry_count
    except:
        logger.error(f'Connection to Kafka failed, retrying in {app_config["events"]["sleep_time"]}')
        time.sleep(app_config["events"]["sleep_time"])
        current_retry_count+=1

def report_temperature_data(body):
    logger.info(f"Received event Temperature request with a unique id of {body['sensor_id']}")

    msg = { "type": "temperature", 
            "datetime":   
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"), 
            "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return logger.info(f"Returned event Temperature response (id: {body['sensor_id']}) with status 201")

def report_air_pressure_data(body):
    
    logger.info(f"Received event Air-Pressure request with a unique id of {body['sensor_id']}")

    msg = { "type": "air-pressure", 
            "datetime":   
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"), 
            "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return logger.info(f"Returned event Air-Pressure response (id: {body['sensor_id']}) with status 201")

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("swaggerhub37-SpaceAPI-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    #t1 = Thread(target=activate_kafka)
    #t1.setDaemon(True)
    #t1.start()
    app.run(port=8080)
