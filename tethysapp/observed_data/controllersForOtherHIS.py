# module imports
from django.shortcuts import render
from .model import SessionMaker, StreamGage
from .lib.getvalues_python import getSitesinBBOX, getVarCode, getJSON, userMenu, getPlotJSON
import pprint, os
import json
import re
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
    print user
    username = str(user)
    folder_path = os.path.abspath(__file__)
    folder_dir = os.path.dirname(folder_path)
    directory = os.path.join(folder_dir, 'public', 'temp', username)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Create a session
    session = SessionMaker()

    # Query DB for gage objects
    gages = session.query(StreamGage).all()

    # Transform into GeoJSON format

#
    # Bounding Box parameters of the Dominican Republic
    xmin = -113.47
    xmax = -113.06
    ymin = 39.9
    ymax = 40.
		# Figure out keyword for hydroserver
    keyword = "Precipitation"
    inputStartDate = "2000-06-13"
    		#add one day to the input?
    inputEndDate = "2000-06-20"
    startDate = inputStartDate + "T00:00:00"
    endDate = inputEndDate + "T00:00:00"
    sites,services=getSitesinBBOX(xmin,ymin,xmax,ymax,keyword)	
    sitesPlotJSON, nameSites =getPlotJSON(sites)

#
    geometries = []

    sensors = []

    for gage in gages:
        gage_geometry = dict(type="Point",
        		coordinates=[gage.latitude, gage.longitude],
                             properties={"value":gage.name, "name":gage.value})
	geometries.append(gage_geometry)
	sensor = (gage.name,gage.value)
	sensors.append(sensor)

    #geojson_gages = {"type": "GeometryCollection",
                     #"geometries": geometries}
    
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
        'options': [('Stage','1'),('Flow','2')]}

    # Start Date Selection
    startdate_options = {'display_text': 'Start Date:',
               'name': 'selectStart',
               'autoclose': True,
               'format': 'yyyy-mm-dd',
               'start_date': '1/1/2014',
               'start_view': 'decade',
               'today_button': True}

    # End Date Selection
    enddate_options = {'display_text': 'End Date:',
               'name': 'selectEnd',
               'autoclose': True,
               'format': 'yyyy-mm-dd',
               'start_date': '1/1/2014',
               'start_view': 'decade',
               'today_button': True}
    
    # Input Submit Button
    submit_button = {'buttons': [
                             {'display_text': 'Get Data',
                              'name': 'clickSubmit',
                              'href':'/apps/observed-data/plot',
                              'type': 'submit'}
                             ]}

    # Pass variables to the template via the context dicitonary
    context = {'map_options': map_options,
		'site_options':site_options,
		'variable_options':variable_options, 
		'startdate_options':startdate_options, 		
		'enddate_options':enddate_options, 
		'submit_button':submit_button}

    return render(request, 'observed_data/map.html', context)





def plot(request):
    """
    Controller for the app values page.
    """
    user = request.user
    username = str(user)

    # Try BBOX
		# Dominican Republic BBOX
    xmin = -113.47
    xmax = -112.06
    ymin = 39.73
    ymax = 40.24
		# Figure out keyword for hydroserver
    keyword = "Precipitation"
    inputStartDate = "2000-06-13"
    		#add one day to the input?
    inputEndDate = "2000-06-20"
    startDate = inputStartDate + "T00:00:00"
    endDate = inputEndDate + "T00:00:00"
    
		#put selection list in sites, selection = 5


    # using python values script
    sites,services=getSitesinBBOX(xmin,ymin,xmax,ymax,keyword)	
    sitesJSON=getJSON(sites)
    varCodes=getVarCode(services,keyword)
    valuesJSON, dataValues, dateTimes =userMenu(sites,varCodes,startDate,endDate)
    

    # Creating the x y values for the plot
    amount = len(dataValues)
    i = 0
    plotlists = []

    for x in range(0,amount):
        observedValue=float(dataValues[i])
        splitdateTimes = re.split(r'[-,T,:]', dateTimes[i])

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
          'text': 'Yaque del Sur Watershed'
      },
    'xAxis': {
        'maxZoom': 1 * 24 * 3600000, # 1 day in milliseconds
        'type': 'datetime'
    },
    'yAxis': {
        'title': {
            'text': keyword + " " + '(ft)'
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
        'name': keyword,
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
                              'href':'/static/observed_data/temp/datavalues.csv',
                              'type': 'submit'}
                             ]}

    # Pass variables to the template via the context dicitonary
    context = {'line_plot_view':line_plot_view, 'data_button':data_button}

    return render(request, 'observed_data/plot.html', context)


