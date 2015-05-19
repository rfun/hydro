# Put your persistent store models in this file
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, Text
from sqlalchemy.orm import sessionmaker

from .utilities import get_persistent_store_engine

# DB Engine, sessionmaker and base
engine = get_persistent_store_engine('stream_gage_db')
SessionMaker = sessionmaker(bind=engine)
Base = declarative_base()

# DB Engine, sessionmaker and base for SeriesCatalog
engine = get_persistent_store_engine('stream_gage_db')
SessionMaker = sessionmaker(bind=engine)
Base = declarative_base()

# SQLAlchemy ORM definition for the stream_gages table
class StreamGage (Base):
    '''
    Example SQLAlchemy DB Model
    '''
    __tablename__ = 'stream_gages'

    # Columns
    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    value = Column(Integer)
    name = Column(Text)

    def __init__(self, latitude, longitude, value, name):
        """
        Constructor for a gage
        """
        self.latitude = latitude
        self.longitude = longitude
        self.value = value
	self.name = name


<ServCode>NWISDV</ServCode>
<ServURL>
http://hydroportal.cuahsi.org/usgs_NWIS/cuahsi_1_1.asmx
</ServURL>
<location>NWISDV_02223500</location>
<VarCode>NWISDV_00060_DataType=MEAN</VarCode>
<VarName>Discharge, cubic feet per second</VarName>
<beginDate>10/1/1897 12:00:00 AM</beginDate>
<endDate>5/28/2014 12:00:00 AM</endDate>
<ValueCount>42606</ValueCount>
<Sitename>OCONEE RIVER AT DUBLIN, GA</Sitename>
<latitude>32.54461117</latitude>
<longitude>-82.894587</longitude>
<datatype>MEAN</datatype>
<valuetype>Field Observation</valuetype>
<samplemedium>Surface Water</samplemedium>
<timeunits>day</timeunits>
<conceptKeyword>Discharge, stream</conceptKeyword>
<genCategory/>
<TimeSupport>1</TimeSupport>


# SQLAlchemy ORM definition for the stream_gages table
class SeriesCatalog (Base):

    __tablename__ = 'series_catalog'

    # Columns
    id = Column(Integer, primary_key=True)
    servURL = Column(Text)
    siteCode = Column(Text)
    varCode = Column(Text)
    varName = Column(Text)
    beginDate = Column(DateTime)
    endDate = Column(DateTime)
    valueCount = Column(BIGINT)
    siteName = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)

    value = Column(Integer)
    name = Column(Text)
    name = Column(Text)

    def __init__(self, latitude, longitude, value, name):
        """
        Constructor for a gage
        """
        self.latitude = latitude
        self.longitude = longitude
        self.value = value
    self.name = name