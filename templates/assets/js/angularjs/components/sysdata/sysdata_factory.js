(function () {
angular.module("mapp_data", ['angularFileUpload'])
      .factory('mappdata', mappdata);

    mappdata.$inject = ['$http', '$q', '$upload', "$log"];
    function mappdata ($http, $q, $upload, $log) {
        var api_root = '/api/v1/';
        var tags_api_root = '/maps-admin/categories/api/v1/categories';

        function get(baseurl, id, list_type, limit, order_by,filter) {
            $log.info('Getting (ajax) via mappdata');

            if (id) {baseurl += id;}
            return $http({
                url: baseurl,
                method: "GET",
                params: {list_type: list_type,
                         limit: limit,
                         order_by: order_by,
                         filter: filter}
            });
        };

        function save(endpoint, data, file) {
            $log.info('Saving (put/post) via mappdata');
            var method, url;
            if (data.id) {
                method = "PUT";
                url = api_root + endpoint + data.id + '/';
            } else {
                method = "POST";
                url = api_root + endpoint;
            }
            return $upload.upload({
                url: url,
                fields: data,
                file: file,
                method: method
            });
        };

        function patch (endpoint, data) {
            url = api_root + endpoint + data.id + '/';
            return $http.patch(url, data);
        };

        function call_tag_api (endpoint, data, file) {
            var method, url;
            if (data.id) {
                method = "PUT";
                url = endpoint + data.id + '/';
            } else {
                method = "POST";
                url = endpoint;
            }
            return $upload.upload({url: url, fields: data, file: file, method: method
                                  });
        }
        
        function isNumeric (obj) {
            return !isNaN(parseFloat(obj)) && isFinite(obj);
        }
        
        var service = {
            getTaxonomies: getTaxonomies,
            getCategories: getCategories,
            getUserTypes: getUserTypes,
            getAllUsers: getAllUsers,
            getUser: getUser,
            saveUser: saveUser,
            patchUser: patchUser,
            getLocations: getLocations,
            getLocation: getLocation,
            getLocationTypes: getLocationTypes,
            saveLocation: saveLocation,
            getSelectedTaxonomy: getSelectedTaxonomy,
            getexternal: getexternal,
            getViz: getViz,
            getAllViz: getAllViz,
            getAllResources: getAllResources,
            saveResource: saveResource,
            updateResource: updateResource,
            getResource: getResource,
            deleteResource: deleteResource,
            updateResourceSettings: updateResourceSettings,
            getResourceSettings: getResourceSettings,
            getBulkData: getBulkData,
            getData: getData,
            getsysdata: getsysdata,
            getToplevels: getToplevels,
            getExternalToplevels: getExternalToplevels,  
            searchLocations: searchLocations,
            getLocType: getLocType,
            saveLocType: saveLocType,
            getAllTags: getAllTags,
            getTag:getTag,
            searchTags: searchTags,
            saveTags: saveTags,
            getTagsForObjectId: getTagsForObjectId,
            getCategory: getCategory,
            getOrg: getOrg,
            getAllOrgs: getAllOrgs,
            deleteDataViz: deleteDataViz
        };

        return service;

        //the factory to return

        function getTaxonomies (list_type, filter) {
            return get(api_root + 'taxonomy/',null, list_type,null,null,filter);
        };
        function getCategories (list_type, filter) {
            return get(api_root + 'categories/',null, list_type,null,null,filter);
        };
        function getUserTypes (list_type, filter) {
            return get(api_root + 'usertypes/',null, list_type,null,null,filter);
        };
        function getAllUsers () {
            return get(api_root + 'users/');        
        }
        function getUser (id) {
            return get(api_root + 'users/' + id + '/',null, null);
        };
        function saveUser (resource_data, file) {
            $log.info("saving user", resource_data, file);
            return save("users/", resource_data, file);
        };
        function patchUser (user) {
            console.log("patching user", user);
            return patch("users/", user);
        };
        function getLocations (list_type) {
            return get(api_root + 'location/',null, list_type);
        };
        function getLocation(id) {
            return $http.get(api_root + 'location/' + id);
        }
        function saveLocation(data, file){
            $log.info("saveLocation with: ", data, file );
            return save("location/", data, file);
        }
        function getLocationTypes (list_type,filter) {
            return get(api_root + 'locationtype/', null, list_type,null,null,filter);
        };
        function getSelectedTaxonomy (id) {
            return $http.get(api_root + 'categories/' + id);
        };
        function getexternal (list_type) {
            if (!list_type) { list_type = "simple";}
            return get(api_root + "dataimport/",null, list_type);
        };
        function getViz (id) {
            return get(api_root + 'dataviz/' + id + "/");
        };        
        function getAllViz (list_type) {
            return get(api_root + 'dataviz/',null,list_type);
        };
        function getAllResources () {
            return get(api_root + 'resources/');
        };
        function saveResource (resource_data, file) {
            console.log(resource_data, file);
            return save("resources/", resource_data, file);
        };
        function updateResource (resource_data, file){
            console.log(resource_data, file);
            return save("resources/", resource_data, file);  
        };
        function getResource (id) {
            return $http.get(api_root + 'resources/' + id + '/');
        };
        function deleteResource (id) {
            return $http.delete(api_root + 'resources/' + id + '/');
        };
        function updateResourceSettings (resource_data){
            console.log(resource_data);
            return $http.put(api_root + 'resources_settings/' + resource_data.id + '/', resource_data);
        };
        function getResourceSettings (id) {
            return $http.get(api_root + 'resources_settings/' + id + '/');
        };
        function saveLocType (loc_data, file) {
            return save("locationtype/", loc_data, file);
        };
        function getLocType (id) {
            console.log('mappdata: getLocType with id: ' + id);
            return $http.get(api_root + 'locationtype/' + id + "/");
        };
        function getTaxonomies () {
            return $http.get(api_root + 'taxonomy/');
        };
        function saveTags (loc_data, file) {
            return call_tag_api(tags_api_root, loc_data, file);
        }
        function getTag(tag_id) {
          return $http.get(api_root + 'categories/' + tag_id);
        }
        function getAllTags () {
            return $http.get(api_root + 'categories/');
        }
        function searchTags (filter) {
            var url = api_root + "categories/";
            if (filter){ url += "?filter=" + filter;}
            return $http.get(url);
        }
        function getTagsForObjectId (id, cls) {
          var url = api_root + "categories/?forid=" + id +"&cls=" + cls;
          return $http.get(url);
        }
        function getCategory (id) {
            return $http.get(api_root + "taxonomy/" + id + "/");
        }
        function getOrg (id) {
            return $http.get(api_root + "org/" + id + "/");        
        }
        function getAllOrgs () {
            return $http.get(api_root + "org/");
        }
        function deleteDataViz (id){
            return $http.delete(api_root + "dataviz/" + id + "/");
        }

        //get data in bulk useful for loading table
        //TODO: this should support system types as well as external data
        function getBulkData (ids, page, page_size, search, search_fields, order_by) {
            //if life gives you lists... make a string
            if (ids.constructor === Array) {ids = ids.join(",");}
            if (search_fields.constructor === Array) { search_fields = search_fields.join(",");}
            return $http({
                url: api_root + "dataimport/get-data/",
                method: "GET",
                params: {import_ids : ids,
                         page : page,
                         page_size :page_size,
                         search : search,
                         search_fields : search_fields,
                         order_by : order_by}
            });
        };

        //generic way to get data, regardless if it's external data or system data
        function getData (id,type,limit, order_by, format) {
            //item is object with at least id and group
            //group being the type of item, i.e. imported from File,
            //Location Type, etc...
            switch(type) {
            case "Location Types": 
                url = "locationtype/form-data/"; 
                break;
            case "Taxonomy":
                url = "taxonomy/form-data/";
                break;
            case "User Types":
                url = "usertypes/form-data/";
                break;
            case "Categories":
                url = "categories/form-data/";
                break;
                //case "Imported from File":
            case "External_Categories":
                url = "categories/external-data/";                
                break;
            default:
                url = "dataimport/get-data/";
            }

            console.log("in get data with url", url);

            return $http({
                url: api_root + url + id,
                method: "GET",
                params: {limit : limit,
                         order_by : order_by,
                         format : format}
            }).then(function(data) {
                //conver to proper type
                console.log("in then functin of $http");
                for (var i = 0, arrLen = data.data.length; i < arrLen; i++) {
                    var val = data.data[i];
                    angular.forEach(val, function(field, field_name) {
                        if (isNumeric(field)) {
                            val[field_name] = parseFloat(field);
                        }
                    });
                };
                return data.data;    
            });
        };

        //get all system data in one shot
        function getsysdata () {
            return $q.all([
                getUserTypes("simple"),
                getCategories("simple"),
                getLocations("simple"),
            ]).then(function(res) {
                var retval = [];
                console.log(res);
                retval.push.apply(retval, res[0].data);
                retval.push.apply(retval, res[1].data);
                retval.push.apply(retval, res[2].data.results);
                return retval;
            });
        };

        function getToplevels (search_term) { 
            return $q.all([
                getUserTypes("simple", search_term),
                getCategories("simple", search_term),
                getLocationTypes("simple", search_term),
                getTaxonomies("simple", search_term),
            ]).then(function(res) {
                var retval = [];
                console.log(res);
                retval.push.apply(retval, res[0].data);
                retval.push.apply(retval, res[1].data);
                retval.push.apply(retval, res[2].data.results);
                retval.push.apply(retval, res[3].data);
                return retval;
            });
        };

        function getExternalToplevels () { 
            return $q.all([
                getCategories("simple"),
                getexternal(),
            ]).then(function(res) {
                var retval = [];
                console.log("retval from getExternalToplevels");
                console.log(res);
                console.log(res[0].data);
                //mark categories as external categories so later we can query DataImports
                //see the getData function in this module
                cats = res[0].data;
                for (var i = 0; i < cats.length; i++) {
                  cats[i].group ="External_Categories";
                }
                retval.push.apply(retval, cats);
                retval.push.apply(retval, res[1].data);
                return retval;
            });
        };

        //search locations, used with a map
        //not yet tested..
        function searchLocations (loc_types, tags, categories, plain_text, data_format) {
            if (! data_format) { data_format = "geojson"; }
            return $http({
                url: api_root + "location/search/",
                method: "GET",
                params: {"loc_types[]" : loc_types,
                         "tags[]" : tags,
                         "categories[]" :categories,
                         q : plain_text,
                         data_format : data_format
                        }
            });
        }
    };
})();
