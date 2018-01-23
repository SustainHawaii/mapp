angular.module('OrganizationModule', [])
    .factory('Organization', function () {
        return function () {
            this.id = '';
            this.name = '';
            this.address = '';
            this.city = '';
            this.state = '';
            this.zip = '';
            this.phone = '';
            this.website = '';
            this.description = '';
            this.privacy = 'Everyone';
        };
    })
    .service('OrganizationAPI', ['$http', function ($http) {
        var baseUrl = '/api/v1/org/';
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
    .service('OrganizationManager', ['Organization', 'OrganizationAPI', function (Organization, OrganizationAPI) {
        var _model = new Organization();
        return {
            model: _model,
            load: function (id, callbackSuccess, callbackError) {
                OrganizationAPI.load(id).then(
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
                OrganizationAPI.save(_model).then(
                    callbackSuccess,
                    callbackError
                );
            },
            remove: function (id, callbackSuccess, callbackError) {
                OrganizationAPI.remove(id).then(
                    callbackSuccess,
                    callbackError
                );
            }
        };
    }])
;
