angular.module('CategoryModule', [])
    .factory('Category', function () {
        return function () {
            this.id = '';
            this.name = '';
            this.privacy = 'Everyone';
            this.description = '';
            this.taxonomies = '';
            this.custom_field_form = '';
        };
    })
    .service('CategoryAPI', ['$http', function ($http) {
        var baseUrl = '/api/v1/categories/';
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
    .service('CategoryManager', ['Category', 'CategoryAPI', function (Category, CategoryAPI) {
        var _model = new Category();
        return {
            model: _model,
            load: function (id, callbackSuccess, callbackError) {
                CategoryAPI.load(id).then(
                    function success(response) {
                        for (var attr in _model) {
                            if (attr in response.data) {
                                if (attr == 'taxonomies' && response.data['taxonomies']) {
                                    _model['taxonomies'] = JSON.parse(response.data['taxonomies']);
                                } else {
                                    _model[attr] = response.data[attr];
                                }
                            }
                        }
                        callbackSuccess && callbackSuccess.call(undefined, response);
                    },
                    callbackError
                );
            },
            save: function (callbackSuccess, callbackError) {
                if (_model.inherit && _model.inherit === 'null') {
                    _model.inherit = null;
                }
                CategoryAPI.save(_model)
                    .then(callbackSuccess, callbackError);
            },
            remove: function (id, callbackSuccess, callbackError) {
                CategoryAPI.remove(id)
                    .then(callbackSuccess, callbackError);
            }
        };
    }]);
