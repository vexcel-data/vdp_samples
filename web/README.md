## Introduction

This folder contains a set of static web pages that each serve a different purpose. This will serve as a table of contents for each of the folders and the purpose of the associated web page.


## Authentication Demo

This demo page will show you how to utilized both federated and regular authentication using our API. Simply enter your username and hit the next button to begin.

A live version can also be viewed here: https://vexceldemoappsandservices.azurewebsites.net/pages/AuthenticationDemoApp.html

## Coverage Viewer

This demo page will show you how to use our services to query for Ortho, Discrete, DSM, or DTM coverage at a point, polygon, or from an entire layer. 

To use this page:

	1. Log in with your credentials - once logged in the layer list drop-down will populate
	2. Enter a lat/long or WKT 
	3. Select the coverage type and imagery layer you are interested from the drop-downs
	4. Hit the "Get Coverage" button
	5. The map will then load to the location you entered and the information panel on the right will populate with the available AOIs/coverage at that location

A live version can also be viewed here: http://gicapps.azurewebsites.net/static/VexcelCoverage.htm

## Extract Ortho Demo

This demo page will show you how to find ortho coverage for an area, view it as an X/Y/Z layer and grab chunks of the ortho imagery for a given AOI and use a static map.

To use this page:

	1. Log in with your credentials
	2. Enter a lat/long and click "Search and Refresh Coverage" for the right panel to populate with available orthos
		a. You can also pan the map around and click the "Refresh coverage at map center" button to populate the right panel
	3. Click on one of the available AOIs on the right panel for the map to populate with the ortho imagery at that location

A live version can also be viewed here: http://gicapps.azurewebsites.net/static/ExtractOrthoDemo.htm

##Time Slider

This demo page will show you how to query for discrete image metadata at a given coordinate. It will also display each discrete image across all orientations.

To use this page:

	1. Enter your credentials
	2. You may use the filters to narrow down your searches as neccessary
	3. Enter a lat/long to search for and click "Get Metadata"
	4. Metadata will populate in the right panel and the discrete images will load in the left
	5. Use the slider above the imagery to scroll through all the available discrete images that are available in that area

A live version can also be viewed here: http://gicapps.azurewebsites.net/static/VexcelAPI_TimeSlider.htm


##Property Info API Demo

This demo will show you how to utilize the API endpoint for querying property data and retrieving building footprints. This demo also utilizes a preview version of our upcoming map control.

To use this page:

	1. Login with your credentials
	2. Once logged in the map control will load
	3. You may search for a lat/long or pan/zoom on the map control. 
	4. Once in a location of interest, you may click on a building inside the map (you must be in the top down view)
	5. If available, a building footprint will then draw around the building and property information will populate in the left panel
	6. You may also click additional locations after this to view additional property information

A live version can also be viewed here: https://gicapps.azurewebsites.net/static/PropertyInfoDemo.htm

##Map Control

This folder contains projects that utilize our map control. The map control is currently in preview and these will be periodically updated as the initial release draws closer.


