from sqlalchemy import func
from .model import SitesTable, SpatialSessionMaker
import os
from xml.dom import minidom
from threading import Thread
import xml.etree.ElementTree as ET
import logging

# LOG_FILENAME = 'logging.txt'
# logging.basicConfig(filename=LOG_FILENAME)

# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)



def getVal(source,element):
	if (source.getElementsByTagName(element)[0].firstChild is None):
		return ""
	else:
		return source.getElementsByTagName(element)[0].firstChild.nodeValue

def files():
	path = os.path.join(os.path.dirname(__file__),'lib','test')
	return os.listdir(path)
	    	

def doWork():
    while True:
        option = q.get()
        print "Processing : " + option
        result = readSites(option)
        doSomethingWithResult(result)
        q.task_done()

def readSites(filePath):
	print "Processing : " + filePath
	inputFile = open(filePath, "r")
	content = inputFile.read()
	xml = minidom.parseString(content)
	sites = xml.getElementsByTagName('Site')
	return sites


def doSomethingWithResult(sites,session):
	
	i=0
	for site in sites:
		i+=1
		site = SitesTable(
			latitude = getVal(site,'Latitude'),
			longitude = getVal(site,'Longitude'),
			name = getVal(site,'SiteName'),
			code = getVal(site,'SiteCode'),
			servCode = getVal(site,'servCode'),
			servURL= getVal(site,'servURL'))
		session.add(site)
		if(i>1000):
			session.commit()
			i=0
			

	session.commit()



