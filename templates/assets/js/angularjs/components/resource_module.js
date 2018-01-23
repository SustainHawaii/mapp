(function(){
    'use strict';
    angular.module('ResourceModule', ['mapp_data','datavizApp'])
        .controller('ResourceController', ResourceController)
        .controller('ResourceSettingsController', ResourceSettingsController)
        .controller('AddVisualizationModalController', AddVisualizationModalController)
        .factory('AddVisualizationModalFactory', AddVisualizationModalFactory)
        .factory('InfographicLayoutFactory', InfographicLayoutFactory)
        .factory('ResourceManagerFactory', ResourceManagerFactory)
        .directive('infographicLayout', infographicLayout)
        .directive('backImg', backImg);

    ResourceController.$inject = ['$scope', '$window', 'TrueFalse', 'AddVisualizationModalFactory', 'InfographicLayoutFactory',
                                  'ResourceManagerFactory', 'dataviz', 'mappdata', 'mapping'];

    function ResourceController($scope, $window, TrueFalse, AddVisualizationModalFactory, InfographicLayoutFactory,
                                ResourceManagerFactory, dataviz, mappdata, mapping) {

        $scope.tf = TrueFalse;
        $scope.resource = {};

        /**
         * the following is specific to front-end resource view
         **/
        $scope.allViz = {};
        $scope.filtered_viz ={};
        $scope.allResources = {};
        $scope.location_types = {};
        $scope.first_level = {'active':'none'};
        $scope.second_level = {'active':false};
        $scope.third_level = {'active':false};
        $scope.show_page_order = false;
        $scope.all_sort_options = {'location':[
          {name: 'Latest', sort: 'properties.last_updated'},
          {name: 'A to Z', sort: 'properties.name'},
          {name: 'Z to A', sort: '-properties.name'},
          {name: 'Featured', sort:'properties.featured'},
          {name: 'Claimed' , sort: 'properties.claimed'},
        ],
        'dataviz':[
          {name: 'Latest', sort: 'last_updated'},
          {name: 'A to Z', sort: 'group_name'},
          {name: 'Z to A', sort: '-group_name'},
        ],
        'resources':[
          {name: 'Latest', sort: 'last_updated'},
          {name: 'A to Z', sort: 'name'},
          {name: 'Z to A', sort: '-name'},
        ]
                                  };

				$scope.show_list = function(active) {
					if (active === $scope.first_level.active){ 
						return true;
				}
				}
        $scope.menu_toggle = function (active, subfilter){
          if (active == 'dataviz') {
              prep_dataviz_menu(subfilter);
            //for dataviz, don't close second level if we have a subfilter
            //just filter
            if (subfilter) {
              $scope.second_level.active = true;
            } else {
              $scope.second_level.active = !$scope.second_level.active;
            }
          } else if (active != 'page_order') {
						$scope.second_level.active = !$scope.second_level.active;
						if ($scope.second_level.active) {
							$scope.first_level.active=active;
						} else {
							$scope.first_level.active = 'none';
						}
          } 

          $scope.search = '';
          //$scope.first_level.active=active;
          $scope.sort_options = $scope.all_sort_options[active];
          $scope.third_level.active=false;
          //$scope.active_item = {};
          if(active==='page_order'){
            $scope.second_level.active = false;
            page_order();
          }
        };

        $scope.hide_this = function() {
          $scope.first_level.active = true;
          $scope.second_level.active = false;
          $scope.third_level.active = false;
        };

        $scope.hide_page_order = function() {
          $scope.show_page_order = false;
        };

        function prep_dataviz_menu(subfilter) {
          //filter based on subfilter
          if (subfilter) {
            $scope.filtered_viz = $scope.allViz.filter(
              function(e){
                  if (e.widgets && e.widgets[0]) {
                    return e.widgets[0].viz_type.toLowerCase() === subfilter;
                  }
              });
          } else {
            $scope.filtered_viz = $scope.allViz;
          }
        }


        $scope.activate_third_level = function (item, id){
            console.log("active item is", item, id);
            //set size of charts to ensure they fit in the space
            if (item.hasOwnProperty('widgets')) {
               if (item.widgets[0].viz_type.toLowerCase() == 'chart') {
                  item.widgets[0].chart_options.size = {
                                                   width: 400,
                                                   height: 300
                                                  };
               }
            }
            $scope.add_to_infographic_checked = false;
            $scope.third_level.active = true;
            $scope.active_item = item;

            $scope.add_to_infographic_btn_text = "Add to layout";
            $scope.can_add = true;
            if(id) {
              var idx = InfographicLayoutFactory.is_in_layout(id);
              if (idx > -1) {
                $scope.add_to_infographic_btn_text = "Added to layout position " + idx;
                $scope.can_add = false;
              }
            }          
        };

        $scope.add_to_infographic = function(){
            if (!$scope.can_add) { return;}
            $scope.add_to_infographic_checked = true;
            var id, name, type;
            if ($scope.first_level.active == 'location') {
              id = $scope.active_item.properties.id;
              name = $scope.active_item.properties.name;
              type = "location";
            }else if ($scope.first_level.active == 'dataviz') {
              id = $scope.active_item.id;
              name = $scope.active_item.group_name;
              type = "dataviz";
            }
            var idx = InfographicLayoutFactory.add_item(id, name, type);

            //set the message saying it was added
            $scope.add_to_infographic_btn_text = "Added to layout position " + idx; 
            $scope.can_add = false;
        };

        function page_order (){
            $scope.show_page_order = !$scope.show_page_order;
        }

        $scope.go_fullscreen = function() {
          if (!($scope.resource.name && $scope.resource.id)) {
            alert("Please save the resource before you can view fullscreen");
          } else {
            $window.location.href = ("/maps-admin/resources/fs-resources/" + $scope.resource.id);
          }
        };

        /**
         * end front-end specific shizzle
         **/


        $scope.save_dashboard_resource = function(resource) {
          resource.name = "Dashboard for " + $scope.user.full_name;
          console.log(resource);
          $scope.save_resource(resource).then(function(data) {
            console.log("saved resource with data as", data.data);
            $scope.user.dashboard_resource_id = data.data.id;
            //$scope.user.organization = null;
            //$scope.user.user_types = null;
            mappdata.patchUser({id : $scope.user.id, 
                                dashboard_resource_id : data.data.id});
            $scope.dashboard_saved = true;
          });
        };

        $scope.hide_dashboard_saved_msg = function() {
          $scope.dashboard_saved = false;
        };

        $scope.save_resource = function (resource, redirect) {
            //defaults to no redirect
            if (typeof(redirect) == 'undefined') {
              redirect = false;
            }
                return ResourceManagerFactory.save(resource, $scope.file)
                    .success(function(data){
                      if (redirect) {
                        $window.location.href = ("/maps-admin/resources/all-resources");
                      }else {
                        //update urls for file
                        $scope.resource.page_background_url = data.page_background_url;
                        $scope.resource.page_logo_url = data.page_logo_url;
                        $scope.resource.id = data.id;
                        
                        //we saved the files, don't save them again
                        $scope.file = {};
                        return $scope.resource;
                      }
                    }).error(function(e){
                        if(e.indexOf('duplicate' > 1)){
                            $scope.duplicate_name_error = "This name is taken";
                        }
                    });
                
        };

        //TODO: this can be reused as is with front end
        $scope.load_resource = function (id) {
            console.log("loading resource no idea");
            if(id){
                console.log("loading resource");
                ResourceManagerFactory.load(id)
                .success(function(data){
                    console.log(data);
                    $scope.resource=data;
                    InfographicLayoutFactory.set_layout(data.layout);
                    if (data.main_map) {
                        $scope.widget = $scope.resource.main_map.widgets[0];
                        mapping.restore_map_functions($scope.widget);
                    }
                })
                .error(function(){
                  //just create one
                  //
                  dataviz.loadData(false, true, 'map').then(function(data) {
                    $scope.resource = {main_map: data};
                    //not sure why it doesn't want to set options, let's try here
                    console.log("my widget", $scope.resource.main_map.widgets[0]);
                    $scope.widget = $scope.resource.main_map.widgets[0];
                    $scope.resource.id = id;
                  });
                });
            } else {
              //we always want to load data for dataviz as loaddata will build
              //the structure that we need as well
              dataviz.loadData(false, true, 'map').then(function(data) {
                $scope.resource = {main_map: data};
                //not sure why it doesn't want to set options, let's try here
                console.log("my widget", $scope.resource.main_map.widgets[0]);
                $scope.widget = $scope.resource.main_map.widgets[0];
              });
            }
        };

        $scope.delete_resource = function (id) {
            mappdata.deleteResource(id)
                .success(function(){
                    $window.location.href = ("/maps-admin/resources/all-resources");
                })
                .error(function(){});
        };

        $scope.show_loc_on_map = function() {
          //update the map to show selected widgets
          //console.log($scope.resource.main_map);
          mapping.plotSystemData($scope.widget);
        };


        $scope.printIt = function(){
           // var table = document.getElementById('printArea').innerHTML;
           // var myWindow = $window.open('', '', 'width=800, height=600');
           // myWindow.document.write(table);
           window.print();
        };

        //TODO: this should be reused
        $scope.addfile = function (files, source) {
            if (files && files.length) {
                var file = files[0];
                if(source==='logo'){
                    $scope.resource.page_logo = file.name;
                }else{
                    $scope.resource.page_background = file.name;    
                }
                //$scope.uploaded = true;
                $scope.file = file;
                $scope.save_resource($scope.resource);
            }
        };

        //TODO: this should be reused
        function getAllLocationTypes() {
            mappdata.getLocationTypes("simple")
                .success(function(data) {
                    $scope.location_types = data.results;
                })
                .error(function() {});
        }

        //TODO: this should be reused
        function getAllViz(){
            mappdata.getAllViz()
                .success(function(data){
                    $scope.allViz = data;
                })
                .error(function(){});
        }

        function getAllResources(){
          mappdata.getAllResources()
          .success(function(data){
              $scope.allResources = data;
              $scope.load_resource($scope.allResources[0].id);                          
          })
          .error(function(){

          });
        }

        //load_resource is called through ng-init from template
        //$scope.load_resource();
        $scope.init_frontend = function() {
          getAllLocationTypes();
          getAllViz();
          getAllResources();
        };
        $scope.init_backend = function(id) {
          $scope.load_resource(id);
          getAllLocationTypes();
          getAllViz();
        };
        $scope.init_dashboard = function(user_id, resource_id){
          $scope.init_backend(resource_id);
          mappdata.getUser(user_id).then(function(data) {
            console.log("we got user with data", data);
            $scope.user = data.data;
          });
        };

        //used by dashboard view to add a row
        $scope.dashboard_add_row = function() {
          InfographicLayoutFactory.append_empty(1);
          InfographicLayoutFactory.append_empty(2);
          InfographicLayoutFactory.append_empty(3);
        };

    }

    ResourceSettingsController.$inject = ['$scope', 'TrueFalse', 'mappdata'];
    function ResourceSettingsController($scope, TrueFalse, mappdata) {
        $scope.settings = {};
        $scope.location_types = {};
        $scope.tf = TrueFalse;

        $scope.submit = function() {
            if ($scope.settings_id) {
                mappdata.updateResourceSettings($scope.settings);
                return;
            }
        };

        $scope.get = function(id) {
            if (id) {
                $scope.settings_id = id;
                mappdata.getResourceSettings(id)
                    .success(function(data, status) {
                        $scope.settings = data;
                    })
                    .error(function() {});
            }
        };

        function getLocationTypes() {
            mappdata.getLocationTypes("simple")
                .success(function(data) {
                    $scope.location_types = data.results;
                })
                .error(function() {});
        }

        getLocationTypes();

    }

    ChangeBracketSyntax.$inject = ['$interpolateProvider'];

    function ChangeBracketSyntax($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }

    AddVisualizationModalFactory.$inject = ['$modal', '$rootScope'];

    function AddVisualizationModalFactory($modal, $rootScope) {
        var service = {};

        function open_modal(index) {
            var modalInstance = $modal.open({
                animation: false,
                templateUrl: '/maps-admin/resources/partials/modal-add-visualization',
                controller: 'AddVisualizationModalController',
                controllerAs: 'vm',
                resolve: {
                    index: function() {
                        return index;
                    },
                }
            });

            modalInstance.result.then(function() {},
                function() {
                    $rootScope.$emit('InfographicLayout');
                });
        }

        service.open_modal = open_modal;

        return service;
    }

    AddVisualizationModalController.$inject = ['$scope', '$modalInstance', 'mappdata', 'InfographicLayoutFactory', 'index'];
    function AddVisualizationModalController($scope, $modalInstance, mappdata, InfographicLayoutFactory, index) {

        $scope.add_item = function(id, name, type) {
            console.log(index);
            InfographicLayoutFactory.add_item(id, name, type, index);
            //close the modal
            $modalInstance.close("done"); 
        };

        ///////////////////////////////////////////////////////
        // Init
        ///////////////////////////////////////////////////////

        function __init__(){
            getAllViz();
            getAllLoc();
        }

        __init__();

        ///////////////////////////////////////////////////////
        // Implementation
        ///////////////////////////////////////////////////////

       function getAllViz() {
            console.log("get all viz", $scope);
            if (!$scope.allViz) {
                mappdata.getAllViz()
                    .success(function(data) {
                        $scope.allViz = data;
                    })
                    .error(function() {});
            }
        }
       
        function getAllLoc() {
            if (!$scope.allLocations) {
                mappdata.getLocations()
                    .success(function(data) {
                        $scope.allLocations = data.results;
                    })
                    .error(function() {});
            }
        }
    }

    /***
     * Resource Manager Factory is responsible for loading and saving resources
     */
    ResourceManagerFactory.$inject = ['InfographicLayoutFactory', 'mappdata', 'dataviz'];

    function ResourceManagerFactory(InfographicLayoutFactory, mappdata, dataviz){
        var service = {};

        function save (resource, file) {
            resource.layout = InfographicLayoutFactory.get_layout();
            //ngRepeat adds some extra stuff to layout lets remove it
            resource = angular.copy(resource); 

            //seems like not all resources are created equal
            if (!resource.hasOwnProperty('main_map')) { 
              console.log("we don't have a main_map");
              return dataviz.loadData(false, true, 'map').then(function(data) {
                resource['main_map'] = data;
                return mappdata.saveResource(resource, file);
              });
            }
              var map_widget = resource.main_map.widgets[0];

              //also we don't save the raw_data so remove it
              if (map_widget.hasOwnProperty('raw_data')){
                delete map_widget.raw_data;
              }
              //widget should be a map type, early version of the code weren't setting this properly
              //set it here so we can "repair" those
              map_widget.viz_type = "map";

              //also we want to ensure that main_map doesn't appear in normal searches for dataviz so set the flag here
              resource.main_map.hidden = true;
              
              //finally make sure our dataviz has a name
              if (!resource.main_map.group_name) {
                resource.main_map.group_name = resource.name;
              }
            if(resource.id){
                return mappdata.updateResource(resource, file);
            }
            return mappdata.saveResource(resource, file);
        }

        function load (id) {
            return mappdata.getResource(id);
        }

        service.save = save;
        service.load = load;
        return service;

    }

    /***
     * InfographicLayout Factory deals with the ordering of the display items (dataviz or locations)
     * that are to be included with a resource.
     */

    InfographicLayoutFactory.$inject = [];

    function InfographicLayoutFactory() {
        var layout = [0,1,2];
        var active_cell = 0;
        var service = {};

        function add_item(id, name, type, idx)
            {
              if (typeof(idx) === 'undefined') {
                if (active_cell) {
                    idx = active_cell;
                } else {
                  idx = get_first_empty_cell();
                }
              }
                var cell = {
                    'id':id,
                    'name': name,
                    'type':type,
                    'size':4
                };
                layout[idx]=cell;
                console.log('added item, here is the layout',layout);
                return idx;
            }

        function append_empty(extra) {
          layout.push(new Date().getUTCMilliseconds() + extra);
        }

        function get_first_empty_cell() {
          for (var i = 0; i < layout.length; i++) {
            if (! layout[i].hasOwnProperty('id')) {
              return i;
            }
          }
          return i;
        }

        function is_in_layout(id) {
          for (var i = 0; i < layout.length; i++) {
            var item = layout[i];
            if (item && item.hasOwnProperty('id') && item.id == id) {
              return i;
            }
          }
          return -1;
        }
                
        function get_layout() {
            return layout;
        }

        function set_layout(data) {
            layout=data;
        }

        function set_active_cell(index) {
            active_cell = index;
        }

				function get_active_cell() {
					return active_cell;
				}


        function remove(index) {
          //use the date to prevent duplicates so ng-repeat doesn't comlain
						if (layout.length > 1) {
							layout.splice(index,1);
						}else {
							layout[index] = new Date().getUTCMilliseconds();
						}
        }

        service.add_item = add_item;
        service.get_layout = get_layout;
        service.set_layout = set_layout;
				service.get_active_cell = get_active_cell;
        service.set_active_cell = set_active_cell;
        service.get_first_empty_cell = get_first_empty_cell;
        service.is_in_layout = is_in_layout;
        service.remove = remove;
        service.append_empty = append_empty;

        return service;

    }

    infographicLayout.$inject = ['InfographicLayoutFactory'];
    /* @ngInject */
    function infographicLayout (InfographicLayoutFactory) {
        // Usage:
        //
        // Creates:
        //
        var directive = {
            
            bindToController: true,
            controller: Controller,
            controllerAs: 'vm',
            restrict: 'EA',
            /* we want full path as we use this in many places */
            templateUrl: '/maps-admin/resources/partials/infographic',
            scope: {
            }
        };
        return directive;

        
    }

    Controller.$inject = ['InfographicLayoutFactory', '$scope','AddVisualizationModalFactory',
    '$attrs'];
    function Controller (InfographicLayoutFactory, $scope, AddVisualizationModalFactory, $attrs) {
        var vm = this;
        vm.preview = angular.isDefined($attrs.preview) ? $attrs.preview : false;
        vm.noheader = angular.isDefined($attrs.noheader) ? $attrs.noheader : false;
        vm.showcontrols = angular.isDefined($attrs.showcontrols) ? $attrs.showcontrols : false;
        //vm.preview = $scope.preview;
        //vm.noheader = $scope.noheader;
        //vm.showcontrols = $scope.showcontrols;
        
        console.log(vm.preview);
        console.log(vm.noheader);
        console.log(vm.showcontrols);

        function get_size_class(item) {
          if (item && item.size) {
            return "col-sm-" + item.size;
          } else {
              return "col-sm-4";
          }
        }

        function add_row() {
          InfographicLayoutFactory.append_empty(1);
          InfographicLayoutFactory.append_empty(2);
          InfographicLayoutFactory.append_empty(3);
        }

        function shrink(item) {
          if (item && item.size) {
            if (item.size > 4) {
              //add a little somethign to append_empty so if we call
              //it in a loop, it won't created duplicates in the list
              InfographicLayoutFactory.append_empty(item.size);
              item.size -= 4;
            }
              //sanity checks
              if (item.size < 4){
                item.size = 4;
              }
            }
        }
        
        function expand(item) {
          if (item && item.size) {
            //sacrifice a kitten to feed expansion
            if (item.size < 12) {
              var kitten = InfographicLayoutFactory.get_first_empty_cell();
              InfographicLayoutFactory.get_layout().splice(kitten,1);
              item.size += 4;
            }
            //sanity checks
            if (item.size > 12){
              item.size = 12;
            }
          }
        }

        function remove(item, index) {
          if (item.size) {
            while(item.size > 4) {
              shrink(item);
            }
          }
          InfographicLayoutFactory.remove(index);
        }
				
				function remove_after_drag(item) {
					console.log(item);
					InfographicLayoutFactory.get_layout().splice(item,1);
				}

        vm.add_row = InfographicLayoutFactory.inc_rows;
        vm.get_layout = InfographicLayoutFactory.get_layout;
        vm.set_active_cell = InfographicLayoutFactory.set_active_cell;
        vm.selected = {};
        vm.layout = vm.get_layout();
        vm.remove = remove;
				vm.remove_after_drag = remove_after_drag;
        vm.get_size_class = get_size_class;
        vm.shrink = shrink;
        vm.expand = expand;
        vm.add_row = add_row;
        vm.open_modal = AddVisualizationModalFactory.open_modal;
    }

    function backImg(){
        var directive = {
            link: link
        };
        return directive;

        function link(scope, element, attrs){
            attrs.$observe('backImg', function(value) {
                console.log("observing backImg", value);
                if (value) {
                    console.log("we got a change");
                    value = window.encodeURI(value);
                    console.log(value);
                    element.css({
                        'background-image': 'url(' + value +')',
                        'background-size' : 'contain'
                    });
                }
            });
        }
    }
})();
    
