# Daft.ie webscraping
Webscraping [daft.ie](http://www.daft.ie), the well-known property listing website of Ireland. Using the folium package, the plots below show [heatmaps of the price]() (left) and the [price per square meter]() (right).

<img src="images/heatmap_price.png" width="400"><img src="images/heatmap_pricesqm.png" width="400">

The average price of a detached house or an apartment with more than 3 bedrooms is well over a million. 1 bedroom apartments are close to half a million on average which is more than the average for 2 bedroom apartments.

<img src="images/prices_property_type.png" width="600">

The data is matched to data from [openstreetmap.org](http://www.openstreetmap.org) on the basis of latitude and longitude. The plot below shows the average number of amenities in a 500 meter radius around a property

<img src="images/amenities.png" width="400">
