angular.module('UserProfileModule', [])
    .factory('UserProfile', function () {
        return function () {
            this.id = '';
            this.full_name = '';
            this.email = '';
            this.password = '';
            this.confirm_password = '';
            this.image = '';
            this.user_types = [];
            this.custom_field_form = '';
            this.address = '';
            this.zip = '';
            this.city = '';
            this.state = '';
            this.description = '';
        };
    })
    .service('UserProfileAPI', ['$http', '$upload', function ($http, $upload) {
        var baseUrl = '/api/v1/users/profile/';
        return {
            load: function (id) {
                return $http.get(baseUrl + id + '/');
            },
            save: function (data, files) {
                var config = {
                    method: 'PUT',
                    url: baseUrl + data.id + '/',
                    fields: angular.copy(data),
                    file: files
                };

                for (var ut in config.fields.user_types) {
                    config.fields.user_types[ut] = config.fields.user_types[ut]['id'];
                }
                return $upload.upload(config);
            },
            remove: function (id) {
                return $http.delete(baseUrl + id + '/');
            }
        };
    }])
    .service('UserProfileManager', ['UserProfile', 'UserProfileAPI', function (UserProfile, UserProfileAPI) {
        var _model = new UserProfile();
        return {
            model: _model,
            load: function (id, callbackSuccess, callbackError) {
                UserProfileAPI.load(id).then(
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
            save: function (callbackSuccess, callbackError, files) {
                UserProfileAPI.save(_model, files).then(
                    callbackSuccess,
                    callbackError
                );
            },
            remove: function (id, callbackSuccess, callbackError) {
                UserProfileAPI.remove(id).then(
                    callbackSuccess,
                    callbackError
                );
            }
        };
    }])
;
