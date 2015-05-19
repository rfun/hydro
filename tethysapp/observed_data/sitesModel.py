from .model import SpatialSessionMaker, SitesTable
from sqlalchemy import func
from geoalchemy2 import Geometry
from geoalchemy2.functions import GenericFunction
import json


from pprint import pprint


def getSitesFromServices(xmin,ymin,xmax,ymax,services):
	
	session = SpatialSessionMaker()
	services = json.loads(services)
	sitesResult=[]
	sites = session.query(SitesTable,func.ST_X(SitesTable.geom).label('X'), func.ST_Y(SitesTable.geom).label('Y')).filter(
			SitesTable.geom.intersects( 
				func.ST_MakeEnvelope (
					xmin, ymin,
					xmax, ymax,
				 4326))
			).filter(
			SitesTable.servicecode.in_(services)
			).all()
	
	outputJSON = {'type': "FeatureCollection",'features' :[]}
	
	#Build Feature from site data
	i=1
	for site in sites:
		if 'cuahsi_1_1.asmx' in site.SitesTable.serviceURL:
			feature = {
				 "type": "Feature",
				 "geometry": {"type": "Point", "coordinates": [site.Y,site.X]},
				 "properties": {"name": site.SitesTable.sitename,"code": site.SitesTable.sitecode,"service": site.SitesTable.serviceURL, "id": i}
				}
			i=i+1
			outputJSON['features'].append(feature)
	
	return json.dumps(outputJSON)