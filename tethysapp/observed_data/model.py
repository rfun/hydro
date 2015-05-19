from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import sessionmaker

from geoalchemy2 import Geometry

from .utilities import get_persistent_store_engine

# Spatial DB Engine, sessiomaker, and base
spatial_engine = get_persistent_store_engine('sites_db')
SpatialSessionMaker = sessionmaker(bind=spatial_engine)
SpatialBase = declarative_base()

# SQLAlchemy ORM definition for the spatial_stream_gages table
class SitesTable(SpatialBase):
    __tablename__ = 'sites'

    # Columns
    id = Column(Integer, primary_key=True)
    sitename = Column(Text)
    sitecode = Column(Text)
    servicecode = Column(Text)
    serviceURL = Column(Text)
    geom = Column(Geometry('POINT'))

    def __init__(self, latitude, longitude, name, code, servCode,servURL):
        """
        Constructor for a site
        """
        self.geom = 'SRID=4326;POINT({0} {1})'.format(longitude, latitude)
        self.sitename = name
        self.sitecode = code
        self.servicecode = servCode
        self.serviceURL = servURL