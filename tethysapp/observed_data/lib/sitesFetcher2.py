import math,random,os
from urlparse import urlparse
from threading import Thread
import httplib, sys
from Queue import Queue
import urllib2,urllib, json
from xml.dom import minidom
import xml.etree.ElementTree as ET
import getvalues_python as gv
from suds.client import Client

import suds

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

concurrent = 200

def doWork():
	while True:
		option = q.get()
		result = makeCentralReq(option)
		doSomethingWithResult(option,result)
		q.task_done()

def makeCentralReq(option):
	
	print "Processing: " + option

	option = 'http://hiscentral.cuahsi.org/webservices/hiscentral.asmx?WSDL'
	client = Client(option)
	print client

	# try:
	# 	result = client.service.GetSitesObject('','')
	# except suds.WebFault as detail:
	# 	print "Something Wrong happened"
	# 	return "ERROR WITH : " + option
	# except Exception, e:
	# 	print e
	# 	print "something wrong also happened here"
	# 	return "ERROR WITH : " + option
	# return result


def makeCentralReqURL(option):
	print option
	url = option.replace("?WSDL",'')
	data = """
	<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
	<soap:Body>
	<GetSiteInfoObject xmlns="http://www.cuahsi.org/his/1.1/ws/">
	  <site></tns:site>
	  <authToken></tns:authToken>
	</GetSiteInfoObject>
	</soap:Body>
	</soap:Envelope>"""

	headers = {
		'Content-Type': 'text/xml; charset=utf-8',
		'SOAPAction' : "http://www.cuahsi.org/his/1.1/ws/GetSiteInfoObject"
 	}
	req = urllib2.Request(url, data, headers)
	try:
		response = urllib2.urlopen(req)
		the_page = response.read()
	except urllib2.HTTPError, error:
		print "Something Wrong happened"
		print error
	#return the_page
	return the_page
	


def doSomethingWithResult(result):
	fileName = str(random.random()*10000)
	filePath = os.path.join(os.path.dirname(__file__),"test2/"+fileName+".xml")
	fo = open(filePath, "wb")
	fo.write(result);
	# Close opend file
	fo.close()



#First lets generate the list of URL's 
def generateOptions():
	return gv.getAllServicesURL()


for option in generateOptions():
	print option
	#doSomethingWithResult(result)



# for option in options:
# 	print str(int(option['xmax']+option['xmin']+option['ymax']+option['ymin']+random.random()*1000000000))


# q = Queue(concurrent * 2)
# for i in range(concurrent):
#     t = Thread(target=doWork)
#     t.daemon = True
#     t.start()
# try:
#     for option in generateOptions():
#         q.put(option)
#     q.join()
# except KeyboardInterrupt:
#     sys.exit(1)

