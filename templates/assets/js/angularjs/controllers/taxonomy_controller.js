angular.module('myApp')
    .config(function(SFormBuilderSettingsProvider) {
        SFormBuilderSettingsProvider.set_base_path('/static/ngtemplates/sform/builder');
    })
    .controller('TaxonomyFormController', function ($scope, TaxonomyManager, TaxonomyAPI, $log,
                                                    Taxonomy, mappdata, $timeout, PrivacyOptions, SFormBuilder) {
        $scope.taxonomy = TaxonomyManager.model;
        $scope.alert = false;
        $scope.parent_tax = [];
        $scope.description_error = false;

        $scope.privacyOptions = PrivacyOptions;

        $scope.loadData = function (id) {
            if (id == '') {
                return;
            }
            TaxonomyManager.load(id, function callbackSuccess() {
                if ($scope.taxonomy.custom_field_form) {
                    $scope.setSFormBuilderData($scope.taxonomy.custom_field_form.field_groups);
                }
            });
        };

        $scope.setSFormBuilderData = function (data) {
            if (data === '') {
                data = [];
            }
            SFormBuilder.setData(data);
        };

        $scope.getSFormBuilderData = function () {
            return angular.toJson(SFormBuilder.getData());
        };



//        $scope.compares = ['Is Equal To', 'Is Not Equal To'];
//        $scope.model_group = ['User Types', 'Locations', 'Categories'];

//        mappdata.getsysdata().then(function (data) {
//            $scope.models = data;
//        });


        TaxonomyAPI.list().then(
            function success(response) {
                var _model;
                for (var item in response.data) {
                    _model = new Taxonomy();
                    for (var attr in _model) {
                        if (attr in response.data[item]) {
                            _model[attr] = response.data[item][attr];
                        }
                    }
                    $scope.parent_tax.push(_model);
                }
            }
        );

        $scope.submit = function () {
            var _has_error = false;
            $scope.taxonomy_form.not_unique = false;
            if ($scope.taxonomy_form.$invalid) {
                _has_error = true;
            }

            //fixed for summernote
            $scope.taxonomy.description = angular.element('.note-editable').text();

            if ($scope.description_error = ($scope.taxonomy.description.length == 0)) {
                _has_error = true;
            }

            if (_has_error) {
                return;
            }
            $scope.taxonomy.custom_field_form = $scope.getSFormBuilderData();

            TaxonomyManager.save(function (response) {
                if(response.data.error !== null && response.data.error === "NotUniqueError"){
                    $log.error('Caught NotUniqueError, Tag Name not unique: ', $scope.taxonomy.name)
                    $scope.formErrorMessage = "NotUniqueError";
                    $scope.taxonomy_form.not_unique = true;                    
                }else{
                    $log.info("Category Save Success", response);                    
                    window.location.href = '/maps-admin/categories';                    
                }
                },
                function (response) {
                    $scope.formErrorMessage = response.data;
                }
            );
        };

    });
