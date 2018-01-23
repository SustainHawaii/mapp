angular.module('UserModule', [])
    .factory('User', function () {
        return function () {
            this.id = '';
            this.full_name = '';
            this.email = '';
            this.password = '';
            this.confirm_password = '';
            this.image = '';
            this.user_types = [];
            this.organization = null;
            this.custom_field_form = null;
            this.address = '';
            this.zip = '';
            this.city = '';
            this.state = '';
            this.description = '';
        };
    })
    .service('UserAPI', ['$http', function ($http) {
        var baseUrl = '/api/v1/users/';
        return {
            load: function (id) {
                return $http.get(baseUrl + id + '/');
            },
            save: function (data) {
                var config = {
                    method: 'POST',
                    url: baseUrl,
                    data: angular.copy(data)
                };

                if (data.organization && 'id' in data.organization) {
                    config.data.organization = data.organization.id;
                }

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
    .service('UserManager', ['User', 'UserAPI', function (User, UserAPI) {
        var _model = new User();
        return {
            model: _model,
            load: function (id, callbackSuccess, callbackError) {
                UserAPI.load(id).then(
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
                UserAPI.save(_model).then(
                    callbackSuccess,
                    callbackError
                );
            },
            remove: function (id, callbackSuccess, callbackError) {
                UserAPI.remove(id).then(
                    callbackSuccess,
                    callbackError
                );
            }
        };
    }])
;
