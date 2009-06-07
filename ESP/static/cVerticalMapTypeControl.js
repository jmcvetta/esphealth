function cVerticalMapTypeControl() {
}
cVerticalMapTypeControl.prototype = new GControl();

cVerticalMapTypeControl.prototype.initialize = function(map) {
    var cvmptc_ = this;

    var container = document.createElement("div");
    container.style.position = 'absolute';

    var mapButtonContainerDiv = document.createElement("div");
    this.setButtonContainerStyle(mapButtonContainerDiv);
    var mapButtonDiv = document.createElement("div");
    this.setSelectedButtonStyle(mapButtonDiv);
    mapButtonContainerDiv.style.top = '0em';
    container.appendChild(mapButtonContainerDiv);
    mapButtonContainerDiv.appendChild(mapButtonDiv);
    mapButtonDiv.appendChild(document.createTextNode("Map"));
    GEvent.addDomListener(mapButtonDiv, "click", function() {
        map.setMapType(G_NORMAL_MAP);
        cvmptc_.setSelectedButtonStyle(mapButtonDiv);
        cvmptc_.setUnSelectedButtonStyle(satelliteButtonDiv);
        cvmptc_.setUnSelectedButtonStyle(hybridButtonDiv);
});

    var satelliteButtonContainerDiv = document.createElement("div");
    this.setButtonContainerStyle(satelliteButtonContainerDiv);
    var satelliteButtonDiv = document.createElement("div");
    this.setUnSelectedButtonStyle(satelliteButtonDiv);
    satelliteButtonContainerDiv.style.top = '2em';
    container.appendChild(satelliteButtonContainerDiv);
    satelliteButtonContainerDiv.appendChild(satelliteButtonDiv);
    satelliteButtonDiv.appendChild(document.createTextNode("Satellite"));
    GEvent.addDomListener(satelliteButtonDiv, "click", function() {
        map.setMapType(G_SATELLITE_MAP);
        cvmptc_.setSelectedButtonStyle(satelliteButtonDiv);
        cvmptc_.setUnSelectedButtonStyle(mapButtonDiv);
        cvmptc_.setUnSelectedButtonStyle(hybridButtonDiv);
 });


    var hybridButtonContainerDiv = document.createElement("div");
    this.setButtonContainerStyle(hybridButtonContainerDiv);
    var hybridButtonDiv = document.createElement("div");
    this.setUnSelectedButtonStyle(hybridButtonDiv);
    hybridButtonContainerDiv.style.top = '4em';
    container.appendChild(hybridButtonContainerDiv);
    hybridButtonContainerDiv.appendChild(hybridButtonDiv);
    hybridButtonDiv.appendChild(document.createTextNode("Hybrid"));
    GEvent.addDomListener(hybridButtonDiv, "click", function() {
        map.setMapType(G_HYBRID_MAP);
        cvmptc_.setSelectedButtonStyle(hybridButtonDiv);
        cvmptc_.setUnSelectedButtonStyle(mapButtonDiv);
        cvmptc_.setUnSelectedButtonStyle(satelliteButtonDiv);
});

    map.getContainer().appendChild(container);
    return container;
}

cVerticalMapTypeControl.prototype.getDefaultPosition = function() {
    return new GControlPosition(G_ANCHOR_TOP_LEFT, new GSize(90,7));
}

cVerticalMapTypeControl.prototype.setButtonContainerStyle = function(div) {
    div.style.border = '1px solid black';
    div.style.position = 'absolute';
    div.style.backgroundColor = 'white';
    div.style.textAlign = 'center';
    div.style.width = '5em';
    div.style.cursor= 'pointer';
}

cVerticalMapTypeControl.prototype.setSelectedButtonStyle = function(div) {
    div.style.border = 'solid';
    div.style.borderColor = 'rgb(176, 176, 176) white white rgb(176, 176, 176)';
    div.style.borderWidth = '1px';
    div.style.fontSize = '12px';
    div.style.fontWeight = 'bold';
}

cVerticalMapTypeControl.prototype.setUnSelectedButtonStyle = function(div) {
    div.style.border = 'solid';
    div.style.borderColor = 'white rgb(176, 176, 176) rgb(176, 176, 176) white';
    div.style.borderWidth = '1px';
    div.style.fontSize = '12px';
    div.style.fontWeight = 'normal';
}

