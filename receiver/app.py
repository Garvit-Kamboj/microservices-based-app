from yaml import events
import connexion
import yaml
import logging, logging.config
from connexion import NoContent
import requests
import datetime, json
from pykafka import KafkaClient

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def report_temperature_data(body):

    logger.info(f"Received event Temperature request with a unique id of {body['sensor_id']}")
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
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

    hostname = "%s:%d" % (app_config["events"]["hostname"], 
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
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
    app.run(port=8080, debug=True)