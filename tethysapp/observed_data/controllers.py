# module imports
import os, json, re, json
from django.shortcuts import render
from .model import SessionMaker, StreamGage
from .lib.getvalues_python import getSitesinBBOX, getVarCode, getJSON, userMenu, getPlotJSON
from datetime import datetime




def home(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'observed_data/home.html', context)




def map(request):
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
    
  # Creating List of sites for the map

    # Bounding Box parameters of the Dominican Republic
    xmin = -71.30
    xmax = -71.10
    ymin = 18.70
    ymax = 19.04
    # keyword found on his-central where you map the variable
    keyword = "gage height, stream"
    sites,services=getSitesinBBOX(xmin,ymin,xmax,ymax,keyword)
    sitesPlotJSON, nameSites =getPlotJSON(sites)

    geojson_gages = sitesPlotJSON

    # Configure the map
    map_options = {'height': '400px',
                   'width': '100%',
                   'input_overlays': geojson_gages,
		  }

  # Required Gizmos for Data Retrieval

    # Site Selection
    site_options = {'display_text': 'Site:',
        'name': 'selectSite',
        'multiple': False,
        'options': nameSites}

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
               'start_date': '1/1/2000',
               'initial': '2015-02-15',
               'start_view': 'decade',
               'today_button': True}
    
    # End Date Selection
    enddate_options = {'display_text': 'End Date:',
               'name': 'selectEnd',
               'autoclose': True,
               'format': 'yyyy-mm-dd',
               'start_date': '1/1/2014',
               'initial':'2015-03-29',
               'start_view': 'decade',
               'today_button': True}

    # Pass variables to the template via the context dicitonary
    context = {'map_options': map_options,
		'site_options':site_options,
		'variable_options':variable_options, 
		'startdate_options':startdate_options, 		
		'enddate_options':enddate_options}

    return render(request, 'observed_data/map.html', context)




def inputsubmit(request):
    """
    The form from the map page pushes input variables to the plot page
    """

    params = request.POST
    startDate = params['selectStart']
    endDate = params['selectEnd']
    siteVariable = int(params['selectVariable'])
    siteID = int(params['selectSite'])

    if siteVariable == 1:
        siteVariable = "Stage"
        mapKeyword = "gage height, stream"
        variableCode = "yaquedelsur:STAGE"
        units = "ft"
    else:
        if siteVariable ==2:
            siteVariable = "Flow"
            mapKeyword = "Dishcharge, stream"
            variableCode = "yaquedelsur:FLOW"
            units = "cfs"

    return startDate, endDate, siteVariable, mapKeyword, siteID, variableCode, units




def plot(request):
    """
    Controller for the plot page
    """
    
    # Get input variables from form on map page
    mapStartDate, mapEndDate, mapVariable, mapKeyword, mapSiteID, variableCode, units= inputsubmit(request)

    # Declaring the user
    user = request.user
    username = str(user)

    # Bounding box coordinates for the Dominican Republic
    xmin = -71.30
    xmax = -71.10
    ymin = 18.70
    ymax = 19.04

    # Input variables given from the map page
    siteID = mapSiteID
    keyword = mapKeyword
    inputStartDate = mapStartDate
    inputEndDate = mapEndDate
    startDate = inputStartDate + "T00:00:00"
    endDate = inputEndDate + "T23:59:59"
    variableCode = variableCode
    units = units

    # Using getvalues_python.py
    sites,services=getSitesinBBOX(xmin,ymin,xmax,ymax,keyword)
    sitesJSON=getJSON(sites)
    sitesPlotJSON, nameSites =getPlotJSON(sites)
    valuesJSON, dataValues, dateTimes =userMenu(sites,variableCode,startDate,endDate,siteID)

    # Finding the selected site name for the plot subtitle
    rows = nameSites
    res_list = [x[0] for x in rows]
    
    newSiteID = res_list[mapSiteID-1]

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
        'type': 'spline',
        'zoomType': 'x'
    },
    'title': {
        'text': 'Hydrologic Data Observations'
    },
      'subtitle': {
          'text': newSiteID
      },
    'xAxis': {
        'maxZoom': 1 * 24 * 3600000, # 1 day in milliseconds
        'type': 'datetime'
    },
    'yAxis': {
        'title': {
            'text': mapVariable + ' (' + units + ')'
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


