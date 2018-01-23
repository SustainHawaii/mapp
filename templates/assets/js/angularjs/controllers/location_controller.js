(function () {
    angular.module('myApp')
        .controller('LocationController', LocationController);

    LocationController.$inject = ["$scope", "$filter", "$timeout", "mappdata", "SFormRenderer", "$log"];
    function LocationController ($scope, $filter, $timeout, mappdata, SFormRenderer, $log) {
        $scope.filePlaceholder = "Add File to display on location page";
        $scope.loc = {tags:[]}; //need to define tags for select2
        $scope.ltypes = [];
        $scope.tags = [];

        $scope.claim_location = function () {
            $log.info("Changed 'owned_by' to, ", $scope.current_user);
            $scope.loc.also_editable_by = $scope.current_user;  
        };

        $scope.update_locationtype_form = function () {
            $log.info("calling update_locationtypee_form with: ",
                      $scope.loc.location_type);
            var tmp = [];
            if($scope.loc.custom_field_form){
                tmp = $scope.loc.custom_field_form;
                if(tmp.field_groups){
                    tmp = tmp.field_groups.filter(function(item){
                        return item.id !== "locationtype";
                    });
                    $scope.loc.custom_field_form.field_groups = tmp;   
                }
            }
            var field_groups = get_field_groups("locationtype");
            field_groups = field_groups.map(function(item){
                item["id"] = "locationtype";
                return item;
            });
            update_custom_field_form(field_groups);
        };

        function update_custom_field_form(field_groups){
            if($scope.loc.custom_field_form){
                var tmp = $scope.loc.custom_field_form.field_groups;
                tmp = tmp.concat(field_groups);
                $scope.loc.custom_field_form.field_groups = tmp;
            }else{
                $scope.loc.custom_field_form = {"field_groups": field_groups};
            }
            if($scope.loc.custom_field_form){
                $log.info('Setting SForm data: ', $scope.loc.custom_field_form);
                SFormRenderer.reset();
                SFormRenderer.setData($scope.loc.custom_field_form.field_groups);                
            }        
        }

        function get_field_groups (type) {
            if(type === "locationtype"){
                var lt = $scope.locationtypes.filter(function(item){
                    return item.id == $scope.loc.location_type;
                });
                try{
                    return lt[0].custom_field_form.field_groups;
                }catch(e){
                    return [];
                }
            }
            return [];
        }

        $scope.seturl = function (url) {
            $scope.loc.org_website = url;
        };

        function setLtypes (data) {
            $scope.ltypes = [];
            $scope.locationtypes = data.data.results;
            angular.forEach(data.data.results, function (ltype) {
                if (ltype) {
                    $scope.ltypes.push({"value": ltype.id, "name": ltype.name});
                }
            });
        };

        $scope.setnumber = function (scopename, val) {
            if (val) {
                $scope.loc[scopename] = parseInt(val);
            }
        };
        $scope.initFile = function (filename) {
            if (filename) {
                split_fname = filename.split("/");
                $scope.filePlaceholder = split_fname[split_fname.length - 1];
                $scope.uploaded = false;
            }
        };

        $scope.addfile = function (files) {
            if (files && files.length) {
                var file = files[0];
                $scope.filePlaceholder = file.name;
                $scope.uploaded = true;
                $scope.file = file;
            }
        };

        $scope.orgOptions = {
            multiple: true,
            maximumSelectionSize: 1,
            tags: function () {
                return [{text: 'Organizations', children: $scope.orgs},{text: 'Users', children: $scope.users}];
            },
            formatSelection: function (item) {
                return item.text;
            }
        };

        var update_org = function (org_id) {
            console.log("update org called with", org_id);
            mappdata.getOrg(org_id).then(function (data) {
                $scope.loc.org_address = data.data.address;
                $scope.loc.org_phone = data.data.phone;
                $scope.loc.org_zip = data.data.zip;
                $scope.loc.org_city = data.data.city;
                $scope.loc.org_state = data.data.state;
                $scope.loc.org_website = data.data.website;
                        
            });
                
        };

        var clear_org = function () {
            $scope.loc.org_address = '';
            $scope.loc.org_zip = '';
            $scope.loc.org_phone = '';
            $scope.loc.org_city = '';
            $scope.loc.org_state = '';
            $scope.loc.org_website = '';                
        };

        $scope.$watch('loc.org', function () {
            var org = $scope.loc.org;
            if (org && org.length > 0) {
                console.log("got org");
                try {
                    update_org(org[0].id);                                
                } catch (e) {}
            } else {
                clear_org();                        
            }                
        });

        function redirect() {
            window.location.href = '/maps-admin/locations';
        }

        $scope.setSFormRendererData = function (data) {
            if (data === '') {
                data = [];                        
            }
            SFormRenderer.setData(data);                
        };

        $scope.getSFormRendererData = function () {
            return angular.toJson(SFormRenderer.getData());                
        };
        
        function setup(data) {
            mappdata.getAllOrgs().then(function setOrg(data) {
                $scope.orgs = [];
                angular.forEach(data.data, function (org) {
                    if (org) {
                        $scope.orgs.push({"id": org.id, "text": org.name});
                    }
                });
            });

            mappdata.getAllUsers().then(function setUser(data) {
                $scope.users = [];
                angular.forEach(data.data, function (user) {
                    if (user) {
                        if (user.organization) {
                            $scope.users.push({"id": user.organization.id, "text": user.name});
                        }
                    }
                });
            });

            ///load full tag info, so we have it for custom forms and what not 
            if ($scope.loc.tags){
              angular.forEach($scope.loc.tags, function(tag) {
                if (tag.hasOwnProperty('name')){
                  mappdata.searchTags(tag.name).then(function(data) {
                    $scope.tags.push(data.data[0]);
                  });
                }
              });
            }

            mappdata.getLocationTypes().then(function(data){
                setLtypes(data);
                if($scope.loc.location_type){
                    $scope.loc.location_type = $scope.loc.location_type.id;                    
                }
                if($scope.loc.custom_field_form){
                    $log.info('Setting SForm data: ', $scope.loc.custom_field_form);
                    SFormRenderer.reset();
                    SFormRenderer.setData($scope.loc.custom_field_form.field_groups.filter(function(item){
                        return item.form_type === "back-end";
                    }));
                }                        
            });
        }
        
        $scope.refresh_tags = function(tag) {
          console.log(tag);
          if (tag) {
            mappdata.searchTags(tag).then(function (data) {
              $scope.tags = data.data;
            });
          }
        }

        var id = window.location.pathname.slice(0, -1).split("/").pop();        
        mappdata.getLocation(id).then(function(data){
            $log.info("Successful getLocation", data.data);
            $scope.loc = data.data;
            $scope.loc.tags = data.data.tags;
            $scope.loc.org = angular.fromJson(data.data.org);
            setup();
        }).catch(function(e){
            $log.error("Error while getting Location", e);
            setup();
        });

        $scope.tag_changed = function (tag, checked){
            $log.info(tag);
            $log.info('Category changed, removing or adding forms');
            if(checked){
                add_tag_forms(tag);
            }else{
                $log.info('Removing custom_fields for category: ', tag);
                if ($scope.loc.custom_field_form) {
                  $scope.loc.custom_field_form.field_groups = $scope.loc.custom_field_form.field_groups.filter(function(i){
                    return _drop_fg(i);
                  });    
                }
            }
            
            if($scope.loc.custom_field_form){
                $log.info('Setting SForm data: ', $scope.loc.custom_field_form);
                SFormRenderer.reset();
                SFormRenderer.setData($scope.loc.custom_field_form.field_groups.filter(function(item){
                    return item.form_type === "back-end";
                }));

            }

            function _drop_fg(fg){
                for(var g in tag.custom_field_form.field_groups){
                    if(fg.name === tag.custom_field_form.field_groups[g].name){
                        return false;
                    }
                }
                return true;
            }

            function add_tag_forms(tag){
                if($scope.loc.custom_field_form){
                    // if the model has custom forms already
                    if (tag.custom_field_form) {
                      for(var fg in tag.custom_field_form.field_groups){                        
                          var tmp = tag.custom_field_form.field_groups[fg];
                          tmp.id = "tag";
                          $scope.loc.custom_field_form.field_groups.push(tmp);
                      }
                      $log.info("Updated model custom_field_form.field_groups to ", $scope.loc.custom_field_form.field_groups);
                    }
                }else{
                    // otherwise just drop in the categories forms in a placeholder
                    if (tag.custom_field_form) {
                      if (!$scope.loc.custom_field_form) {
                        $scope.loc.custom_field_from = {"field_groups": []};
                      } else {
                        $scope.loc.custom_field_form.field_groups = [];
                      }
                      for(var fg in tag.custom_field_form.field_groups){
                          var tmp = tag.custom_field_form.field_groups[fg];
                          tmp.id = "tag";
                          $scope.loc.custom_field_form.field_groups.push(tmp);
                      }
                      $log.info("Updated model custom_field_form to ", $scope.loc.custom_field_form);
                    }
                }
            }
        };

        $scope.submit = function () {
            $log.info("Updating model");
            $log.info($scope.loc.tags);
            $scope.submitting = true;
            if ($scope.location_form.$invalid) {
                $log.error("Location form is invalid");
                $scope.submitting = false;
                return;
            }

            // summernote doesn't update all the time get the value with jQuery
            $scope.loc.description = angular.element('.note-editable').html();
            if(!$scope.loc.image){
                $scope.loc.image = "";
            }

            // custom form
            var renderer_data = JSON.parse($scope.getSFormRendererData());
            if (renderer_data.length > 0) {
                var field_groups = $scope.loc.custom_field_form.field_groups;                
                for (var i in renderer_data) {                
                    field_groups = field_groups.filter(function(item){
                        if(item.name === renderer_data[i].name){
                            return false;
                        }
                        return true;
                    });
                    field_groups.push(renderer_data[i]);
                }
                $scope.loc.custom_field_form.field_groups = field_groups;
            }

            $scope.loc.custom_field_form = JSON.stringify($scope.loc.custom_field_form);

            mappdata.saveLocation($scope.loc, $scope.file).then(function (retVal) {
                redirect();
            }).catch(function(e){
                $scope.duplicate_name_error = e.data.error;
            });
        };        
    }

})();






