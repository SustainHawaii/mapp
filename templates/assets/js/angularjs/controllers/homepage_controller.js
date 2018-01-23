/**
 * Created by Suleiman on 12-Mar-15.
 */

var app = angular.module(
    'HomePageApp', ['ui.select2', 'ui.bootstrap', 'sForm.Renderer', 'angularFileUpload',
                    'ngMaps', 'mapp_data', 'datavizApp', 'checklist-model', 'previewLocation',
                    'dndLists', 'ResourceModule', 'angular-click-outside']);

app.config(function ($interpolateProvider, SFormRendererSettingsProvider, $locationProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');

    SFormRendererSettingsProvider.set_base_path('/static/ngtemplates/sform/renderer');

    /*html5mode breaks the whole site... dn't do this*/
    //$locationProvider.html5Mode(true);
    
});

app.factory('home', function ($http) {
    var api_root = '/api/v1/';
    var call_api = function (endpoint, data, file) {
        if (data.id) {
            nurl = api_root + endpoint + "/" + data.id;
            return $http.put(url, data);
        } else {
            url = api_root + endpoint;
            return $http.post(url, data);
        }
    };

    return {
        Register: function (loc_data) {
            return call_api("users/", loc_data);
        },
        Login: function (loc_data) {
            return $http.post("/login", loc_data);
        },
        getOrgs: function () {
            return $http.get(api_root + 'org/');
        },
        getUserTypes: function () {
            return $http.get(api_root + 'usertypes/');
        }
    };
});


app.directive("passwordVerify", function () {
    return {
        require: "ngModel",
        scope: {
            passwordVerify: '='
        },
        link: function (scope, element, attrs, ctrl) {
            scope.$watch(function () {
                var combined;

                if (scope.passwordVerify || ctrl.$viewValue) {
                    combined = scope.passwordVerify + '_' + ctrl.$viewValue;
                }
                return combined;
            }, function (value) {
                if (value) {
                    ctrl.$parsers.unshift(function (viewValue) {
                        var origin = scope.passwordVerify;
                        if (origin !== viewValue) {
                            ctrl.$setValidity("passwordVerify", false);
                            return undefined;
                        } else {
                            ctrl.$setValidity("passwordVerify", true);
                            return viewValue;
                        }
                    });
                }
            });
        }
    };
});

app.filter('CapitalizeFilter', function() {
    return function (input, format) {
        if (!input) {
            return input;
        }
        format = format || 'all';
        if (format === 'first') {
            // Capitalize the first letter of a sentence
            return input.charAt(0).toUpperCase() + input.slice(1).toLowerCase();
        } else {
            var words = input.split(' ');
            var result = [];
            words.forEach(function(word) {
                if (word.length === 2 && format === 'team') {
                    // Uppercase team abbreviations like FC, CD, SD
                    result.push(word.toUpperCase());
                } else {
                    result.push(word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());
                }
            });
            return result.join(' ');
        }
    };
});
app.filter('filterByPropertiesName', function(){
    return function(arr, searchString){
        if(!searchString){
            return arr;
        }
        var result = [];
        searchString = searchString.toLowerCase();
        angular.forEach(arr, function(item){
            if(item.properties.name.toLowerCase().indexOf(searchString) !== -1){
                result.push(item);
            }
        });
        return result;
    };
});
app.filter('filterByAttr', function(){
    return function(arr, attr, searchString){
        if(!searchString){
            return arr;
        }
        console.log(attr);
        var result = [];
        searchString = searchString.toLowerCase();
        angular.forEach(arr, function(item){
            if(item[attr] && item[attr].toLowerCase().indexOf(searchString) !== -1){
                result.push(item);
            }
        });
        return result;
    };
});
app.controller('LoginController', function ($scope, $timeout, home) {
    $scope.log = {};
    $scope.isCollapsed = true;

    $scope.submit = function () {
        //hide message
        $scope.success_message = 'Logging in...';

        home.Login($scope.log)
            .then(function (result) {
                if (result.data.success === true & result.status==200) {
                    $scope.success_message = result.data.message;
                    $scope.isCollapsed = false;
                    $timeout(function () {
                        if (result.data.next == '/') {
                            window.location.href = '/maps-admin/dashboard';
                        } else {
                            window.location.href = result.data.next;
                        }
                    }, 250);
                }
                else {
                    $scope.success_message = result.data.message;
                    $scope.isCollapsed = false;
                }
            }, function(result){
                console.log("An error occurred during login: ", result);
                $scope.success_message = result.data.message;
                $scope.isCollapsed = false;                
            }
                 );
    };
});

app.controller('PasswordRecoverController', function ($scope, $timeout, home, $http) {
    
    $scope.rec = {};
    $scope.isCollapsed = true;

    $scope.submit = function () {
        $http.post("/password-recovery", $scope.rec)
            .success(function (data) {
                if (data.success) {
                    $scope.success_message = 'Password recovery request successful.';
                    $scope.isCollapsed = false;
                    $('#modal-recover').modal('hide');
                    $timeout(function () {
                        var success_msg = angular.element(document.querySelector('#tmpl-rec-success'));
                        var msgDiv = angular.element(document.querySelector('#messages'));
                        msgDiv.append(success_msg.text());
                    }, 250);
                } else {
                    $scope.success_message = data.message;
                    $scope.isCollapsed = false;
                }
            });
    };

    function close_other_modals(){
        console.log("Closing any other open modal");
        $('#modal-login').modal('hide');
        $('#modal-signup').modal('hide');    
    }
});

app.controller('RegisterController', function ($scope, $timeout, home, $http) {
    $scope.reg = {};
    $scope.isCollapsed = true;

    init_orgs = function () {
        home.getOrgs().then(function (data) {
            $scope.orgs = [];
            angular.forEach(data.data, function (org) {
                if (org) {
                    $scope.orgs.push({"id": org.id, "text": org.name});
                }
            });
        });
    };
    init_orgs();

    init_usertypes = function () {
        home.getUserTypes().then(function (data) {
            $scope.userTypes = [];
            angular.forEach(data.data, function (usertype) {
                if (usertype) {
                    $scope.userTypes.push({"id": usertype.id, "text": usertype.name});
                    if(usertype.name === "Member"){
                        $scope.reg.user_types = [usertype.id];
                    }
                }
            });
        });
    };
    init_usertypes();


    $scope.submit = function () {
        $scope.isCollapsed = false;
        $scope.success_message = "Registering... Please wait";
        $http.post('/signup', $scope.reg)
            .success(function() {
                $scope.success_message = "Registration Successful! Please check your email to confirm.";
                $scope.isCollapsed = false;
                $timeout(function () {
                    $('#modal-signup').modal('hide');
                    var success_msg = angular.element(document.querySelector('#tmpl-reg-success'));
                    var msgDiv = angular.element(document.querySelector('#messages'));
                    msgDiv.append(success_msg.text());
                    $scope.isCollapsed = true;
                }, 1000);
            })
            .error(function(data, status) {
                var tmp = "Registration unsuccessful. ";
                for (i in data) {
                    tmp += i + ": " + data[i];
                }
                $scope.success_message = tmp;
                $scope.isCollapsed = false;
            });
    };
});


app.directive('shDatepicker', function() {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function (scope, element, attrs, ngModelCtrl) {
            $(function(){
                element.datepicker({
                    dateFormat: attrs.shDatepicker ? attrs.shDatepicker : 'dd/mm/yy',
                    onSelect:function (date) {
                        ngModelCtrl.$setViewValue(date);
                        scope.$apply();
                    }
                });
            });
        }
    };
});

app.config(['$httpProvider', function($httpProvider){
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }]);

app.controller('CustomFieldController', function ($scope, $http, $timeout, SFormRenderer, mappdata, $log) {
    $scope.location_id = null;
    $scope.formInfo = null;
    $scope.formMessage = '';
    $scope.formIds = [];
    var defaultData = [];

    $scope.setObjectId = function(id) {
        var input = id.split('/');
        $scope.obj_id = input[1];

        if (input[0] == 'user') {
            $scope.url = '/api/v1/users/' + $scope.obj_id + '/form/';
        } else if (input[0] == 'location') {
            $scope.url = '/api/v1/location/' + $scope.obj_id + '/form/';
        }
    };

    $scope.setSFormRendererData = function (data) {
        // defaultData.push(data);
        // if (data === '') {
        //     $scope.formInfo = [];
        // } else {
        //     $scope.formIds.push($scope.formInfo.id);
        // }

        // var fg = $scope.formInfo.field_groups;
        // var front_end_fg = [];
        // for (i in fg) {
        //     if (fg[i]['form_type'] == 'front-end') {
        //         front_end_fg.push(fg[i]);
        //     }
        // }
        SFormRenderer.setData(data);
    };

    $scope.resetSFormRendererData = function () {
        SFormRenderer.reset();

        for (fg in defaultData) {
            dict = JSON.parse(defaultData[fg]);
            fg = dict['field_groups'];
            var front_end_fg = [];
            for (i in fg) {
                if (fg[i]['form_type'] == 'front-end') {
                    front_end_fg.push(fg[i]);
                }
            }
            SFormRenderer.setData(front_end_fg, true);
        }
    };

    $scope.getSFormRendererData = function () {
        var form = {
            ids: $scope.formIds,
            fieldGroups: SFormRenderer.getData()
        };
        return form;
    };

    $scope.reset = function() {
        $scope.resetSFormRendererData(defaultData);
    };

    $scope.submit = function () {
        if ($scope.formCustomField.$invalid) {
            return;
        }
        $http({
            method: 'POST',
            url: $scope.url,
            data: $scope.getSFormRendererData()
        }).success(function () {
            $scope.formMessage = 'Form submitted successfully.';
            $scope.reset();
            $scope.formCustomField.$setPristine();
            $timeout(function() {
                $scope.formMessage = '';
            }, 5000);
        }).error(function () {
            console.log('error');
        });
    };
    function setup(){
        console.log("in setup");
        if ($scope.loc.location_type.custom_field_form) {
          console.log("papa got some forms");
          var frontend_forms = $scope.loc.location_type.custom_field_form.field_groups.filter(function(item){
              return item.form_type === "front-end";
          });
          $scope.setSFormRendererData(frontend_forms);
        }
    }
    
    var id = window.location.pathname.slice(0, -1).split("/").pop();        
    mappdata.getLocation(id).then(function(data){
        $log.info("Successful getLocation", data.data);
        $scope.loc = data.data;
        setup();
    }).catch(function(e){
        $log.error("Error while getting Location Type", e);
    });
});

app.value('TrueFalse', [
    true,
    false
]);

app.filter('trueFalseToYesNo', function () {
    return function (value) {
        return value ? 'Yes' : 'No';
    };
});

app.filter('trueFalseToPrivacyOptions', function () {
    return function (value) {
        return value ? 'Everyone' : 'Private';
    };
});

app.controller("MemberController", function($scope, $log, $window, $location, mappdata){
    $scope.user = {};
    $scope.owner = {};
    $scope.active = {};
    $scope.loc = {};
    
    $scope.setActiveAndRedirect = function(type, item){
        $log.info("Setting activeItem to: " + type);
        $window.location.href = "/?type="+type+"&item="+item;
    };

    $scope.claim_location = function (id) {
        $log.info("Changed 'also_editable_by' to, ", id);
        $scope.loc.also_editable_by = id;
        $scope.loc.location_type = $scope.loc.location_type.id;
        mappdata.saveLocation($scope.loc).then(function(){
            $log.info('location save success'); 
        });
    };    

    $scope.getUser = function (id) {
        mappdata.getUser(id).then(function(data){
            $scope.user = data.data;
        });
    };
    $scope.getOwner = function (id) {
        if($scope.user.id !== id){
            mappdata.getUser(id).then(function(data){
                $scope.owner = data.data;
            });            
        }
    };

    $scope.getLocation = function (id) {
        mappdata.getLocation(id).then(function(data){
            $scope.loc = data.data;
        });            
    };        

});

app.controller("IndexController", function($scope, $log, $window, $location, $timeout,  mappdata, mapping){
    $scope.selectedTags = [];
    $scope.selectedCategory = [];
    $scope.tags = [];
    $scope.categories = [];
    $scope.selectedTags = [];
    $scope.tags_for_jquery = [];
    
    $scope.tagOptions = {
        multiple: true,
        simple_tags: true,
        tags: function(){
            return $scope.tags;
        }
    };
    $scope.catOptions = {
        'multiple': true
    };

    $scope.initMapping = function(locid) {
      /* give me a locatino id, i'll build the properties you
       * need to display that dude on the map
       * currently this is used for members-location page
       */
        $scope.map = mapping.options_for_location(locid);
    };


    $scope.angular_submit_form = function(item,add) {
      console.log(item);
      if(add) {
        $scope.tags_for_jquery.push(item.id);
      } else {
        var idx = $scope.tags_for_jquery.indexOf(item.id);
        $scope.tags_for_jquery.splice(idx,1);
      }
        $scope.$apply();
      $('#search-form').submit();
    };

    $scope.refresh_tags = function(tag) {
      if (tag) {
        mappdata.searchTags(tag).then(function (data) {
          $scope.tags = data.data;
        });
      }
    };

    function setSearchItem() {
        var active = $location.search();
        if(active.item){
            if(active.type === 'category'){
                $scope.selectedCategory.push(active.item);
            }else{
                $scope.selectedTags.push(active.item);
            }
            $log.info("Setting active to: ", active);
        }
    }
    
    function getTaxonomies() {
        mappdata.getTaxonomies().then(
            function(data){
                $scope.categories = data.data;
               // $scope
                setSearchItem();                 
            });
    }

    function getTags () {
        mappdata.getAllTags().then(
            function(data){
                $scope.tags = [];
                angular.forEach(data.data, function (ltype) {
                    if (ltype) {
                        $scope.tags.push(ltype.name);
                    }
                });
            });
    }
    getTaxonomies();
    getTags();
});
