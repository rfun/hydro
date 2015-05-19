# Put your persistent store initializer functions in here

from .model import spatial_engine, SpatialSessionMaker, SpatialBase, SitesTable

def init_sites_db(first_time):
    # Create tables
    SpatialBase.metadata.create_all(spatial_engine)

