(function(){
'use strict';
    angular.module('myApp')
        .config(function(SFormBuilderSettingsProvider) {
            SFormBuilderSettingsProvider.set_base_path('/static/ngtemplates/sform/builder');
        })
        .controller('LocationTypeController', LocationTypeController);


    LocationTypeController.$inject = ["$scope", "$log", "mappdata", "$timeout", "SFormBuilder", "SFormRenderer", "TrueFalse"];

    function LocationTypeController ($scope, $log, mappdata, $timeout, SFormBuilder, SFormRenderer, TrueFalse) {
        $scope.loc = {};
        $scope.tf = TrueFalse;
        $scope.filePlaceholder = "Add File";

        $scope.initFile = function (filename) {
            var split_fname;
            if (filename) {
                split_fname = filename.split("/");
                $scope.filePlaceholder = split_fname[split_fname.length - 1];
                $scope.uploaded = false;
            }
        };

        //TODO: these should be broken out into directives

        $scope.addfile = function (files) {
            if (files && files.length) {
                var file = files[0];
                $scope.filePlaceholder = file.name;
                $scope.uploaded = true;
                $scope.file = file;
            }
        };

        function redirect() {
            window.location.href = '/maps-admin/locations-types';
        }

        $scope.getSFormBuilderData = function () {
            $log.info("calling getSFormBuilderData()");
            return JSON.parse(angular.toJson(SFormBuilder.getData()));
        };

        $scope.submit = function () {
            $log.info("calling submit()");
            //summernote doesn't update all the time get the value with jQuery
            $scope.loc.desc = angular.element('.note-editable').text();
            $scope.loc.taxonomies = angular.toJson($scope.loc.taxonomies);

            //update allows...
            $scope.loc.allow_categories = $scope.loc.allow_categories;
            $scope.loc.allow_forms = $scope.loc.allow_forms;
            $scope.loc.allow_galleries = $scope.loc.allow_galleries;
            $scope.loc.allow_media = $scope.loc.allow_media;

            //custom fields
            var renderer_data = SFormRenderer.getData();
            var builder_data  = $scope.getSFormBuilderData();
            var field_groups = renderer_data.concat(builder_data);
            try{
                $scope.loc.custom_field_form.field_groups = field_groups;
            }catch(e){
                $scope.loc.custom_field_form = {"field_groups": field_groups};
            }
            mappdata.saveLocType($scope.loc, $scope.file, $scope.uploaded)
                .then(redirect)
                .catch(function(e){
                    if(e.data.indexOf('duplicate') > 1){
                        $scope.duplicate_name_error = "This name is taken";
                    }
                });
        };

        $scope.getTax = function () {
          return $scope.loc.taxonomies;
        };

        $scope.tax_changed = function (tx, checked){
            $log.info('Category changed, removing or adding forms');
            if(checked){
                if($scope.loc.custom_field_form){
                    // if the model has custom forms already
                    for(var fg in tx.custom_field_form.field_groups){
                        var tmp = tx.custom_field_form.field_groups[fg];
                        if(tmp.id !== "category"){
                            tmp.id = "category";
                        }
                        $scope.loc.custom_field_form.field_groups.push(tmp);
                    }
                    $log.info("Updated model custom_field_form.field_groups to ", $scope.loc.custom_field_form.field_groups);
                }else{
                    // otherwise just drop in the categories forms in a placeholder
                    $scope.loc.custom_field_form = {"field_groups": []};
                    for(var fg in tx.custom_field_form.field_groups){
                        var tmp = tx.custom_field_form.field_groups[fg];
                        if(tmp.id !== "category"){
                            tmp.id = "category";
                        }
                        $scope.loc.custom_field_form.field_groups.push(tmp);
                    }
                    $log.info("Updated model custom_field_form to ", $scope.loc.custom_field_form);
                }
            }else{
                $log.info('Removing custom_fields for category: ', tx);
                $scope.loc.custom_field_form.field_groups = $scope.loc.custom_field_form.field_groups.filter(function(i){
                    return _drop_fg(i);
                });    
            }
            
            if($scope.loc.custom_field_form){
                $log.info('Setting SForm data: ', $scope.loc.custom_field_form);
                var field_groups = $scope.loc.custom_field_form.field_groups;
                var lt_forms = field_groups.filter(function(item){
                    return item.id !== "category";
                });
                var cat_forms = field_groups.filter(function(item){
                    return item.id === "category";
                });
                SFormBuilder.setData(lt_forms);
                SFormRenderer.reset();
                SFormRenderer.setData(cat_forms);
            }

            function _drop_fg(fg){
                for(var g in tx.custom_field_form.field_groups){
                    if(fg.name === tx.custom_field_form.field_groups[g].name){
                        return false;
                    }
                }
                return true;
            }
        };
        function setup() {
            mappdata.getTaxonomies().then(function (data) {
                $log.info("Successful getTaxonomies", data.data);                
                $scope.taxonomy = data.data;

                if($scope.loc.custom_field_form){
                    $log.info('Setting SForm data: ', $scope.loc.custom_field_form);
                    var field_groups = $scope.loc.custom_field_form.field_groups;
                    var lt_forms = field_groups.filter(function(item){
                        return item.id !== "category";
                    });
                    var cat_forms = field_groups.filter(function(item){
                        return item.id === "category";
                    });
                    SFormBuilder.setData(lt_forms);
                    SFormRenderer.setData(cat_forms);
                }
            }).catch(function(e){
                $log.error("Error while getting Taxonomies", e);    
            });                       
        }
        // Load model based on id in the url
        var id = window.location.pathname.slice(0, -1).split("/").pop();        
        mappdata.getLocType(id).then(function(data){
            $log.info("Successful getLocType", data.data);
            $scope.loc = data.data;
            setup();
        }).catch(function(e){
            $log.error("Error while getting Location Type", e);
            setup();
        });
    }
})();
