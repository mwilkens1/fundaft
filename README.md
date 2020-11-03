# Property valuation webapp Daft.ie
Live version: [fundaft.herokuapps.com](http://fundaft.herokuapp.com/)

### Table of Contents

1. [Installation](#installation)
2. [Project Motivation](#motivation)
3. [File Descriptions](#files)
4. [Results](#results)
5. [Reflection](#reflection)
6. [Licensing, Authors, and Acknowledgements](#licensing)

## Installation <a name="installation"></a>

There should be no necessary libraries to run the code here beyond the Anaconda distribution of Python.  The code should run with no issues using Python version 3. All requirements are listed in the file 'requirements.txt'.

## Project Motivation<a name="motivation"></a>
For most people, buying a house is something that you do only once or a few times in a lifetime. In today's overheated real estate markets, prospective buyers need to take quick decisions on whether to make an offer for a property and with which amount. 

This requires an expertise usually reserved for real estate experts: estimating a property's value. This project builds a Python Flask web app that will assist prospective property buyers by providing a property valuation for a given ad and general information about the Dublin housing market. 

More specifically, the webapp can be accessed on [fundaft.herokuapps.com](http://fundaft.herokuapp.com/) and includes the following:
- a machine learning model that predicts the asking price of a property listed on Ireland's main property advertising website [Daft.ie](https://www.daft.ie/). It is trained on Daft.ie data as well as [openstreetmap](https://www.openstreetmap.org/) data. Users of the web app can enter a link to an ad and immediately get a valuation of the property.
- Dashboard style information about the Dublin property market

The data used for this project is data from Daft.ie for Dublin city and has been scraped since May 2019. The data is enriched with openstreetmap data.

## File Descriptions <a name="files"></a>

### Data collection
* scrape_daft.py: script that includes classes for scraping daft.ie. It is a scrapy spider that goes scrapes each ad on each page of the properties listed for Dublin city for a given time interval.
* openstreetmap_api.py: script that fetches the amenities (schools, pubs, etc) in Dublin from the openstreetmaps API. 
* electoral_divisions.py: script for transforming a shapefile for Dublin. It selects only the relevant areas. This is used to create a map on the web app. Shapefile is from the [Central Statistics Office](https://www.cso.ie/en/census/census2011boundaryfiles/)
* add_data.py: script for matching the scraped Daft.ie ads to the openstreetmap data. Amenities in a 0.5km radius are counted for a given property. Also, the electoral divisions are added to the data. 
* update_data.py: ETL pipeline that calls the spider and enriches the data with the openstreetmap data and the electoral divisions using add_data.py. The output is a dataset.

### Data
* data/df_ads_mapdata.csv: the main datafile containing ads scraped from Daft.ie since May 2019 as well as variables on the number of amenities surrounding a property. Finally, the geographic areas (electoral boundaries) are included.
* data/osm_data.p: pickled file of the openstreetmap data collected with openstreetmap_api.py
* data/boundaries: folder including the shapefiles as well as the transformed shapefile (ED.geojson / ED.p)

### Machine learning
* MLpipeline.py: class MLpipeline includes methods for building a machine learning pipeline for a given estimator. It also allows evaluation of the model and storing the model locally. 
* train_model.ipynb: jupyter notebook to train the model used to predict the asking price. This notebook contains exploratory data analysis, model training and storing the final model. 
* pricepredictor.py: class that predicts a price for a given property's ad URL
* model: folder with stored model

### Web app files
* templates / index.html: webpage for the web app.
* static: folder with some images used on the page
* app.py: Runs the app via Flask
* requirements.txt: lists all packages required to run the app. 
* runtime.txt: shows python version used

## Results<a name="results"></a>
The webapp is available on [fundaft.herokuapps.com](http://fundaft.herokuapp.com/). It can also be run locally after downloading the files. This also allows the updating of the data as well by running update_data.py. 

## Reflection<a name="reflection"></a>
The webapp provides useful information for those looking to buy a house in Dublin. Not only does it give a general overview of the housing market, it also give an estimated value of a listed property. The accuracy of the prediciton is rather high, given that it not based on characterisics of the property that cannot easily be captured in data, such as the looks of a property. 

Future development of the project could focus on: 
* Rather than having a URL to an ad as an input for the prediction, a template could be created where users input characteristics of a property, such as its locations, number of bedrooms, etc. This would allow prospective sellers to use the app as well to get an idea on how much their asking price should be.
* Natural Language Processing could be applied on the general description of the property to include non-standard information that is relevant for determining the value of the property. For example, the discription could mention the property was recently renovated. 
* Image learning: each ad includes a series of photos of the property. A machine learning model could be developed that extracts features from these images to predict the price of the property. 

## Licensing, Authors, Acknowledgements<a name="licensing"></a>

Feel free to use the code. 
