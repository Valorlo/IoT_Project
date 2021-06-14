var map;
// Google maps
// First load
function initialize() {
    var uluru = {lat: 22.6272784, lng: 120.3014353};
    // initialize map
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 19,
        mapTypeId: google.maps.MapTypeId.SATELLITE,
        center: uluru
    });

    var marker = new google.maps.Marker({
        position: uluru,
        map: map
    });
    // var geocoder = new google.maps.Geocoder(); //用於將地址轉座標

    //用於將地址轉座標 跟點出警察局的點
    // geocoder.geocode( { 'address': addr}, function(results, status) {
    //     if (status == 'OK') {
    //         if ($('h4.D_status').html() != "Drone Status : Drone Disconnect" && $('h4.D_status').html() != "Drone Status : Server Disconnect") {
    //             var initialPos = $("div#initial_gps").html().replace(/\'/g, '"')
    //             var dPos = JSON.parse(initialPos)
    //             position = {
    //                 lat: parseFloat(dPos['lat']),
    //                 lng: parseFloat(dPos['lng'])
    //             };
    //             flightMarker = new google.maps.Marker({
    //                 position: position,
    //                 map: map,
    //                 animation: google.maps.Animation.DROP,
    //                 icon: "/static/images/camera-drone_32px.png"
    //             });
    //             smMarker = new google.maps.Marker({
    //                 position: position,
    //                 map: map2,
    //                 animation: google.maps.Animation.DROP,
    //                 icon: "/static/images/camera-drone_32px.png"
    //             });
    //             map.panTo(position)
    //             map2.panTo(position)
    //         }
    //         else{
    //             map.panTo(results[0].geometry.location);
    //             map2.panTo(results[0].geometry.location);
    //         }
    //         mapCenter = {
    //             lat:results[0].geometry.location.lat(),
    //             lng:results[0].geometry.location.lng()
    //         }
    //         var request = {
    //             location: mapCenter,
    //             radius: '500',
    //             type: ['police']
    //         };
    //         service = new google.maps.places.PlacesService(map);
    //         service.nearbySearch(request, callback);
    //     }
    // });



    // //點擊新增Marker
    // map.addListener('click', (event) => {
    //     $('button#plan').removeClass('d-none')
    //     placeMarker(event.latLng);
    //     smallFixed(event.latLng);
    // });
    // map.addListener('dragend',(event)=>{
    //     map2.setCenter(map.getCenter())
    // })
}

// 用於處理地址轉座標
// function callback(results, status) {
//     if (status == google.maps.places.PlacesServiceStatus.OK) {
//         for (var i = 0; i < results.length; i++) {
//             createMarker(results[i]);
//         }
//     }
// }

google.maps.event.addDomListener(window, 'load', initialize);