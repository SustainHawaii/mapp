//Configure google map and load data from REST json
window.bigMap = null;
window.mapProp = null;
window.mapBound = null;
window.infowindow = null;

function initialize() {
    //need to set the variable to be public so it will able to use outside this function.
    mapProp = {
        center: new google.maps.LatLng(21.1098, -157.5311),
        zoom: 7
    };

    bigMap = new google.maps.Map(document.getElementById("map_canvas"), mapProp);

    //style it -- to images loaded from location type
    bigMap.data.setStyle(function (feature) {
        return {
            icon: feature.getProperty('icon')
        };
    });

    //show the info windows for the features
    infowindow = new google.maps.InfoWindow({
        content: ""
    });

    bigMap.data.addListener('click', function (event) {
        var contentString = getContentString(event);
        infowindow.setContent(contentString);
        var point = new google.maps.Point();
        // Let infowindow slightly above the marker
        point.x = 0;
        point.y = -30;

        // tell infowindow where should it show at.
        var anchor = new google.maps.MVCObject();
        anchor.set("position", event.latLng);
        anchor.set("anchorPoint", point);

        infowindow.open(bigMap, anchor);
    });

    //close the infowindow when click on bigMap. This will not prevent infowindow to be shown when click on other marker.
    google.maps.event.addListener(bigMap, 'click', function () {
        infowindow.close();
    });

    loadGeoJson();
}

google.maps.event.addDomListener(window, 'load', initialize);

//format what's displayed in the infowindow
function getContentString(obj) {
    var tmpl = $('#tmpl-infowindow').text();
    var replaceStrings = [
        {
            'search': '%img_src%',
            'replace': obj.feature.getProperty('image') || '/static/img/logo-sh.png'
        },
        {
            'search': '%item_id%',
            'replace': obj.feature.getProperty('id') || ''
        },
        {
            'search': '%item_name%',
            'replace': obj.feature.getProperty('name') || ''
        },
        {
            'search': '%formatted_address%',
            'replace': obj.feature.getProperty('formatted_address') || ''
        },
        {
            'search': '%desc%',
            'replace': obj.feature.getProperty('description') || ''
        }
    ];

    for (var strArr in replaceStrings) {
        tmpl = tmpl.replace(replaceStrings[strArr]['search'], replaceStrings[strArr]['replace']);
    }

    return tmpl;
}

function loadGeoJson(query, resize) {
    query || (query = {});

    //request geojson format
    query['data_format'] = 'geojson';

    function _callback() {
        resize || (resize = false);
        loadGeoJsonCallback(resize);
    }

    bigMap.data.loadGeoJson('/api/v1/location/search/?' + $.param(query), null, _callback);
}

function loadGeoJsonCallback(resize) {
    //set the extend
    mapBound = new google.maps.LatLngBounds();
    var hasFeatures = false;
    var count = 0;

    //show map features.
    bigMap.data.forEach(function (feature) {
        count++;
        hasFeatures = true;
        var geom = feature.getGeometry();
        if (geom.getType() == 'Point') {
            mapBound.extend(geom.get());
        }
    });

    if (hasFeatures && resize) {
        bigMap.fitBounds(mapBound);
        if (bigMap.getZoom() > 15) {
            bigMap.setZoom(15);
        }
    }

    //DirectoryManager.refreshData(bigMap.data);
    //DirectoryManager.showRecords();

    switch (count) {
        case 0:
            count = 'No result';
            break;
        case 1:
            count = '1 result';
            break;
        default:
            count = count + ' results';
    }
    $('#record_count').text(count);
}

/**
 * @class DirectoryRecord
 */
function DirectoryRecord(feature, parentNode) {
    this.contentString = "";
    this.parentNode = parentNode;
    this.feature = feature;

    var _show = false;
    var _initializedMap = false;
    var _elm = null;
    var _map = null;
    var _maxZoom = 15;
    var mapProp = {
        center: new google.maps.LatLng(21.1098, -157.5311),
        zoom: _maxZoom
    };
    var _mapBound = new google.maps.LatLngBounds();

    this.setContentString = function(str) {
        var replaceStrings = [
            {
                'search': '%item_id%',
                'replace': this.feature.getProperty('id') || ''
            },
            {
                'search': '%item_name%',
                'replace': this.feature.getProperty('name') || ''
            },
            {
                'search': '%formatted_address%',
                'replace': this.feature.getProperty('formatted_address') || ''
            },
            {
                'search': '%desc%',
                'replace': this.feature.getProperty('description') || ''
            }
        ];
        for (var strArr in replaceStrings) {
            str = str.replace(replaceStrings[strArr]['search'], replaceStrings[strArr]['replace']);
        }
        this.contentString = str;
    };

    this.show = function() {
        if (!_show) {
            _elm = $(this.contentString);
            this.parentNode.append(_elm);
            _show = true;
        }
        this.initMap();
    };

    this.initMap = function() {
        if (_initializedMap) {
            return;
        }
        _initializedMap = true;

        //need to set the variable to be public so it will able to use outside this function.
        _map = new google.maps.Map($(_elm).find('.google_map_container')[0], mapProp);

        //style it -- to images loaded from location type
        _map.data.setStyle(function (feature) {
            return {
                icon: feature.getProperty('icon')
            };
        });

        _map.data.add(this.feature);
        var geom = feature.getGeometry();
        if (geom.getType() == 'Point') {
            _mapBound.extend(geom.get());
        }
        this.showMap();
    };

    this.showMap = function() {
        //adjust google map viewport if the map already initialized.
        if (_initializedMap) {
            google.maps.event.trigger(_map, 'resize');
            _map.fitBounds(_mapBound);
            if (_map.getZoom() >_maxZoom) {
                _map.setZoom(_maxZoom);
            }
        }
    };

    function getTemplate() {
        return $('#tmpl-directory-block').text();
    }

    this.setContentString(getTemplate());
}

window.DirectoryManager = undefined;
/**
 * @class DirectoryManager (Singleton)
 */
(function(name, window, $) {
    var _elm = $('#tab-search-directory');
    var _containerElm = $(_elm).find('.directory-block-container');
    var _loadMoreBtn = $(_elm).find('#load-more-button');

    var obj = {
        records: [],
        recordShown: 0,
        createRecord: function(feature) {
            this.records.push(new DirectoryRecord(feature, _containerElm));
        },
        showRecords: function(recCnt) {
            //default to 10
            recCnt || (recCnt = 10);
            for (var i = 0; i < recCnt; i++) {
                //hit the last records?
                if (this.recordShown >= this.records.length) {
                    $(_loadMoreBtn).hide();
                    break;
                }
                this.records[this.recordShown++].show();
            }

            if (this.records.length > this.recordShown) {
                $(_loadMoreBtn).show();
            }
        },
        clear: function() {
            this.records = [];
            this.recordShown = 0;
            $(_loadMoreBtn).hide();
            $(_containerElm).html('');
        },
        refreshData: function(mapData) {
            //clear cache
            this.clear();

            var self = this;
            mapData.forEach(function (feature) {
                //add to cache
                self.createRecord(feature);
            });
        },
        adjustMap: function() {
            for (var i = 0; i < this.recordShown; i++) {
                this.records[i].showMap();
            }
        }
    };
    window[name] = obj;

    $(_loadMoreBtn).click(function(e) {
        e.preventDefault();
        obj.showRecords();
    });

})('DirectoryManager', window, jQuery);

//submit the form when click on the search icon
$("#submit-icon").click(function () {
    $('#search-form').submit();
});

$("#location_type").change(function () {
    $('#search-form').submit();
});

$("#category").change(function () {
    $('#search-form').submit();
});

$("#tags").change(function () {
    $('#search-form').submit();
});

$("#viz").change(function () {
    var viz_id = $(this).val()[0];
    $.ajax({
        url: '/maps-admin/data/show-viz/' + viz_id + '/',
        success: function(data) {
            $('.directory-block-container').html(data);
        }
    });
});

//capture form submit event
$("#search-form").submit(function (e) {
    //do not submit the form
    e.preventDefault();

    //hide the info window
    infowindow.close();

    //clear out existing data
    bigMap.data.forEach(function (feature) {
        bigMap.data.remove(feature);
    });

    //build query string
    var query = {
        q: $("#q").val(),
        loc_type: $("#location_type").val(),
        tags: $("#tags").val(),
        category: $("#category").val()
    };
    loadGeoJson(query, true);
});
