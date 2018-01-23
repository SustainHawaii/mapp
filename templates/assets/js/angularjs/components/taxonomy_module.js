angular.module('TaxonomyModule', [])
    .factory('Taxonomy', function () {
        return function () {
            this.id = '';
            this.name = '';
            this.privacy = 'Everyone';
            this.description = '';
            this.inherit = null;
            this.model = '';
            this.compare = '';
            this.model_id = '';
            this.custom_field_form = '';
        };
    })
    .service('TaxonomyAPI', ['$http', function ($http) {
        var baseUrl = '/api/v1/taxonomy/';
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
    .service('TaxonomyManager', ['Taxonomy', 'TaxonomyAPI', function (Taxonomy, TaxonomyAPI) {
        var _model = new Taxonomy();
        return {
            model: _model,
            load: function (id, callbackSuccess, callbackError) {
                TaxonomyAPI.load(id).then(
                    function success(response) {
                        for (var attr in _model) {
                            if (attr in response.data) {
                                if (attr == 'inherit' && response.data['inherit'] && 'id' in response.data['inherit']) {
                                    _model['inherit'] = response.data['inherit']['id'];
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
                TaxonomyAPI.save(_model)
                    .then(callbackSuccess, callbackError);
            },
            remove: function (id, callbackSuccess, callbackError) {
                TaxonomyAPI.remove(id)
                    .then(callbackSuccess, callbackError);
            }
        };
    }]);
