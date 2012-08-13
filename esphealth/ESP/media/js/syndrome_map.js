
function initialize(lat, long, zoom) {
  if (GBrowserIsCompatible()) {
    var map = new GMap2(document.getElementById("map_canvas"));
    map.setCenter(new GLatLng(lat, long), zoom);
    map.setUIToDefault();
  }
}
