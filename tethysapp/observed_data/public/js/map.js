window.onload=function(){
    setTimeout(function() {
        var mapobject=TETHYS_GOOGLE_MAP_VIEW.getMap();
		
		mapobject.setCenter({lat: 18.81, lng: -70.95});
        mapobject.setZoom(8);
    }, 2000);
};

