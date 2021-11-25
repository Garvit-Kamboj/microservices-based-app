import connexion
from connexion import NoContent
import yaml
import logging, logging.config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from temperature import Temperature
from air_pressure import AirPressure
import datetime
import json
import time
import os
from pykafka import KafkaClient
from pykafka.common import OffsetType
from sqlalchemy import and_
from threading import Thread

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

DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

# External Logging configuration 
with open(os.path.join(os.path.dirname(__file__), log_conf_file), 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

#logger.info("App Conf file: %s" % app_conf_file)
#logger.info("Log Conf file: %s" % log_conf_file)

logger.info(f'connecting to DB. Hostname: {app_config["datastore"]["hostname"]}, Port: {app_config["datastore"]["port"]}')

def process_messages():
    """ Process event messages """

    current_retry_count = 0
    max_retry_count = app_config["events"]["max_allowed_retries"]
    hostname = "%s:%d" % (app_config["events"]["hostname"],  app_config["events"]["port"])

    while current_retry_count < max_retry_count:
        print("CURRENT:, MAX: ", current_retry_count, max_retry_count)
        try:
            logger.info(f"Connecting to Kafka...Attempt {current_retry_count}")
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            current_retry_count = max_retry_count
            print("Connection to Kafka successful")
        except:
            logger.error(f'Connection to Kafka failed, retrying in {app_config["events"]["sleep_time"]}')
            time.sleep(app_config["events"["sleep_time"]])
            current_retry_count += 1

    # Create a consume on a consumer group, that only reads new messages 
    # (uncommitted messages) when the service re-starts (i.e., it doesn't 
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking it, will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        #logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "temperature": # Change this to your event type
            # Store the event1 (i.e., the payload) to the DB
            # print("Temp:", payload)
            report_temperature_data(payload)
        elif msg["type"] == "air-pressure": # Change this to your event type
            # Store the event2 (i.e., the payload) to the DB
            # print("Air pressure:", payload)
            report_air_pressure_data(payload)

        # Commit the new message as being read
        consumer.commit_offsets()

def get_temperature_data(start_timestamp, end_timestamp):
    """Gets new temperature data after the timestamp"""

    # print("TIMESTAMP:", timestamp)

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    readings = session.query(Temperature).filter(
        and_(Temperature.date_created >= start_timestamp_datetime,
             Temperature.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Temperature data after %s and before %s returns %d results" %
                (start_timestamp, end_timestamp, len(results_list)))

    return results_list, 200

def get_air_pressure_data(start_timestamp, end_timestamp):
    """Gets new air pressure data after the timestamp"""

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    readings = session.query(AirPressure).filter(
        and_(AirPressure.date_created >= start_timestamp_datetime,
            AirPressure.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Air Pressure data after %s and before %s returns %d results" %
                (start_timestamp, end_timestamp, len(results_list)))

    return results_list, 200

def report_temperature_data(body):
    """ Receives a temperature reading """

    session = DB_SESSION()

    bp = Temperature(body['sensor_id'],
                       body['coordinates'],
                       body['temperature']['low'],
                       body['temperature']['intermediate'],
                       body['temperature']['high'],
                       body['timestamp'],
                    )

    session.add(bp)

    session.commit()
    session.close()

    logger.debug(f"Stored event Temperature request with a unique id of {body['sensor_id']}")

    # return NoContent, 201


def report_air_pressure_data(body):
    """ Receives an air-pressure reading """

    session = DB_SESSION()

    hr = AirPressure(body['sensor_id'],
                   body['coordinates'],
                   body['air_pressure'],
                   body['timestamp']
                    )

    session.add(hr)

    session.commit()
    session.close()

    logger.debug(f"Stored event Air-Pressure request with a unique id of {body['sensor_id']}")

    # return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("swaggerhub37-SpaceAPI-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
