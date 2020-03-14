// plots the figure with id
// id much match the div id above in the html
var data = [{
    type: "choroplethmapbox", locations: ["NY", "MA", "VT"], z: [-50, -10, -20],
    geojson: "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
}];

var layout = {
    mapbox: { center: { lon: -74, lat: 43 }, zoom: 3.5 },
    width: 600, height: 400
};

var config = { mapboxAccessToken: "pk.eyJ1IjoibXdpbGtlbnMiLCJhIjoiY2s3ajRtbzN3MDBtMTNrcnZsMWNraHpmZCJ9.L-XPpfyIRcDx_gaaRMjHLg" };

Plotly.newPlot("mydiv", data, layout, config || {});
