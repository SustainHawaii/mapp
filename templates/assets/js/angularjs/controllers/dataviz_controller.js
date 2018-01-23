(function(){
    'use strict';

    angular.module('datavizApp', ['ngRoute', 'ngSanitize', 'ui.select',
                                  'socialLinks', 'smart-table', 'mapp_data', 'ngMaps', 'highcharts-ng'])
        .filter("escape", escape)
        .controller("TabsCtrl", TabsCtrl)
        .controller("SourceCtrl", SourceCtrl)
        .controller("BuildCtrl", BuildCtrl)
        .controller("PreviewCtrl", PreviewCtrl)
        .controller("PublishCtrl", PublishCtrl)
        .controller("DataVisualizationController", DataVisualizationController)
        .controller("DrilldownModalController", DrilldownModalController)
        .controller("OptionsModalController", OptionsModalController)
        .factory("DrilldownModalFactory", DrilldownModalFactory)
        .factory("OptionsModalFactory", OptionsModalFactory)
        .factory("mapping", mapping)
        .factory("charting", charting)
        .factory("dataviz", dataviz)
        .directive("previewViz", previewViz)
        .directive("dsInfo", dsInfo)
        .config(datavizConfig);

    function filter_numbers(ds){
        return  (ds.name.indexOf("number") > 1) && (angular.isNumber(ds.value));
    }                    

    function escape(){
        return window.encodeURIComponent;
    }
    function find_by_prop(propertyName, propertyValue, collection) {
      var i=0, len=collection.length;
      for (; i<len; i++) {
          if (collection[i][propertyName] == propertyValue) {
              return collection[i];
          }
      }
      return null;
    }
    /*pure js helpers*/

    //TODO: if each type was and object that exposed the proper functinoality, then
    //we could save alot of these checks... ala polymorphism
     function isMap (widget){
        return (widget.viz_type.toLowerCase() == "map");
    }

    function mapping() {

        //functions to update markers and draw info window
        var infowindow = new google.maps.InfoWindow();
        var url =  "";
        var center = [ 21.1098, -157.5311];
        var data_types = ['System Data', 'GeoJSON', 'latlong'];        

        var service = {
            getInfoWindowHTML: getInfoWindowHTML,
            point_options: point_options,
            click_function: click_function,
            center: center,
            options: options,
            restore_map_functions: restore_map_functions,
            clearLayers: clearLayers,
            getDataTypes: getDataTypes,
            plotSystemData: plotSystemData,
            options_for_location: options_for_location
        };

        return service;

        ///////////////////////////////////////////////////////
        // Implementation
        ///////////////////////////////////////////////////////

        function getInfoWindowHTML(obj) {
            // generates the popup template for map points
            var tmpl = '<div id="info-map">'
                    +  '<div style="display: inline-block; width: 86px; verticle-align: top; float: left;">'
                    +  ' <img src="%img_src%" class="thumbnail" style="width: 80%; verticle-align: top;"/>'
                    + '</div>'
                    +  '<div style="display:inline-block; width:200px; float:left;">'
                    +    '<h4><a href="/members-location/%item_id%/">%item_name%</a></h4>'
                    +     '<div>%formatted_address%</div>'
                    +      '<br/>'
                    + '<div><b>%desc%</b></div>'
                    +  ' </div>'
                    + '</div>';

            var replaceStrings = [
                {
                    search: "%img_src%",
                    replace: obj.properties['image'] || "/static/img/logo-sh.png"
                },
                {
                    search: "%item_id%",
                    replace: obj.properties['id'] || ""
                },
                {
                    search: "%item_name%",
                    replace: obj.properties["name"] || ""
                },
                {
                    search: "%formatted_address%",
                    replace: obj.properties['formatted_address'] || ""
                },
                {
                    search: "%desc%",
                    replace: obj.properties["description"] || ""
                }
            ];
            for (var strArr in replaceStrings) {
                tmpl = tmpl.replace(replaceStrings[strArr]['search'], replaceStrings[strArr]['replace']);
            }
            return tmpl;
        }

        function point_options(geometry, properties, map, i) {
            if (geometry.type == "MultiPolygon" || geometry.type == "Polygon") {
                return polygon_config();
            } else {
                return point_config(properties);
            }
        }

        function polygon_config(){
            return {fillColor: "#e67e22",
                    strokeColor: "#d35400"};
        }

        function point_config(properties) {
            return {icon: properties.icon,
                    title:properties.name};
        }

        function click_function(e, marker, map, markers) {
            var content = getInfoWindowHTML(marker);
            infowindow.setContent(content);
            var point = new google.maps.Point();
            // Set infowindow slightly above the marker
            point.x = 0;
            point.y = -30;

            // Set infowindow coords
            var anchor = new google.maps.MVCObject();
            anchor.set("position", e.latLng);
            anchor.set("anchorPoint", point);

            infowindow.open(map, anchor);
        }

        function options() {
            return {
                streetViewControl: false,
                zoomControl: true,
                scrollwheel: false
            };
        }

    /* map layer config example...
    {loc_type : { url : url,
        options : point_options,
          events : { click : click_function}
        },
  */

        function restore_map_functions(widget) {
            /* ensure map type charts have proper options setup
             * i.e. click function to show info window,
             * function to use proper marker symbols
             * and map initially centered in the correct place
             */
					  console.log("restore_map_functions");
            if (!widget.chart_options.hasOwnProperty("map_center")){
                widget.chart_options["map_center"] = center;
            }
            if (!widget.chart_options.hasOwnProperty("map_zoom")){
                widget.chart_options["map_zoom"] = 7;
            }
            if (!widget.chart_options.hasOwnProperty("map_options")){
                widget.chart_options["map_options"] = options;
            }

            if (!widget.chart_options.hasOwnProperty("layers")) {
                widget.chart_options["layers"] = {};
                return widget;
            }
            angular.forEach(widget.chart_options.layers, function(layer) {
							  console.log("layer is", layer);
                if (!layer.options) {
                    layer.options = point_options;

										//click options only for locations
										if (layer.hasOwnProperty("url") &&
												layer.url.search("location") > 0){ 

													layer.events.click = click_function;
										}
                }
            });

            return widget;
        }

        function clearLayers(widget) {
            //this will in effect remove all the markers from the map
            angular.forEach(widget.chart_options.layers, function(layer) {
                layer.url = '';
            });
        }

        function getDataTypes(widget) {
            /* get selected data grouped by type, this is used to reduce the number of queries
             * to the backend.  I.e. one per type as opposed to one per dataset.
             */

            var layer_data = { "location types" :
                               {query : { loc_type : []}, param_name : "loc_type", url : '/api/v1/location/search/?',
                                layer_name : "location types"},
                               //"user types" :  {query : { user_type : []}, param_name : "user_type"},
                               "categories":  {query : { tags : []}, param_name : "tags", url : '/api/v1/location/search/?',
                                               layer_name : "categories"},
                               "external_categories": {query : {category_id : []}, param_name : "category_id",
                                                            url : "/api/v1/dataimport/get-data/geo/?", layer_name : "external_categories"},
 
                               "taxonomy":  {query : { category : []}, param_name : "category", url : '/api/v1/location/search/?',
                                             layer_name : "taxonomy"},
                               "imported from live feed" : {query : {import_id : []}, param_name : "import_id",
                                                            url : "/api/v1/dataimport/get-data/geo/?", layer_name : "imported from live feed"},
                               "imported from file": {query : {import_id : []}, param_name : "import_id",
                                                      url : "/api/v1/dataimport/get-data/geo/?", layer_name : "imported from file"}
                             };

            //get list of selected datatypes for widget
            angular.forEach(widget.viz_datasets, function(ds) {
                if (ds.group) {
                    var layer = layer_data[ds.group.toLowerCase()];
                    if (layer) {
                        layer.query[layer.param_name].push(ds.id);
                    }
                }
            });

            return layer_data;
        }

        function plotSystemData(widget) {
            var layers = widget.chart_options.layers;

            //make sure we got map layers setup correctly
            restore_map_functions(widget);

            //get selected data grouped by type
            var layer_data = getDataTypes(widget);

            angular.forEach(layer_data, function(data) {
                //only update if we have some data of that appropriate type
                if(data.query[data.param_name].length > 0) {
                    data.query['data_format'] = "geojson";
                    if (!layers.hasOwnProperty(data.layer_name)) {
                        layers[data.layer_name] = { options : point_options,
                                                    events : { click : click_function}
                                                  };
                    }
                    //update the map
                    layers[data.layer_name].url = data.url + $.param(data.query);
                } else { // perhaps the layer type has been droped from the list of datasets
                    //  thus lets remove the markers from the map
                    if (layers && layers[data.layer_name]) {
                        layers[data.layer_name].url = '';
                    }
                }
            });
        }

        function options_for_location(locid) {
            return {"map_center" : mapping.center,
                    "map_zoom" : 7,
                    "map_options" : mapping.options,
                    "pointoptions" : mapping.point_options,
                    //"events" : {"click" : mapping.click_function},
                    "url" : "api/v1/location/geo/" + locid + "/"
                   };
        }
    }


    function charting($q, $filter, $timeout, mappdata) {

        //chart options
        var shared_chart_options = {
            options: {
                chart: {}
            },
            series: [],
            title: { text: 'Sample Chart' },
            xAxis: {
                title : { text : '' },
								type : "category",
            },
            yAxis: {
                title : { text : '' }
            },
            loading: false,
            func: function(chart) {
                $timeout(function() {
                    //chart.reflow();
                }, 0);
            }
        };

        var bar_specific_options = {
            options: {
                chart: { type : 'column' },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};">{series.name}: </td>' +
                        '<td ><b>{point.y}</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0
                    }
                }
            },
            drilldown: {
                series: []
            }
        };

        //TODO: upgrade angular to get the angular merge, instead of jquery one used here
        var bar_chart_options = $.extend(true,{}, shared_chart_options, bar_specific_options);

        var line_specific_options = {
            options: {
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'middle',
                    borderWidth: 0
                }
            }
        };

        var line_chart_options = $.extend(true,{}, shared_chart_options, line_specific_options);

        var pie_specific_options = {
            options: {
                chart: {
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
										type: 'pie',
                },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                            style: {
                                color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                            }
                        },
                        showInLegend: true
                    }
                },
                tooltip: { pointFormat: '{series.name}  -- <b>{point.percentage:.1f}%</b>' }
            },

            drilldown: {
                series: []
            }
        };

        var pie_chart_options = $.extend(true, {}, shared_chart_options, pie_specific_options);

        var donut_specific_options = {
            options: {
                chart: {
                    plotBackgroundColor: null,
                    plotBorderWidth: 0,
                    plotShadow: false,
										type: 'pie',
                },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        dataLabels: {
                            enabled: true,
                            distance: -50,
                            style: {
                                fontWeight: 'bold',
                                color: 'white',
                                textShadow: '0px 1px 2px black'
                            }
                        },
                        startAngle: -90,
                        endAngle: 90,
                        center: ['50%', '75%']
                    }
                },
                tooltip: { pointFormat: '{series.name}  -- <b>{point.percentage:.1f}%</b>' }
            },
            title: {
                text: 'Donut Chart',
                align: 'center',
                verticalAlign: 'middle',
                y: 50
            },
            drilldown: {
                series: []
            }
        };

        var donut_chart_options = $.extend(true, {}, shared_chart_options, donut_specific_options);

        var area_specific_options = {
            options: {
                chart: { type: 'area' }
            }
        };

        var area_chart_options = $.extend(true, {}, shared_chart_options, area_specific_options);

        var polar_specific_options = {
            options: {
                chart: {
                    type: 'bar',
                    polar: true
                }
            }
        };

        var polar_chart_options = $.extend(true, {}, shared_chart_options, polar_specific_options);

        var options = {'line-chart' : line_chart_options,
                       'bar-chart' : bar_chart_options,
                       'pie-chart' : pie_chart_options,
                       'area-chart' : area_chart_options,
                       'donut-chart' : donut_chart_options,
                       'polar-chart' : polar_chart_options
                      };

        var chart_types = [{key:'bar-chart', value:'Bar Charts'},
                           {key:'pie-chart', value:"Pie Charts" },
                           {key:'area-chart', value:"Area Charts"},
                           {key:'line-chart', value:"Line Charts"},
                           {key:'donut-chart', value: "Donut Charts"},
                           {key:'polar-chart', value: "Polar Charts"}
                          ];        

        var service = {
            chart_types: chart_types,
            get_chart_options: function(chartType) {
                return angular.copy(options[chartType]);
            },
            defaultChartOptions : bar_chart_options,
            dummyChartData : generateData,
            colors: colors,
						drilldownCB : drilldownCB,
            updateChartFields : updateChartFields,
            updateAllCharts : function(viz,limit) {
                return updateAllCharts(viz,limit);
            }
        };

        return service;

        ///////////////////////////////////////////////////////
        // Implementation
        ///////////////////////////////////////////////////////


        function drilldownCB (e){
            var chart = this;
            // Show the loading label
            chart.showLoading('Loading drilldown ...');

                var id = e.currentTarget.userOptions.dd[e.point.name];
                mappdata.getViz(id).then(function(result){
                    updateAllCharts(result.data).then(function(result){
                        var widget = result[0];
                        chart.hideLoading();
                        var data = widget.chart_options.series[0];
                        data = data.data.map(function(d, i){
                            return [widget.config_fields.categories[i], d.y];
                        });
												console.log("drilldown data series is", data);
                        chart.addSeriesAsDrilldown(e.point, {name:widget.title, data:data});
                    });
                });
                    
            }

        //combined colors theme
        var colors = ['#002A7F', '#005943', '#A5B500', '#FF7A00', '#620700', '#36002A'];

        function generateData() {
            return [{
                    data: [107, 23, 48, 86, 62, 12]
                }];
        }

        function getColorForField(idx) {
            if (idx <= colors.length) {
                var field_color = colors[idx];
            } else {
                var color_idx = (idx % colors.length) - 1;
                field_color = colors[color_idx];
            }
            return field_color;
        }

        //manipulate the charts
        function  getFieldValues(yfield, xfield, data) {
            /* get array of x-values and array of y-values in the same order */
            var values = [];
            var x_vals = [];
            var sorted = $filter('orderBy')(data[yfield.ds_id], xfield.ds_fieldName);
            if (!sorted) {
                return { x : x_vals, y : values};
            }
            for (var i = 0, arrLen = sorted.length; i < arrLen; i++) {
                var row = sorted[i];
                if (row.hasOwnProperty(xfield.ds_fieldName)){
                    values.push(row[yfield.ds_fieldName]);
                    x_vals.push(row[xfield.ds_fieldName]);
                }
            }
            values = values.map(ensure_valid_numbers);
            return { x : x_vals, y : values};
        };

        function ensure_valid_numbers(n){
            if(!Number(n) && n !== 0){
                n = n.replace(",","");
                n = parseFloat(n);
            }
            return n;
        }


        function updateChartFields(widget) {
            //the following code, is not the most terse form it could be
            //but has been optimized and tested for performance as this
            //is the most critical part of getting the data for the charts
            //the attempt is to keep as much checking out of the loop as possible
            //also angular.forEach is really slow, turns out
            //a for loop (will all init inside the for) is about the fastest on most browsers
            if (widget.config_fields.hasOwnProperty("y_axis") &&
                widget.config_fields.hasOwnProperty("x_axis"))
            {

                widget.chart_data = [];
                widget.chart_options.series = [];
                if (widget.chart_options.hasOwnProperty("xAxis")) {
									  //this delete should convert existing data viz to new format
										//need to remove it soonish
									  delete widget.chart_options.xAxis.categories;	
										widget.config_fields.categories = [];
                }

                //get settings for chart types
                var chart_type = widget.chart_type;
                var series_settings = function(chart_type) {
                    var options = { type : 'pie',
                                    data : [],
                                    name : ""
                                  };
                    if (chart_type == "donut-chart") {
                        options['innerSize'] = '50%';
                        if (widget.config_fields.y_axis.length > 1) {
                            options['center'] = ['50%', '50%'];
                        }
                    } else if (chart_type == "bar-chart") {
                        options.type = 'column';
                    } else if (chart_type == "area-chart") {
                        options.type = 'area';
                    } else if (chart_type == 'polar-chart') {
                        options.type = 'area';
                    } else if (chart_type == 'line-chart') {
                        options.type = 'line';
                    } else if (chart_type == 'pie-chart') {
                        if (widget.config_fields.y_axis.length > 1) {
                            options['center'] = ['50%', '50%'];
                        }
                    }
                    return options;
                };

                var settings = series_settings(chart_type);

                    for (var idx = 0, arrLen = widget.config_fields.y_axis.length; idx < arrLen; idx++) {
                        var field = widget.config_fields.y_axis[idx];

                        //ensure we aren't put string type date in the y-axis
                        if(filter_numbers(field)){
                            var field_values = getFieldValues(field, widget.config_fields.x_axis, widget.raw_data);
                            if (field_values.x.length > 0) {
                                var row_settings = angular.copy(settings);
                                row_settings.name = field.key;

                                row_settings.data = field_values.y;

                                //if(widget.chart_options.options.chart.type === "column"){
																if(chart_type == "donut-chart" || chart_type == "pie-chart" ||
																		chart_type == "bar-chart"){
																	  //we need drilldown info to be avliable in the ajax call back so move them to chart_options 
																		widget.chart_options.options.chart.events = {drilldown: drilldownCB};
                                    widget.chart_options.options.dd = widget.config_fields.drilldown;

                                    row_settings.data = row_settings.data.map(function(value, itr){
																			  var has_drilldown = false;
																				if (widget.config_fields.drilldown) {
																					has_drilldown = widget.config_fields.drilldown.hasOwnProperty(field_values.x[itr]);
																				}
                                        return {name: field_values.x[itr] ,y: value, drilldown: has_drilldown};
                                    });                                    
                                }
                                //only need to store categories the first time, as they shouldn't change
                                //widget.chart_options.xAxis.categories = field_values.x;
																widget.config_fields.categories = field_values.x;
                                widget.chart_options.series.push(row_settings);                            
																console.log("data for chart is", widget);
														} else { console.log("fyi we didn't get any data for this one", widget); }                            
                        }else{
                            alert("Y-axis data should be numeric.");
                        }
                    }

            }
            return widget;
        };

        //since we don't store data with the data viz, we need to populate some data
        //if we are loading an existing data viz, so the build screen will work
        function updateAllCharts(viz,limit) {
            var dataLoadCalls = [];            
            angular.forEach(viz.widgets, function(widget) {
                //limit is now a property of the widget
                //but can still be overridden
                if (!limit) {
                  if (widget.config_fields.hasOwnProperty('datalimit')) {
                    limit = widget.config_fields.datalimit;
                  }
                }
                if (widget.viz_type.toUpperCase() == "CHART") {
                    //turn on chart loading, and hope somebody turns it off ;/
                    widget.chart_options.loading = true;
                    //TODO: this is pretty naive, we should filter, by the actual
                    //fields in the chart
                    angular.forEach(widget.viz_datasets, function(ds, idx) {
                        var order_by = "";
                        if (widget.config_fields && widget.config_fields.x_axis) {
                            order_by = widget.config_fields.x_axis.ds_fieldName;
                        }
                        dataLoadCalls.push(
                            mappdata.getData(ds.id,ds.group, limit, order_by)
                                .then(function(data) {
                                    //sum data based on 
                                    if (order_by) {
                                       var group_by = order_by; //sane naming
                                       var agg_data = [];
                                       //find datasets with same group_by name
                                       //and combine into one dataset with
                                       //y-axis fields summed
                                       for (var i = 0, len = data.length; i < len; i++) {
                                         var item = data[i];
                                         var agg_data_item = find_by_prop(order_by, item[order_by], agg_data); 
                                         if (!agg_data_item) {
                                           agg_data.push(angular.copy(item));
                                           continue;
                                         } else {
                                           //we have the item, so add to the sum
                                           var yaxis = widget.config_fields.y_axis;
                                           if (yaxis) {
                                             for (var j = 0, jlen = yaxis.length; j < jlen; j++) {
                                                var y_item = yaxis[j];
                                                var field_name = y_item['ds_fieldName'];
                                                if (! agg_data_item.hasOwnProperty(field_name)) {
                                                  agg_data_item[field_name] = 0;
                                                }
                                                agg_data_item[field_name] += item[field_name];
                                             }
                                           }
                                         } //end else
                                       } //end for
                                    }
                                    //end create sum aggregated

                                    //now update the chart    
                                    widget.raw_data[ds.id] = agg_data;
                                    updateChartFields(widget);
                                    widget.chart_options.loading = false;
                                    return widget;
                                })
                        );
                    });
                    // defer.resolve($q.all(dataLoadCalls));
                }
            });
            // return defer.promise;
            return $q.all(dataLoadCalls);
        }
    }

    
    dataviz.$inject = ["$http", "$location", "$q", "$filter", "mappdata", "charting", "mapping"];
    function dataviz($http, $location, $q, $filter, mappdata, charting, mapping){
        var api_root = '/api/v1/dataviz/';
        var currentviz = null;

        var basic_widget = {
            viz_type : "Chart",
            viz_datasets : [],
            chart_type : "bar-chart",
            chart_options : get_basic_defaults(),
            data_fields : [],
            raw_data: {},
            config_fields : {},
            show : true,
            title : ""
        };

        var basic_map_widget = {
            viz_type : "map",
            viz_datasets : [],
            chart_type : "",
            chart_options : {},
            data_fields : [],
            raw_data: {},
            config_fields : {},
            show : true,
            title : ""
        };                

        var service = {
            create_widget: create_widget,
            new_dataviz : new_dataviz,
            updateSelectedDatasets : updateSelectedDatasets,
            get: get,
            save: save,
            current_datasets: current_datasets,
            loadData: loadData,
        };

        return service;

        ///////////////////////////////////////////////////////
        // Implementation
        ///////////////////////////////////////////////////////

        function create_widget(){
            var default_widget = {};
            angular.copy(basic_widget, default_widget);
            return default_widget;
        }

        function save(viz){
            if (viz.id) {
                return $http.put(api_root + viz.id +"/" , viz);
            } else {
                return $http.post(api_root, viz);
            }
        }

        function current_datasets(){
            return currentviz.selected_external_ds.concat(currentviz.selected_internal_ds);
        }

        function loadData(id, cache, type) {
            var defer = $q.defer();
            if (typeof(cache) == "undefined") {
                cache = true;
            }
            //assume we have a hidden field containing the id:
            if (currentviz && cache) {
                defer.resolve(currentviz);
                return defer.promise;
            }

            if (typeof(id) == "undefined") {
                id = $("#dataviz-id").val();
            }

            //did we get a mongo id?
            if (!id || typeof(id) == "undefined") {
                //we are adding not updating
                var new_viz = new_dataviz(type);
                if (cache){
                    currentviz = new_viz;
                }
                defer.resolve(new_viz);
                return defer.promise;
            }else{
                get(id)
                    .then(function(data){
												data.data.widgets[0].chart_options.options.chart.events = {drilldown: charting.drilldownCB};
                        if (cache) {
                            currentviz = data.data;
                        }
                        updateConfigFields(data.data);
                        defer.resolve(data.data);
                    });
                return defer.promise;
            } //end else
        } //end loadData

        function new_dataviz(type){
            if (type === 'map'){
                mapping.restore_map_functions(basic_map_widget);
                return { group_name : "",
                         widgets : [basic_map_widget],
                         selected_external_ds : [],
                         selected_internal_ds : []
                       };
            }
            return { group_name : "",
                     widgets : [basic_widget],
                     selected_external_ds : [],
                     selected_internal_ds : []
                   };
        }

        function  get(id){
            return $http.get(api_root +id);
        }

        //used for loading up multi-select cause they don't load properly
        //unless you jump through some hoops
        function findById(list, id){
            var retval = -1;
            angular.forEach(list, function(item, idx) {
                if (item.id == id) {
                    retval = idx;
                }
            });
            return retval;
        }

        function updateConfigFields(viz) {

            //all the selected datasets
            var viz_ds = viz.selected_external_ds.concat(viz.selected_internal_ds);

            angular.forEach(viz.widgets, function(widget) {
                //update the selected datasets for the widget
                angular.forEach(widget.viz_datasets, function(ds, idx) {
                    var selected = findById(viz_ds, ds.id);
                    widget.viz_datasets[idx] = viz_ds[selected];
                });

                // it doesn't make sense to graph text with text, this filter ensures y-axis datasets
                // contain on number.                
                function filter_numbers(ds){return ds.name.indexOf("number") > 1 && angular.isNumber(ds.value);}

                //update x and y axis fields for charts                
                if (widget.viz_type.toLowerCase() == "chart") {
                    if (widget.config_fields.hasOwnProperty("x_axis")) {
                      var x_selected = findById(widget.data_fields,widget.config_fields.x_axis.id);
                      widget.config_fields.x_axis = widget.data_fields[x_selected];
                      widget.config_fields.y_axis = widget.config_fields.y_axis.filter(filter_numbers);
                    }
                    
                    //take care of the y-axis
                    /*angular.forEach(widget.config_fields.y_axis, function(field,idx) {
                     y_selected = findById(widget.data_fields, field.id);
            widget.config_fields.y_axis[idx] = widget.data_fields[y_selected];
          });
          */
                } else if (widget.viz_type.toLowerCase() == "table") {
                    //update col settings
                    angular.forEach(widget.config_fields.table_columns, function(col, idx) {
                        var col_data_field = findById(widget.data_fields, col.field.id);
                        col.field = widget.data_fields[col_data_field];
                    });
                } else if (widget.viz_type.toLowerCase() == "map") {
                    //redraw the map
                    mapping.restore_map_functions(widget);
                }
            });
            return viz;
        }

        function updateSelectedDatasets(viz,datasets,is_external) {
            //basically link up the datasets stored with the viz, with the list of datasets queried from the system
            var ds_type = "selected_internal_ds";
            if (is_external) {ds_type = "selected_external_ds";}

            angular.forEach(viz[ds_type], function(selected_ds,idx) {
                var selected = findById(datasets, selected_ds.id);
                viz[ds_type][idx] = datasets[selected];
            });
        }

        function get_basic_defaults() {
            var default_chart =  charting.get_chart_options('bar-chart');
            default_chart['series'] = charting.dummyChartData();
            return default_chart;
        }
		}

    TabsCtrl.$inject = ["$scope", "$rootScope", "$filter", "$location", "$q", "mappdata", "dataviz"];
    function TabsCtrl($scope, $rootScope, $filter, $location, $q, mappdata, dataviz) {

        $scope.tabs = [
            { link : '#/source', label : '1. Source'},
            { link : '#/build', label : '2. Build'},
            { link : '#/preview', label : '3. Preview'},
            { link : '#/publish', label : '4. Publish'},
        ];

        $scope.selectedTab = $scope.tabs[0];

        $scope.setSelectedTab = function(tab) {
            $scope.selectedTab = tab;
        };

        $scope.tabClass = function(tab) {
            if ($scope.selectedTab == tab) {
                return "active";
            } else {
                return "";
            }
        };
    }


    SourceCtrl.$inject = ["$scope", "$location", "$rootScope", "mappdata", "dataviz", "currentviz"];
    function SourceCtrl($scope, $location, $rootScope, mappdata, dataviz, currentviz) {

        $scope.currentviz = currentviz;

        $scope.setSelectedTab($scope.tabs[0]);
        $scope.hide_error = true;
        $scope.external_ds = [];

        mappdata.getExternalToplevels().then(function(data) {
            $scope.external_ds = data;
            dataviz.updateSelectedDatasets(currentviz, $scope.external_ds, true);
        });


        $scope.search_datasets = function(name) {
            if (!name) { return; }
            mappdata.getToplevels(name).then(function(data) {
                $scope.internal_ds = data;
                dataviz.updateSelectedDatasets(currentviz, $scope.internal_ds, false);
            });
        };

        $scope.submit = function() {
            var datasets = $scope.currentviz.selected_external_ds.concat($scope.currentviz.selected_internal_ds);
            if (datasets.length === 0) {
                $scope.hide_error = false;
                return;
            }
            $scope.hide_error = true;
            $location.path("/build");
        };
    }

    BuildCtrl.$inject = ["$window", "$scope", "$routeParams", "$filter", "$location", "$timeout",
                         "mappdata", "dataviz", "charting", "mapping", "currentviz", "DrilldownModalFactory",
                         "OptionsModalFactory"];
    
    function BuildCtrl ($window, $scope, $routeParams, $filter, $location, $timeout,
                        mappdata, dataviz, charting, mapping, currentviz, DrilldownModalFactory,
                        OptionsModalFactory) {

        $scope.setSelectedTab($scope.tabs[1]);
        $scope.currentviz = currentviz;
        $scope.current_datasets = dataviz.current_datasets();

        //just for the fun of it
        $scope.getWidgetIcon = function(widget) {
            switch (widget.viz_type.toUpperCase()) {
            case "TABLE":
                return "fa-table";
            case "CHART":
                switch(widget.chart_type.toLowerCase()) {
                case "pie-chart":
                    return "fa-pie-chart";
                case "bar-chart":
                    return "fa-bar-chart";
                case "area-chart":
                    return "fa-area-chart";
                case "line-chart":
                    return "fa-line-chart";
                case "donut-chart":
                    return "fa-life-ring";
                default:
                    return "fa-sliders";
                }
            case "MAP" :
                return "fa-map-marker";
            default:
                return "fa-sliders";
            }
        };

        //initialize stuff for Table
        $scope.yn = ['Yes', 'No'];

        var init_table_viz = function(widget) {
            if (! widget.config_fields.hasOwnProperty('table_columns') )
            {
                widget.config_fields.table_columns = [
                    {title: '', field: ''},
                    {title: '', field: ''},
                    {title: '', field: ''},
                    {title: '', field: ''},
                    {title: '', field: ''},
                ];
            }
        };

        $scope.addTableColumnRow = function(widget) {
            widget.config_fields.table_columns.push({title: '', field: ''});
        };

        $scope.removeTableColumnRow = function(widget) {
            widget.config_fields.table_columns.pop();
        };


        //this will run when contoller is first loaded,
        //its necessary to force charts to redraw when we are
        //updating an existing visualization
        $timeout(function() {
            var updateAllFields = function() {
                //just update the fields so charts will redraw
                
                angular.forEach(currentviz.widgets, function(widget) {
                    if (widget.viz_type.toUpperCase() == "CHART") {
                        charting.updateChartFields(widget);
                    } else if (widget.viz_type.toUpperCase() == "MAP") {
                        mapping.plotSystemData(widget);
                    }
                });
            };

            //if we don't have data yet, let's get some
            if (Object.keys(currentviz.widgets[0].raw_data).length === 0)
            {

                    var widget = currentviz.widgets[0];
                    if (widget.viz_type.toUpperCase() == "CHART") {
                      charting.updateAllCharts(currentviz);
                    } else if (widget.viz_type.toUpperCase() == "MAP") {
                        mapping.plotSystemData(widget);
                    }
            }else {
                updateAllFields();
            }
        }, 200);

        //widget tool bar
        $scope.add_widget = function()
        {
            angular.forEach(currentviz.widgets, function(widget) {
                widget.show = false;
            });
            currentviz.widgets.push(dataviz.create_widget());
        };

        $scope.toggle_vis = function(widget){
            widget.show = !widget.show;
        };
        $scope.delete_widget = function(widget){
            var index = currentviz.widgets.indexOf(widget);
            currentviz.widgets.splice(index, 1) ;
        };
        $scope.limit_data = function(widget, currentviz){
            if (!widget.config_fields.hasOwnProperty('datalimit')) {

              widget.config_fields['datalimit'] = 250;
            }
            OptionsModalFactory.open_modal(widget, currentviz);
        };

        //select data source
        $scope.addDataFields = function(item, widget){
            //add fields from data source to master list of all fields
            //keep info about which datasource the field belongs to
            if (isMap(widget)) {
                mapping.plotSystemData(widget);
                return;
            }
            var order_by = null;
            if (widget.config_fields && widget.config_fields.x_axis) {
                order_by = widget.config_fields.x_axis.ds_fieldName;
            }
            mappdata.getData(item.id, item.group, 10, order_by).then(function(data) {
                angular.forEach(data[0], function(value, key) {
                    //get list of values for sample chart
                    var field = {name: key + " - ( " + item.name + " ) - [" + typeof(value) + "]",
                                 key: key,
                                 value: value,
                                 id : item.id + "." + key,
                                 ds_id : item.id,
                                 ds_fieldName : key,
                                 group : item.group};
                    widget.data_fields.push(field);
                });
                //store the data
                widget.raw_data[item.id] = data;
            });
        };

        $scope.removeDataFields = function(item, widget){
            //delete widget.data_fields belonging to the removed data set
            if (isMap(widget)) {
                mapping.plotSystemData(widget);
                return;
            }
            widget.data_fields = $filter('filter')(widget.data_fields,
                                                   function(value, index){
                                                       return item.id != value.id.split(".")[0];
                                                   }
                                                  );
            //remove associated data
            delete widget.raw_data[item.id];
        };

        //viz type
        $scope.isActive = function(widget, vizType){
            if (widget && widget.viz_type && vizType) {
                return widget.viz_type.toLowerCase() == vizType.toLowerCase();
            }
            return false;
        };

        $scope.activeClass = function(widget, vizType) {
            var classes = "btn btn-default";
            if ($scope.isActive(widget, vizType)) {
                classes += " active";
            }
            return classes;
        };

        //it seems that the label wrapping the radio input is stealing
        //the click event, causing ng-model to not function correctly
        //let's manually set it here
        $scope.setActive = function(widget, viztype){
            widget.viz_type = viztype;
            if (viztype == 'table') {
                init_table_viz(widget);
            } else if (viztype == 'map') {
                mapping.plotSystemData(widget);
            }
        };


        //charting stuff start here
        $scope.chart_types = charting.chart_types;

        $scope.updateChartType = function(widget){
            widget.chart_options = charting.get_chart_options(widget.chart_type);
            widget.chart_options.title.text = widget.title;
            $scope.updateBarChartXAxis(widget);
        };

        $scope.showChart = function(widget, chart_type){
            if (widget && widget.chart_type && chart_type){
                return widget.chart_type.toLowerCase() == chart_type.toLowerCase();
            }
            return false;
        };

        //update data on temporary chart
        $scope.updateBarChartFields = function(item, widget) {
            charting.updateAllCharts($scope.currentviz);
            //charting.updateChartFields(widget);
        };

        //update x axis on temporary chart
        $scope.updateBarChartXAxis = function(widget) {
            if (widget.config_fields.x_axis) {
                if (widget.chart_type != "polar-chart") {
                    widget.chart_options.xAxis.title.text = widget.config_fields.x_axis.key;
                }
                $scope.updateBarChartFields(null, widget);
            }
        };

        $scope.updateChartTitle = function(widget) {
            widget.chart_options.title.text = widget.title;
            //$scope.updateBarChartFields(null, widget);
        };

				$scope.can_drilldown_chart = function(chart_type) {
					var can = false;
					if (chart_type == 'bar-chart' || chart_type == 'pie-chart' || chart_type == 'donut-chart') {
						can = true;
					}
					return can;
				};
				
        $scope.open_drilldown_modal = function(){
            DrilldownModalFactory.open_modal($scope.currentviz);
        };

        //move on to preview
        $scope.submit = function() {
            if(!$scope.currentviz.group_name){
                $window.alert("Please add enter a 'Group Name' before continuing");
            }else{
                $location.path("/preview");
            }
        };
        
    }


    PreviewCtrl.$inject = ["$scope", "$routeParams", "$log", "$location",
                           "$q", "$timeout", "dataviz", "mappdata", "charting", "currentviz"];
    
    function PreviewCtrl($scope, $routeParams, $log, $location,
                         $q, $timeout, dataviz, mappdata, charting, currentviz) {

        $scope.setSelectedTab($scope.tabs[2]);
        $scope.currentviz = currentviz;

        function  setVizId(data) {
            currentviz.id = data.data.id;
            currentviz.short_url = data.data.short_url;
        }

        function  goToPublish() {
            $location.path("/publish");
        }

        $scope.submit = function() {
            //save the current viz
            //but first remove a few unnecessary pieces
            angular.forEach(currentviz.widgets, function(widget) {
                widget.chart_data = [];
                widget.raw_data = {};
                delete widget.fullDataLoaded;
            });

            dataviz.save(currentviz)
                .then(setVizId)
                .then(goToPublish)
                .catch(function(e){
                    $scope.duplicate_name_error = e.data.error;
                });
        };
      }


    PublishCtrl.$inject = ["$scope", "$routeParams", "$log", "currentviz", "$http", "$location", "$window"];
    
    function PublishCtrl($scope, $routeParams, $log, currentviz, $http, $location, $window) {

        $scope.setSelectedTab($scope.tabs[3]);
        $scope.currentviz = currentviz;
        $scope.msg = "Check out this awesome data vizualisation I just created with Mapps";

        $scope.shortUrl = currentviz.short_url;

        $scope.sendMail = function(msg, url)
        {
            msg = window.encodeURIComponent(msg);
            url = window.encodeURIComponent(url);
            window.location.href = "mailto:?subject=Awesome%20Dataviz&body=" + msg + " " + url;
        };
    }

    DataVisualizationController.$inject = ["mappdata", "$log", "$window"];
    function DataVisualizationController(mappdata, $log, $window){
        var vm = this;
        vm.delete_viz = delete_viz;
        vm.set_id = set_id;

        ///////////////////////////////////////////////////////
        // Public
        ///////////////////////////////////////////////////////

        activate();

        ///////////////////////////////////////////////////////
        // Implementation
        ///////////////////////////////////////////////////////

        function set_id(id){
            vm.selected_viz = id;
        }

        function delete_viz(){
            mappdata.deleteDataViz(vm.selected_viz).then(function(data){
                $log.info("Visualization deleted successfully");
                $window.location.reload();
            });
        }
        
        ///////////////////////////////////////////////////////
        // Initializes controller data
        function activate() {

            
        }                
    }

    function previewViz() {
        return {
            restrict: 'EA',
            scope: {
                currentviz : '=?viz',
                vizid : '@',
                cache : '@',
                widgetnum : '@',
                showtabs : '@',
                preview : '@'
            },
            controller: PreviewVizController,
            template: "<ng-include src='getTemplateUrl()'/>"
        };

        function PreviewVizController($scope, $element, charting, dataviz, mappdata,
                                      $timeout, $q, mapping) {

            //covert cache scope param to boolean
            if ($scope.cache === 'false') { $scope.cache = false;}
            //Table stuff

            //TODO: break this out into a factory
            var getListOfDatasetsFromFields = function(table_columns) {
                var dslist = {}; //we need set like functinality
                var dsnames = [];
                var dsfields = {};
                var fields = [];
                angular.forEach(table_columns, function(column, idx) {
                    //get list of ids of datasets
                    if(column.field) {
                        if (!dslist.hasOwnProperty(column.field.ds_id)){
                            dslist[column.field.ds_id] = 1;
                            dsnames.push(column.field.ds_id);
                        }
                        //get list of fields
                        if (!dsfields.hasOwnProperty(column.field.ds_fieldName)){
                            dsfields[column.field.ds_fieldName] = 1;
                            fields.push(column.field.ds_fieldName);
                        }
                    }
                });
                return {datasets: dsnames, fields : fields};
            };

            $scope.loadTableData = function loadTableData(tableState) {
                $scope.isLoading = true;
                var pagination = tableState.pagination;
                var start = pagination.start || 0;
                var number = pagination.number || 10;
                var page = (start + 10) / number;
                var filter = "";
                if (tableState.search.predicateObject) {
                    filter = tableState.search.predicateObject.$;
                }

                var order_by = "";

                if (tableState.sort.predicate) {
                    if (tableState.sort.reverse){
                        order_by = "-";
                    }
                    order_by += tableState.sort.predicate.replace(/\'/g, "");
                }

                //get out data
                var widget = $scope.selectedWidget;
                var dslist = getListOfDatasetsFromFields(widget.config_fields.table_columns);
                mappdata.getBulkData(dslist.datasets, page, number, filter, dslist.fields, order_by)
                    .then(function(data){
                        $scope.selectedWidget.chart_data = data.data.results;
                        $scope.selectedWidget.display_data = [].concat(data.data.results);
                        tableState.pagination.numberOfPages = Math.ceil(data.data.count / number);
                    });
            };

            var setup = function() {
                if (! $scope.currentviz) {return;}
                $scope.selectedWidget = $scope.currentviz.widgets[0];
                if (isMap($scope.selectedWidget)) {
                    mapping.plotSystemData($scope.selectedWidget);
                } else {
                    charting.updateAllCharts($scope.currentviz);
                }
            };

            //THIS is initial action
            //if we get vizid, grab the data first
            function startup() {
                if ($scope.vizid) {
                    dataviz.loadData($scope.vizid, $scope.cache).then(function (viz) {
                        //handle widget num
                        if (typeof(widgetnum) != 'undefined') {
                            viz.widgets = [viz.widgets[parseInt(widgetnum)]];
                        }
                        $scope.currentviz = viz;
                    }).then(setup);
                } else {
                    setup();
                }
            };
            startup();

            $scope.showWidget = function(widget) {
                $scope.selectedWidget = widget;
                //no need to do anything for highmaps... they just work :)
                if (isMap(widget)) {
                    //with tabs maps drawn off scren, are broken, we have to force
                    //a complete update for it to display correctly
                    mapping.clearLayers(widget);
                    widget.chart_options.refresh_map = true;
                    $timeout(function() {
                        //widget.chart_options.refresh_map = true;
                        mapping.plotSystemData(widget);
                    }, 200);
                }
            };

            $scope.setActiveClass = function(widget) {
                if ($scope.selectedWidget == widget) {
                    return "active";
                } else {
                    return "";
                }
            };

            $scope.getTemplateUrl = function () {
                if ($scope.showtabs) {
                    return "/maps-admin/resources/partials/viz_infographic";
                }
                return "/maps-admin/data/partials/viz_widget";
            };

            //watch for changes to $scope.vizid
            $scope.$watch(function() {
                return $scope.vizid;
            }, function() {
                if ($scope.vizid) {
                    startup();
                }
            });

            //and to viz
            $scope.$watch(function() {
                return $scope.currentviz;
            }, function() {
                setup();
            });
        }
    }

    function dsInfo() {
        return {
            restrict: 'EA',
            scope: {
                ds: '=dsInfo',
                source: '=dsSource',
                index: '=dsIndex'
            },
            link: function(scope, elem, attrs){
                scope.removeds = function() {
                    scope.source = scope.source.filter(function (el) {
                        return el.id != scope.ds.id;
                    });
                };
                //scope.ds.range = [];
            },
            template:
            "<div class='row dataset-block'>"+
                "<div class='col-sm-2'>" +
                "<a ng-click='removeds()' class='btn btn-default btn-sm'>" +
                "<i class='fa fa-close'></i> </a>" +
                "</div>" +
                "<div class='col-sm-5'><h4>[[ds.name]]</h4>" +
                "<p>[[ds.description]]</p></div>"+
                "</div>"            
            
        };
    }

    datavizConfig.$inject = ["$interpolateProvider", "$routeProvider", "$httpProvider"];
    function datavizConfig($interpolateProvider, $routeProvider, $httpProvider) {

        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

        $routeProvider.
            when('/source', {templateUrl: 'partials/addvisualization-source',
                             controller: "SourceCtrl",
                             resolve: {
                                 currentviz: vizPrep
                             }
                            }).
            when('/build', {templateUrl: 'partials/addvisualization-build',
                            controller: "BuildCtrl",
                            resolve: {
                                currentviz: vizPrep
                            }
                           }).
            when('/preview', {templateUrl: 'partials/addvisualization-preview',
                              controller: "PreviewCtrl",
                              resolve: {
                                  currentviz : vizPrep
                              }
                             }).
            when('/publish', {templateUrl: 'partials/addvisualization-publish',
                              controller: "PublishCtrl",
                              resolve: {
                                  currentviz : vizPrep
                              }
                             }).
            otherwise({redirectTo: '/source'});
    }

    vizPrep.$inject = ["dataviz"];
    function vizPrep(dataviz) {
        return dataviz.loadData();
    }


    DrilldownModalFactory.$inject = ["$modal", "$rootScope"];
    function DrilldownModalFactory($modal, $rootScope) {
        var service = {};

        function open_modal(currentviz) {
            var modalInstance = $modal.open({
                animation: false,
                templateUrl: '/maps-admin/data/partials/modal-drilldown',
                controller: 'DrilldownModalController',
                controllerAs: 'vm',
                resolve: {
                    currentviz: function() {
                        return currentviz;
                    }
                }
            });
        }

        service.open_modal = open_modal;

        return service;
    }

    DrilldownModalController.$inject = ['$scope', '$modalInstance', 'mappdata', "dataviz", "currentviz"];
    function DrilldownModalController($scope, $modalInstance, mappdata, dataviz, currentviz) {
        var vm = this;
        vm.currentviz = currentviz;
        vm.xaxis = get_xaxis_fields;
        vm.allDataViz = [];
        vm.selectedDrillDown = vm.currentviz.widgets[0].config_fields.drilldown || {};
        vm.save = save;
        vm.close = close;
        function __init__(){
            get_all_dataviz();
        }
        __init__();

        function get_xaxis_fields(){
            var fields = vm.currentviz.widgets[0].config_fields.categories;
            return fields;
        }

        function get_all_dataviz(){
            mappdata.getAllViz().then(function(result){
               vm.allDataViz = result.data;
            });
        }

        function close() { $modalInstance.close(); }

        function save(){
             vm.currentviz.widgets[0].config_fields.drilldown = vm.selectedDrillDown;
             // set_drilldown_values(vm.currentviz);
             dataviz.save(vm.currentviz).then(function(result){
                     $modalInstance.close();
                 }
             );
        }
    }

    OptionsModalFactory.$inject = ["$modal", "$rootScope"];
    function OptionsModalFactory($modal, $rootScope) {
        var service = {};

        function open_modal(widget,currentviz) {
            var modalInstance = $modal.open({
                animation: false,
                templateUrl: '/maps-admin/data/partials/modal-options',
                controller: 'OptionsModalController',
                controllerAs: 'vm',
                resolve: {
                    widget: function() {
                        return widget;
                    },
                  currentviz: function() {
                    return currentviz;
                  }
                }
            });
        }

        service.open_modal = open_modal;

        return service;
    }

    OptionsModalController.$inject = ['$scope', '$modalInstance', "widget",
                                      'currentviz',"charting"];
    function OptionsModalController($scope, $modalInstance, widget,currentviz,charting) {
        var vm = this;
        vm.ok = ok;
        vm.close = close;

        vm.widget = widget;


        function close() { $modalInstance.close(); }
        
        function ok(){
          $modalInstance.close();
          charting.updateAllCharts(currentviz);
        }
    }
})();
