from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Temperature(Base):
    """ Temperature """

    __tablename__ = "temperature"

    id = Column(Integer, primary_key=True)
    sensor_id = Column(String(250), nullable=False)
    coordinates = Column(String(250), nullable=False)
    low = Column(String(250), nullable=False)
    intermediate = Column(String(250), nullable=False)
    high = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, sensor_id, coordinates, low, intermediate, high, timestamp):
        """ Initializes a temperature reading """
        self.sensor_id = sensor_id
        self.coordinates = coordinates
        self.low = low
        self.intermediate = intermediate
        self.high = high
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a temperature reading """
        dict = {}
        dict['id'] = self.id
        dict['sensor_id'] = self.sensor_id
        dict['coordinates'] = self.coordinates
        dict['temperature'] = {}
        dict['temperature']['low'] = self.low
        dict['temperature']['intermediate'] = self.intermediate
        dict['temperature']['high'] = self.high
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
