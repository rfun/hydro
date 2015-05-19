# module imports
import os, json, re, json
from django.shortcuts import render
from django.http import HttpResponse
from .model import SpatialSessionMaker, SitesTable
from .lib.getvalues_python import getSitesinBBOX, getVarCode, getJSON, getPlotJSON, getAllServices, getSitesFromServices,getVariablesFromSites, sendReq
from datetime import datetime

import sitesModel
import addSites2,test

def siteprocess(request):
    test.add()
    return HttpResponse("Yaay",status='200')

def home(request):
    """
    Controller for map page.
    """

    
    #Creating List of sevices
   
    allServices = getAllServices()
    allServices.sort(key=lambda tup: tup[0]) 
    # Configure the map
    map_options = {'height': '400px',
                   'width': '100%'
          }
    # Required Gizmos for Data Retrieval

    # Service Selection
    service_options = {'display_text': 'Theme:',
        'name': 'selectService',
        'multiple': True,
        'options': allServices}
    site_options = {'display_text': 'Site:',
        'name': 'selectSite',
        'multiple': False,
        'options': []}
    
    #TODO : WORK ON THIS ONE
    # Variable Selection
    variable_options = {'display_text': 'Variable:',
        'name': 'selectVariable',
        'multiple': False,
        'options': [('Stage','1')]}
    # When the hydroserver has flow ready, just add the flow option
        #'options': [('Stage','1'),('Flow','2')]}

    # Start Date Selection
    startdate_options = {'display_text': 'Start Date:',
               'name': 'selectStart',
               'autoclose': True,
               'format': 'yyyy-mm-dd',
               'start_date': '1/1/1900',
               'initial': '2010-01-01',
               'start_view': 'decade',
               'today_button': True}
    
    # End Date Selection
    enddate_options = {'display_text': 'End Date:',
               'name': 'selectEnd',
               'autoclose': True,
               'format': 'yyyy-mm-dd',
               'start_date': '1/1/1900',
               'initial':'2015-03-29',
               'start_view': 'decade',
               'today_button': True}
               
    # Pass variables to the template via the context dicitonary
    context = {'map_options': map_options,
        'service_options':service_options,
        'site_options':site_options,
        'variable_options':variable_options, 
        'startdate_options':startdate_options,      
        'enddate_options':enddate_options}


    return render(request, 'observed_data/home.html', context)



def homeOld(request):
    """
    Controller for map page.
    """

    # Create workspace for the user
    user = request.user
    username = str(user)
    folder_path = os.path.abspath(__file__)
    folder_dir = os.path.dirname(folder_path)
    directory = os.path.join(folder_dir, 'public', 'temp', username)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    #Creating List of sevices
   
    allServices = getAllServices()
    # Configure the map
    map_options = {'height': '400px',
                   'width': '100%'
		  }
    # Required Gizmos for Data Retrieval

    # Service Selection
    service_options = {'display_text': 'Theme:',
        'name': 'selectService',
        'multiple': True,
        'options': allServices}

    
    variable_options = {'display_text': 'Variable:',
        'name': 'selectVariable',
        'multiple': False,
        'options': [('Stage','1')]}
    # When the hydroserver has flow ready, just add the flow option
        #'options': [('Stage','1'),('Flow','2')]}

    # Start Date Selection
    startdate_options = {'display_text': 'Start Date:',
               'name': 'selectStart',
               'autoclose': True,
               'format': 'yyyy-mm-dd',
               'start_date': '1/1/1900',
               'initial': '2010-01-01',
               'start_view': 'decade',
               'today_button': True}
    
    # End Date Selection
    enddate_options = {'display_text': 'End Date:',
               'name': 'selectEnd',
               'autoclose': True,
               'format': 'yyyy-mm-dd',
               'start_date': '1/1/1900',
               'initial':'2015-03-29',
               'start_view': 'decade',
               'today_button': True}
    # Pass variables to the template via the context dicitonary
    context = {'map_options': map_options,
        'service_options':service_options}

    return render(request, 'observed_data/home.html', context)




def inputsubmit(request):
    """
    The form from the map page pushes input variables to the plot page
    """

    params = request.POST
    startDate = params['selectStart']
    endDate = params['selectEnd']
    variable = params['selectVariable']
    siteID = params['siteCode']
    service = params['service']

    return startDate, endDate, variable, siteID, service




def plot(request):
    """
    Controller for the plot page
    """
    
    # Get input variables from form on map page
    mapStartDate, mapEndDate, mapVariable, mapSiteID, service= inputsubmit(request)

    # Declaring the user
    user = request.user
    username = str(user)

    # Input variables given from the map page
    siteID = mapSiteID
    inputStartDate = mapStartDate
    inputEndDate = mapEndDate
    startDate = inputStartDate + "T00:00:00"
    endDate = inputEndDate + "T23:59:59"
    variableCode = mapVariable
    
    valuesJSON, dataValues, dateTimes = sendReq(siteID,variableCode,startDate,endDate,service)

#  return HttpResponse(json, content_type="application/json",status='200')


    # Creating the x y values for the plot
    amount = len(dataValues)
    i = 0
    plotlists = []

    for x in range(0,amount):
        observedValue=float(dataValues[i])
        splitdateTimes = re.split(r'[-,T,:,\s]', dateTimes[i])


        dateYear = int(splitdateTimes[0])
        dateMonth = int(splitdateTimes[1])
        dateDay = int(splitdateTimes[2])
        dateHour = int(splitdateTimes[3])
        dateMinute = int(splitdateTimes[4])
        dateSecond = int(splitdateTimes[5])
        
        plotlist = [datetime(dateYear,dateMonth,dateDay,dateHour,dateMinute,dateSecond),observedValue]
        plotlists.append(plotlist)
        i += 1

    # write the datavalues into a .csv file
    module_path = os.path.abspath(__file__)
    module_dir = os.path.dirname(module_path)
    csv_path = os.path.join(module_dir, 'public', 'temp', username, 'datavalues.csv')
    list = json.loads(valuesJSON)
    with open(csv_path, 'w') as f:
        f.write('DataValues'+","+'DateTime'+"\n")
        for pair in list:
	    f.write(','.join(pair)+"\n")

    # Plot View Options
    highcharts_object = {
    'chart': {
        'type': 'line',
        'zoomType': 'x'
    },
    'title': {
        'text': 'Hydrologic Data Observations'
    },
      'subtitle': {
          'text': mapSiteID
      },
    'xAxis': {
        'maxZoom': 1 * 24 * 3600000, # 1 day in milliseconds
        'type': 'datetime'
    },
    'yAxis': {
        'title': {
            'text': mapVariable #TODO : ADD UNITS HERE
        },
        'min': 0
    },
    'legend': {
        'layout': 'vertical',
        'align': 'right',
        'verticalAlign': 'top',
        'x': -350,
        'y': 125,
        'floating': True,
        'borderWidth': 1,
        'backgroundColor': '#FFFFFF'
    },
    'series': [{
        'name': mapVariable,
        'data': plotlists
        }]
    }
    
    line_plot_view = {'highcharts_object': highcharts_object,
                  'width': '500px',
                  'height': '500px'}


   # Download the data values .csv file
    data_button = {'buttons': [
                             {'display_text': 'Download Data',
                              'name': 'clickData',
                              'href':'/static/observed_data/temp/'+ username+'/datavalues.csv',
                              'type': 'submit'}
                             ]}

    # Pass variables to the template via the context dicitonary
    context = {'line_plot_view':line_plot_view, 'data_button':data_button}

    return render(request, 'observed_data/plot.html', context)

def displaySites(request):

    params = request.POST
    services = params.getlist('selectService')
    bbox = params.get('bbox').split(',')
    # For each service we will build a list of sites. 
    #First task is to get the sites to show up on the map. Second task will be to populate a drop down with all these sites
    
    # Bounding Box parameters from the URL
    xmin = float(bbox[1])
    xmax = float(bbox[3])
    ymin = float(bbox[0])
    ymax = float(bbox[2])
    
    sites=getSitesFromServices(xmin,ymin,xmax,ymax,','.join(services))
    sitesJSON = getJSON(sites)
    sitesPlotJSON, nameSites =getPlotJSON(sites)
   
    # Required Gizmos for Data Retrieval

    # Site Selection
    site_options = {'display_text': 'Site:',
        'name': 'selectSite',

        'multiple': False,
        'options': nameSites}

    #TODO : WORK ON THIS ONE
    # Variable Selection
    variable_options = {'display_text': 'Variable:',
        'name': 'selectVariable',
        'multiple': False,
        'options': [('Stage','1')]}
    # When the hydroserver has flow ready, just add the flow option
        #'options': [('Stage','1'),('Flow','2')]}

    # Start Date Selection
    startdate_options = {'display_text': 'Start Date:',
               'name': 'selectStart',
               'autoclose': True,
               'format': 'yyyy-mm-dd',
               'start_date': '1/1/1900',
               'initial': '2010-01-01',
               'start_view': 'decade',
               'today_button': True}
    
    # End Date Selection
    enddate_options = {'display_text': 'End Date:',
               'name': 'selectEnd',
               'autoclose': True,
               'format': 'yyyy-mm-dd',
               'start_date': '1/1/1900',
               'initial':'2015-03-29',
               'start_view': 'decade',
               'today_button': True}

    #Building toggle elements
    
    toggle_switch2 = {'display_text': 'Map update on Pan','name': 'panUpdate', 'initial': True}

    # Pass variables to the template via the context dicitonary
    context = {
        'sitesJSON' : sitesJSON,
        'toggle_switch2' : toggle_switch2,
        'services' : ','.join(services),
        'site_options':site_options,
        'variable_options':variable_options, 
        'startdate_options':startdate_options,      
        'enddate_options':enddate_options}

    return render(request, 'observed_data/map.html', context)

def getSites(request):
    params = request.POST
    bbox = params.get('bbox').split(',')
    services = params.get('services')
    #print services
     # Bounding Box parameters from the URL
    xmin = float(bbox[1])
    xmax = float(bbox[3])
    ymin = float(bbox[0])
    ymax = float(bbox[2])
    
    sites=sitesModel.getSitesFromServices(xmin,ymin,xmax,ymax,services)
    
    return HttpResponse(sites, content_type="application/json",status='200')


def getVariables(request):
    params = request.POST
    siteCode = params.get('siteCode')
    service = params.get('siteUrl')

    return HttpResponse(getVariablesFromSites(siteCode,service), content_type="application/json",status='200')