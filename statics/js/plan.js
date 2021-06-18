// Google maps
var map;
var lat;
var lng;
var markers = [];
var marker;
var dMarker;
var geocoder;
var origin;
// First load
function initialize() {
    geocoder = new google.maps.Geocoder();
    var address = $(".source_info").text()
    geocoder.geocode({ 'address': address }, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            origin = results[0].geometry.location
            // initialize map
            map = new google.maps.Map(document.getElementById('map'), {
                zoom: 19,
                mapTypeId: google.maps.MapTypeId.SATELLITE,
                center: origin
            });

            marker = new google.maps.Marker({
                position: origin,
                map: map,
                animation: google.maps.Animation.DROP,
                icon: "/statics/images/camera-drone_32px.png"
            });
        } else {
            alert("失敗, 原因: " + status);
        }
    });
}

google.maps.event.addDomListener(window, 'load', initialize);

// draw gps route on the map
function GPSinterval(map, marker) {
    var count = 0;
    console.log("in GPSinterval")
    poly = new google.maps.Polyline({
        strokeColor: "#000000",
        strokeOpacity: 1.0,
        strokeWeight: 3,
    });
    poly.setMap(map);
    Ginterval = window.setInterval(function () {
        // 定時去檢查無人機到了沒
        if(count == 10){
            $.ajax({
                method:"POST",
                url:"api/drone/state",
                success:function(msg){
                    if(msg.state == "LAND"){
                        clearInterval(Ginterval);
                        deliveryInfo();
                    }
                    else{
                        console.log(msg.state)
                    }
                }
            })
        }
        // 請求無人機目前的位置
        $.ajax({
            method: "GET",
            url: "api/drone/current",
            success: function (msg) {
                cp = []
                if (!msg.status) {
                    console.log("GPS not recived")
                }
                else {
                    cp = [msg.currentP[0], msg.currentP[1]]
                    var pos = new google.maps.LatLng(cp[0], cp[1]);
                    console.log(cp[0])
                    console.log(cp[1])
                    // if ($("div.pos").length > 0) {
                    //     $("div.pos").empty()
                    // }
                    // $(".pos").append(`<p><h5>Current Drone's Position : </h5><br><h5>lat : ${cp[0]} lng : ${cp[1]}</h5></p>`)
                    const path = poly.getPath()
                    marker.setPosition(pos);
                    path.push(pos)
                    map.panTo(pos);
                }
            }
        })
        count++;
    }, 1000);
}

// Sets the map on all markers in the array.
function setMapOnAll(map) {
    for (let i = 0; i < markers.length; i++) {
        markers[i].setMap(map);
    }
}

// detect destinations select
$('#destination').on('change', function () {
    if ($(this).val() != "請選擇目的地") {
        setMapOnAll(null);
        $("#address").attr("placeholder", $(this).val());
        geocoder = new google.maps.Geocoder();
        var address = $(this).val()
        geocoder.geocode({ 'address': address }, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                lat = results[0].geometry.location.lat(),
                lng = results[0].geometry.location.lng()
                map.setCenter(results[0].geometry.location);
                dMarker = new google.maps.Marker({
                    position: results[0].geometry.location,
                    map: map,
                    animation: google.maps.Animation.DROP,
                });
                markers.push(dMarker)
            } else {
                alert("失敗, 原因: " + status);
            }
        });
    } else {
        setMapOnAll(null);
        map.setCenter(origin);
        $("#address").attr("placeholder", "");
    }
});

// order confirm
$("#order").on('click', function () {
    var pid = $("#destination option:selected").attr("id")
    var counts = $("#pNumbers").val()
    if (counts > 0) {
        $.ajax({
            method: "POST",
            url: "api/users/confirm",
            data: {
                pid: pid,
                counts: counts,
                lat: lat,
                lng: lng
            },
            success: function (msg) {
                if (msg.status) {
                    // 先把地圖移回出發地
                    map.setCenter(origin);
                    $(".card").hide()
                    // 這邊要放畫地圖的function
                    GPSinterval(map, marker)

                    // // test for 簽收功能
                    // setTimeout(deliveryInfo, 3000)
                } else {
                    alert("something went wrong :(")
                }
            }
        })
    }

})

// arrive destination, show packages info
function deliveryInfo() {
    var mid = $("#destination option:selected").attr("id")
    $.ajax({
        method: "POST",
        url: "api/users/retrieve",
        data: {
            mid: mid
        },
        success: function (msg) {
            if (msg.status) {
                $.ajax({
                    method: "POST",
                    url: "api/users/sendEmail",
                    data: {
                        pid: msg.pid
                    },
                    success: function (msg) {
                        if (msg.status) {
                            console.log("Email sent!")
                        }
                    }
                })
                $("#packages_id").text(msg.pid)
                $("#source_name").text(msg.name)
                $("#source_address").text(msg.address)
                var date = new Date(msg.time)
                var result = date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate() + ' '
                    + date.getHours() + ":" + ((date.getMinutes() < 10 ? '0' : '') + date.getMinutes())
                $("#start_time").text(result)
                $("#p_counts").text(msg.counts)
            }
        }
    })
    $("#deliverForm").show();
}

// sign up packages
$("#signfor").on('click', signfor)
function signfor() {
    var pid = $("#packages_id").text();
    $.ajax({
        method: "POST",
        url: "api/users/signfor",
        data: {
            pid: pid
        },
        success: function (msg) {
            if (msg.status) {
                $("thead tr").children()[5].remove()
                $("tbody tr").children()[5].remove()
                $("thead tr").append(`<th scope="col">抵達時間</th><th scope="col">返航</th>`)
                var date = new Date(msg.arrive_time)
                var result = date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate() + ' '
                    + date.getHours() + ":" + ((date.getMinutes() < 10 ? '0' : '') + date.getMinutes())
                $("tbody tr").append(`<td>${result}</td><td><button type="button" class="btn btn-success btn-sm" data-toggle="modal"
                data-target="#warning">返航</button></td>`)
            }
        }
    })
}

// drone rtl
$("#return").on('click', rtl)
function rtl() {
    $.ajax({
        method: "POST",
        url: "api/drone/rtl",
        success: function (msg) {
            if (msg.status) {
                window.location.reload()
            }
        }
    })
}

// delivery record
$("#record").on('click',record)
function record(){
    window.location.href = "/record"
}