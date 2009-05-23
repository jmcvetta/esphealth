{% extends "espss_base.html" %}

{% block title %}
<title>ESP:SS Syndromic Surveillance Maps</title>
{% endblock %}

{% block extrahead %}

    <script type="text/javascript">
      var styles = [[{
        url: '../images/people35.png',
        height: 35,
        width: 35,
        opt_anchor: [16, 0],
        opt_textColor: '#FF00FF'
      },
      {
        url: '../images/people45.png',
        height: 45,
        width: 45,
        opt_anchor: [24, 0],
        opt_textColor: '#FF0000'
      },
      {
        url: '../images/people55.png',
        height: 55,
        width: 55,
        opt_anchor: [32, 0]
      }],
      [{
        url: '../images/conv30.png',
        height: 27,
        width: 30,
        anchor: [3, 0],
        textColor: '#FF00FF'
      },
      {
        url: '../images/conv40.png', 
        height: 36,
        width: 40,
        opt_anchor: [6, 0],
        opt_textColor: '#FF0000'
      },
      {
        url: '../images/conv50.png',
        width: 50,
        height: 45,
        opt_anchor: [8, 0]
      }],
      [{
        url: '../images/heart30.png',
        height: 26,
        width: 30,
        opt_anchor: [4, 0],
        opt_textColor: '#FF00FF'
      },
      {
        url: '../images/heart40.png', 
        height: 35,
        width: 40,
        opt_anchor: [8, 0],
        opt_textColor: '#FF0000'
      },
      {
        url: '../images/heart50.png',
        width: 50,
        height: 44,
        opt_anchor: [12, 0]
      }]];
    
  
      function refreshMap() {
        if (markerClusterer != null) {
          markerClusterer.clearMarkers();
        }
        var zoom = parseInt(document.getElementById("zoom").value, 10);
        var size = parseInt(document.getElementById("size").value, 10);
        var style = document.getElementById("style").value;
        zoom = zoom == -1 ? null : zoom;
        size = size == -1 ? null : size;
        style = style == "-1" ? null: parseInt(style, 10);
        markerClusterer = new MarkerClusterer(map, markers, {maxZoom: zoom, gridSize: size, styles: styles[style]});
      }
    </script>



{% if scount_list %}

<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;sensor=false&amp;key={{ GOOGLE_KEY }}"
   type="text/javascript"></script>
<title>ESP:SS Syndromic Surveillance Maps</title>
<script src="http://esphealth.org/espss/static/cVerticalMapTypeControl.js"></script>
<script src="http://esphealth.org/espss/static/mapiconmaker.js"></script>
<script src="http://gmaps-utility-library.googlecode.com/svn/trunk/markermanager/release/src/markermanager.js"></script>
<script type="text/javascript">
    var scounts = [{% for c in scount_list %}[{{c.lon}},{{c.lati}},'{{c.z}}','{{c.synd}}',
    '{{c.n}}','{{c.pct}}','{{ c.edate }}',{{c.heat}}]{% if not forloop.last %},{% endif %}{% endfor %}];

  
    var map_long = -71.0928603;
    var map_lat = 42.3404107;
    var map_zoom = 9;
    var custom = 0;
    {% for hex in heathex_list %}  
    var iconOptions = {};
    iconOptions.width = 18 + {{ forloop.counter }};
    iconOptions.height = 12 + {{ forloop.counter }};
    iconOptions.primaryColor = "{{ hex.hex }}";
    iconOptions.label = "{{ hex.n }}";
    iconOptions.labelSize = 0;
    iconOptions.labelColor = "#000000";
    iconOptions.shape = "roundrect";
    var icon = MapIconMaker.createFlatIcon(iconOptions);
    /* see colour gradient maker at http://www.herethere.net/~samson/php/color_gradient/?cbegin=00FF00&cend=FF0000&steps=10 
    and the mapiconmaker docs at http://gmaps-utility-library.googlecode.com/svn/trunk/mapiconmaker/1.1/docs/examples.html */
    var heat{{ forloop.counter }} = MapIconMaker.createFlatIcon(iconOptions); 
    
{% endfor %} 
var hicons = [heat1,heat2,heat3,heat4,heat5,heat6,heat7,heat8,heat9,heat10];

function addSyndMarker(map,lng, lat, z, synd, n, pct, edate, heat) {


var markers = [];
var markerClusterer = null;
function initialize() {

var latlng = new GLatLng(lat,lng);
    var marker = new GMarker(latlng, {icon: hicons[heat]});
    var html = '<b>Date =&nbsp;' + edate + '</b><br>Zip Code =&nbsp;' + z + '<br>Synd Count=' + n + '<br>Synd Pct=' + pct;
    GEvent.addListener(marker, "click", function() { marker.openInfoWindowHtml(html); });
    //map.addOverlay(marker);
    markers.push(marker);
}

    function initialize() {
        if (GBrowserIsCompatible()) {
            var map = new GMap2(document.getElementById("map_canvas"));
            {% if not map_type %} var map_type="normal"; {% else %} var map_type = {{map_type}}; {% endif %}            
            if (map_type == "normal") map.setMapType(G_NORMAL_MAP);                  
            if (map_type == "satellite") map.setMapType(G_SATELLITE_MAP);               
            if (map_type == "hybrid") map.setMapType(G_HYBRID_MAP);                  
            if (map_type == "terrain") map.setMapType(G_TERRAIN_MAP);      
            map.setCenter(new GLatLng(map_lat,map_long), map_zoom);
            var mgr = new MarkerManager(map); 
            if (custom==1){
                var pos1 = new GControlPosition(G_ANCHOR_TOP_LEFT, new GSize(19,170));
                map.addControl(new GSmallMapControl(),pos1 );
                var pos2 = new GControlPosition(G_ANCHOR_TOP_LEFT, new GSize(7,90));
                map.addControl(new cVerticalMapTypeControl(), pos2);
            }
            else {  
          map.addControl(new GLargeMapControl());
          map.addControl(new GMapTypeControl());
          var icon = new GIcon(G_DEFAULT_ICON);
          icon.image = "http://chart.apis.google.com/chart?cht=mm&chs=24x32&chco=FFFFFF,008CFF,000000&ext=.png";
           
            //map.setUIToDefault();
            }
            if (scounts) {
                for (var i=0; i < scounts.length; i++) {
                    addSyndMarker(map,scounts[i][0], scounts[i][1], scounts[i][2], 
                    scounts[i][3], scounts[i][4],scounts[i][5],scounts[i][6],scounts[i][7]);
                }
            }
            refreshMap();
            }

      }  

</script>
{% endif %}

{% endblock %}


{% if scount_list %}
{% block extrabody %}
    <body onload="initialize()" onunload="GUnload()">
{% endblock %}
{% endif %}

{% block content %}
    {% if scount_list %}
        <div style="width:{{ width }}px; text-align:center;">
        <font color="maroon"> Syndrome Map for {{syndrome}} on {{sdate}}. Heatmap legend below. Click a site to see details<br>
        <table border="0" width="{{width}}" cellspacing="5" cellpadding="10">
        <tr valign="middle" align="center">
        <td>{% if prevw %}<a href="http://esphealth.org/espss/ssmap/{{prevw}}">Previous Week ({{prevw}})</a>{% endif %}</td>
        <td>{% if prevd %}<a href="http://esphealth.org/espss/ssmap/{{prevd}}">Previous Day ({{prevd}})</a>{% endif %}</td>
        <td>{% if nextd %}<a href="http://esphealth.org/espss/ssmap/{{nextd}}">Next Day ({{nextd}})</a>{% endif %}</td>
        <td>{% if nextw %}<a href="http://esphealth.org/espss/ssmap/{{nextw}}">Next Week ({{nextw}})</a>{% endif %}</td>
        </td></tr></table></font>
        </div>
        <div id="map_canvas" style="width: {{ width }}px; height: {{ height }}px">
        </div>
        <div>
        <TABLE BORDER="0" width="{{width}}"><TR ALIGN="center" ><td width="30%"><font color="maroon"><b>Icon Heatmap Legend</b></font></td>
        {% for hex in heathex_list %} <TD VALIGN="top" BGCOLOR="{{hex.hex}}">
        <font color="#000000"><b>{{ hex.n }}</b></font></TD>
        {% endfor %}</tr></table>
        </div>
    {% else %}
        <div>
        <table border="0" cellpadding="10" width="{{width}}">
        <tr><td valign="middle" align="center"><font size="+2" color="maroon">
        ESP Syndrome Map for {{syndrome}}<br>
        Sorry, no data available for date {{sdate}}. Please select a date from the list </font></td></tr>
        <tr><td valign="middle" align="center"><font color="maroon">Please select a valid date&nbsp;&nbsp;</font>

        <SELECT size="5" width="150" name="dsel" style="color:maroon;text-align:center;width:150px"
         onchange="window.location.href=this.options[this.selectedIndex].value">
        {% for d in date_list %} <OPTION VALUE="/espss/ssmap/{{d.date}}" {% ifequal d.date tdate %}SELECTED{% endifequal %}>{{d.datetime}}</OPTION> 
        {% endfor %} 
        </SELECT>
        </td></tr></table>
        </div>
    {% endif %}
    <div>
      <span>zoom level: 
        <select id="zoom">
          <option value="-1">Default</option>
          <option value="7">7</option>
          <option value="8">8</option>
          <option value="9">9</option>

          <option value="10">10</option>
          <option value="11">11</option>
          <option value="12">12</option>
          <option value="13">13</option>
          <option value="14">14</option>
        </select>

      </span>
      <span style="margin-left:20px;">Cluster size:
        <select id="size">
          <option value="-1">Default</option>
          <option value="40">40</option>
          <option value="50">50</option>
          <option value="70">70</option>

          <option value="80">80</option>
        </select>
      </span>
      <span style="margin-left:20px;">Cluster style: 
        <select id="style">
          <option value="-1">Default</option>
          <option value="0">People</option>
          <option value="1">Conversation</option>

          <option value="2">Heart</option>
       </select>
       <input type="button" value="Refresh Map" style="margin-left:20px;" onclick="refreshMap()"></input>
    </div>



{% endblock content %}
