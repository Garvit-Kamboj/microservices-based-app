from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class AirPressure(Base):
    """ AirPressure """

    __tablename__ = "air_pressure"

    id = Column(Integer, primary_key=True)
    sensor_id = Column(String(250), nullable=False)
    coordinates = Column(String(250), nullable=False)
    air_pressure = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, sensor_id, coordinates, air_pressure, timestamp):
        """ Initializes an air pressure reading """
        self.sensor_id = sensor_id
        self.coordinates = coordinates
        self.air_pressure = air_pressure
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of an air pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['sensor_id'] = self.sensor_id
        dict['coordinates'] = self.coordinates
        dict['air_pressure'] = self.air_pressure
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
