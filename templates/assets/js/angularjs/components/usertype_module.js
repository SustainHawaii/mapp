angular.module('UserTypeModule', [])
    .value('Permission', {
        locations: {
            '0': 'Can Add Locations',
            '1': 'Can Edit Own Locations',
            '2': 'Can Delete Own Locations',
            '3': 'Can Edit Custom Location Types',
            '4': 'Can Edit Others Locations',
            '5': 'Can Delete Others Locations',
            '6': 'Can Add Custom Location Types',
            '7': 'Can Delete Custom Location Types'
        },
        categories: {
            '0': 'Can Add Categories',
            '1': 'Can Edit Own Categories',
            '2': 'Can Delete Own Categories',
            '3': 'Can Add Taxonomy',
            '4': 'Can Edit Others Taxonomy',
            '5': 'Can Delete Others Taxonomy',
            '6': 'Can Add Custom Categories',
            '7': 'Can Delete Custom Categories'
        },
        users: {
            '0': 'Can Add Users',
            '1': 'Can Edit Own Users',
            '2': 'Can Delete Own Users',
            '3': 'Can Edit Custom User Types',
            '4': 'Can Edit Others Users',
            '5': 'Can Delete Others Users',
            '6': 'Can Add Custom User Types',
            '7': 'Can Delete Custom User Types'
        },
        forms: {
            '0': 'Can Add Forms',
            '1': 'Can Edit Own Forms',
            '2': 'Can Delete Own Forms',
            '3': 'Can Edit Custom Form Types',
            '4': 'Can Edit Others Forms',
            '5': 'Can Delete Others Forms',
            '6': 'Can Add Custom Forms',
            '7': 'Can Delete Custom Forms'
        },
        'Resources': {
            '0': 'Can Add Resources',
            '1': 'Can Edit Own Resources',
            '2': 'Can Delete Own Resources',
            '3': 'Can Edit Others Resources',
            '4': 'Can Delete Others Resources',
            '5': 'Can Edit Resources Settings'
        },
        'Settings': {
            '0': 'Can Edit Global  Settings'
        }        
    })
    .factory('UserType', function () {
        return function () {
            this.id = '';
            this.name = '';
            this.is_superuser = false;
            this.permissions = {
                locations: {},
                category: {},
                users: {},
                forms: {}
            };
            this.allow_register = true;
            this.need_authorization = true;
            this.custom_field_form = '';
        };
    })
    .service('UserTypeAPI', ['$http', function ($http) {
        var baseUrl = '/api/v1/usertypes/';
        return {
            list: function() {
                return $http.get(baseUrl);
            },
            load: function (id) {
                return $http.get(baseUrl + id + '/');
            },
            save: function (data) {
                var config = {
                    method: 'POST',
                    url: baseUrl,
                    data: data
                };

                if (data.id) {
                    config.method = 'PUT';
                    config.url = baseUrl + data.id + '/';
                }

                return $http(config);
            },
            remove: function (id) {
                return $http.delete(baseUrl + id + '/');
            }
        };
    }])
    .service('UserTypeManager', ['UserType', 'UserTypeAPI', function (UserType, UserTypeAPI) {
        var _model = new UserType();
        return {
            model: _model,
            load: function (id, callbackSuccess, callbackError) {
                UserTypeAPI.load(id).then(
                    function success(response) {
                        for (var attr in _model) {
                            if (attr in response.data) {
                                _model[attr] = response.data[attr];
                            }
                        }
                        callbackSuccess && callbackSuccess.call(undefined, response);
                    },
                    callbackError
                );
            },
            save: function (callbackSuccess, callbackError) {
                UserTypeAPI.save(_model).then(
                    callbackSuccess,
                    callbackError
                );
            },
            remove: function (id, callbackSuccess, callbackError) {
                UserTypeAPI.remove(id).then(
                    callbackSuccess,
                    callbackError
                );
            }
        };
    }])
;
