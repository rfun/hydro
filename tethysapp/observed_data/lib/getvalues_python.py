##################HIS to CIWATER################
## Version 0.3
## Developed by : Rohit Khattar
## Modified by : Matt Saguibo
## Reupdated again : Rohit Khattar
## BYU
## Note : 
##############################################


#Import Required Libraries (These are included by default with python, hence no additional setups required)
import urllib2,urllib, json
from xml.dom import minidom
import xml.etree.ElementTree as ET

#Extra Lib
from suds.client import Client
import suds
from suds.xsd.doctor import Import, ImportDoctor
# Helper to get the string value of an element
import logging
# logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)

import ulmo

def getVal(source,element):
    if (source.getElementsByTagName(element)[0].firstChild is None):
        return ""
    else:
        return source.getElementsByTagName(element)[0].firstChild.nodeValue

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
    return minidom.parseString(the_page)

def makeServiceReq(service,endpoint,options):
    url = service.replace("?WSDL",'/'+endpoint)
    data = urllib.urlencode(options)
    req = urllib2.Request(url, data)
    try:
        response = urllib2.urlopen(req)
        the_page = response.read()
    except urllib2.HTTPError, error:
        print error.read()

    #return the_page
    return ET.fromstring(the_page)

def getSiteInfo(service,endpoint,siteCode):
    imp = Import('http://schemas.xmlsoap.org/soap/encoding/')
    imp.filter.add('http://www.cuahsi.org/his/1.0/ws/')
    imp.filter.add('http://www.cuahsi.org/his/1.0/ws/AbstractTypes')
    imp.filter.add('http://www.cuahsi.org/his/1.1/ws/')
    imp.filter.add('http://www.cuahsi.org/waterML/1.1/')
    imp.filter.add('http://www.cuahsi.org/his/1.1/ws/AbstractTypes')
    
    doctor = ImportDoctor(imp)
    client = Client(service, doctor=doctor)
    print service,siteCode
    try:
        result = client.service.GetSiteInfo(siteCode,'').encode('utf8')
    except suds.WebFault as detail:
        # Error Happened. 
        # Mark this service as faulty!
        return False
    except Exception, e:
        return False
    return ET.fromstring(result)


def getSitesinBBOX(xmin,ymin,xmax,ymax,keyword,networks=""):

    #Sending out a POST request to get data from HIS Central
   
    options = {'xmin' : xmin,
          'xmax' : xmax,
          'ymin' : ymin,
          'ymax' : ymax,
          'conceptKeyword' : keyword,
            'networkIDs':networks}
    xmldoc = makeCentralReq('GetSitesInBox2',options)
 
    sitelist = xmldoc.getElementsByTagName('Site') 
    #Prepare List of sites
    sites=[]
    services = set()

    # SomeSites Do Not have a name. Hence the name will be a combination of the siteName is present and siteCode

    for site in sitelist:
        serviceURL = site.getElementsByTagName('servURL')[0].firstChild.nodeValue
        services.add(serviceURL)
        if(site.getElementsByTagName('SiteName')[0].firstChild is None):
            siteName = site.getElementsByTagName('SiteCode')[0].firstChild.nodeValue
        else:
            siteName = site.getElementsByTagName('SiteName')[0].firstChild.nodeValue
        newSite = {'sitename': siteName,
                   'SiteCode': site.getElementsByTagName('SiteCode')[0].firstChild.nodeValue,
                   'servURL': serviceURL,
                   'Latitude': site.getElementsByTagName('Latitude')[0].firstChild.nodeValue,
                   'Longitude': site.getElementsByTagName('Longitude')[0].firstChild.nodeValue
                                 }
        sites.append(newSite)
    
    return sites,services



def getTSJSON(values,ts):
    return json.dumps(zip(values,ts))
    


def sendReq(siteCode,varCode,startDate,endDate,service):
    #Define Parameters for data retrieval
    
    data = ulmo.cuahsi.wof.get_values(service, siteCode, varCode, start=startDate, end=endDate, suds_cache=('default', ))
   
    values,ts = parseData(data)
    outputJSON = getTSJSON(values,ts)
    return outputJSON, values, ts

def parseData(getvalues_data):


    values = []
    timeStamps = []

    for value in getvalues_data['values']:
        if value['value'] != '-9999':
            values.append("%.2f" % (float(value['value'])))
            timeStamps.append(str(value['datetime']))

    return values, timeStamps




#Function To process each site and display the list of sites to fetch data

def userMenu(sites,variableCode,startDate,endDate,siteID):
    selection = siteID
    site = sites[selection-1]
    varCode = variableCode
    valuesJSON, values, ts = sendReq(site,varCode,startDate,endDate)
    return valuesJSON, values, ts



def getJSON(sites):

    outputJSON = {'type': "FeatureCollection",'features' :[]}
    #Build Feature from site data
    i=1
    for site in sites:
        feature = {
             "type": "Feature",
             "geometry": {"type": "Point", "coordinates": [float(site['Latitude']), float(site['Longitude'])]},
             "properties": {"name": site['sitename'],"code": site['SiteCode'],"service": site['servURL'], "id": i}
            }
        i=i+1
        outputJSON['features'].append(feature)
    
    return json.dumps(outputJSON)




# Function to create a list of sites suitable for the editable map
def getPlotJSON(sites):

    outputPlotJSON = {"type": "GeometryCollection",'geometries':[]}
    #Build Feature from site data
    nameSites= []
    
    i = 1
    for site in sites:
        geometries = dict(type = "Point", coordinates = [site['Latitude'], site['Longitude']], properties={"name": i, "value":site['sitename']})
        outputPlotJSON['geometries'].append(geometries)
        nameSite = (site['sitename'],i)
        nameSites.append(nameSite)
        i += 1

    return outputPlotJSON, nameSites

# This code could be used for future use in HIS-Central

def getVariablefromXML(xml,keyword):
    #XML Parsing is not working due to some namespace issues.
    #Doing a simple string search and then from there will extract the code
    pos1 = xml.find('<variableName>'+keyword)
    if pos1==-1:
        pos1= xml.find('&lt;variableName&gt;'+keyword)
    if not pos1 ==-1:
        pos2 = xml.rfind('variableCode vocabulary="', 0, pos1)
        pos3 = xml.find('"', pos2+26)
        pos4 = xml.find('&gt;', pos2)
        pos5 = xml.find('&lt;/variableCode&gt;',pos4)
        return xml[pos2+25:pos3]+":"+xml[pos4+4:pos5]
    else:
        return ""
    
    #To ADD Support for multiple precipitation values
    #TODO : Also change this to mindom module instead, use the object url to get the data

def getVarCode(services,keyword):
    #This function queries the server for the Variable code for our keyword
    varCodes={}
    for service in services:
        service1=service.replace("?WSDL",'/GetVariables?authToken=""')
        req = urllib2.Request(service1)
        try:
            response = urllib2.urlopen(req)
            the_page = response.read()
            var = getVariablefromXML(the_page,keyword)
            if not (var == "" or var is None):

                varCodes[service]=var
        except urllib2.HTTPError, error:
            print error.read() 
    return varCodes

# Will fetch all available services on HIS Central
def getAllServices():
    xmin = -180
    xmax = 180
    ymin = -90
    ymax = 90
    options = {'xmin' : xmin,
          'xmax' : xmax,
          'ymin' : ymin,
          'ymax' : ymax}
    xmldoc = makeCentralReq('GetServicesInBox2',options)

    services = xmldoc.getElementsByTagName('ServiceInfo') 
    titles=[]
    for service in services:
        titles.append((getVal(service,'Title'),getVal(service,'NetworkName')))
    return titles

# Will fetch all available services on HIS Central
def getAllServicesURL():
    xmin = -180
    xmax = 180
    ymin = -90
    ymax = 90
    options = {'xmin' : xmin,
          'xmax' : xmax,
          'ymin' : ymin,
          'ymax' : ymax}
    xmldoc = makeCentralReq('GetServicesInBox2',options)

    services = xmldoc.getElementsByTagName('ServiceInfo') 
    titles=[]
    for service in services:
        titles.append(getVal(service,'servURL'))
    return titles

#Get Sites only with the listed services
def getSitesFromServices(xmin,ymin,xmax,ymax,services):
    sites,services = getSitesinBBOX(xmin,ymin,xmax,ymax,"",services)
    #For each of the services, get the variables associated.
    # for site in sites:
    #     print site['servURL']
    # print services
    return sites
    
def getVariablesFromSites(siteCode,service):
    
    variableFinalList = []
    variables = {}
    try:
        siteInfo = ulmo.cuahsi.wof.get_site_info(service, siteCode, suds_cache=('default', ))
        for series in siteInfo['series']:
            variable = siteInfo['series'][series]['variable']
            print variable
            if "name" in variable:
                varName = variable['name']
            else:
                varName = "No Name"
            if "data_type" in variable:
                dt = variable['data_type']
                finalName = varName + " (" + dt + ")"
            else:
                dt = ""
                finalName = varName
            varCode = variable['vocabulary']+":"+variable['code']
            if(not (variables.has_key(varCode))):
                variables[varCode]={'varCode':varCode,'varName':finalName}
    except Exception,e:
        print "ERROR",e
        
    for var in variables:
        variableFinalList.append(variables[var])

    #return variableFinalList
    return json.dumps(variableFinalList);
