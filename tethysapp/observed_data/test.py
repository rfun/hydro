import addSites,os,time
from .model import SitesTable, SpatialSessionMaker
import ulmo

def add2():
	count =0
	for fileName in addSites.files():
		session = SpatialSessionMaker()
		path = os.path.join(os.path.dirname(__file__),'lib','test')
		filePath = path + '/' + fileName
		result = addSites.readSites(filePath)
		addSites.doSomethingWithResult(result,session)
		session.close()
		count += len(result)
	print count

	
def add():
	wsdl_url = 'http://drought.usu.edu/ncdc_l1/cuahsi_1_1.asmx?WSDL'
	site_code = 'UCRB_NCDC:USC00427064'

	print ulmo.cuahsi.wof.get_site_info(wsdl_url, site_code, suds_cache=('default', ))
