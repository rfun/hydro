import math,random,os
from urlparse import urlparse
from threading import Thread
import httplib, sys
from Queue import Queue
import urllib2,urllib, json
from xml.dom import minidom
import xml.etree.ElementTree as ET

concurrent = 200

def doWork():
    while True:
        option = q.get()
        result = makeCentralReq('GetSitesInBox2',option)
        doSomethingWithResult(option,result)
        q.task_done()

def makeCentralReq(endpoint,options):
    url = 'http://hiscentral.cuahsi.org/webservices/hiscentral.asmx/'+endpoint
    data = urllib.urlencode(options)
    req = urllib2.Request(url, data)
    try:
        response = urllib2.urlopen(req)
        the_page = response.read()
    except urllib2.HTTPError, error:
        print error.read()
    #return the_page
    return the_page


def doSomethingWithResult(options,result):
	fileName = str(int(option['xmax']+option['xmin']+option['ymax']+option['ymin']+random.random()*1000000000))
	filePath = os.path.join(os.path.dirname(__file__),"test/"+fileName+".xml")
	fo = open(filePath, "wb")
	fo.write(result);
	# Close opend file
	fo.close()



#First lets generate the list of URL's 
def generateOptions():
	minX = -180.0
	maxX = 180.0
	minY = -90.0
	maxY = 90.0
	sliceSize = 10

	# We will traverse all the vertical at each horizontal Slice

	horizontalSlices = int(math.ceil((maxX-minX)/sliceSize))
	verticalSlices = int(math.ceil((maxY-minY)/sliceSize))

	x1 = minX
	options = []
	for i in range(horizontalSlices):
		x1 = minX + sliceSize*i
		x2 = min((x1+sliceSize),maxX)
		for j in range(verticalSlices):
			y1 = minY + sliceSize*j
			y2 = min((y1+sliceSize),maxY)
			option = {'xmin' : x1,
	          'xmax' : x2,
	          'ymin' : y1,
	          'ymax' : y2,
	          'conceptKeyword' : '',
	            'networkIDs':''}
			options.append(option)
	
	print len(options)
	return options

# options = generateOptions()

# for option in options:
# 	print str(int(option['xmax']+option['xmin']+option['ymax']+option['ymin']+random.random()*1000000000))


q = Queue(concurrent * 2)
for i in range(concurrent):
    t = Thread(target=doWork)
    t.daemon = True
    t.start()
try:
    for option in generateOptions():
        q.put(option)
    q.join()
except KeyboardInterrupt:
    sys.exit(1)

