angular.module('myApp')
    .config(function(SFormBuilderSettingsProvider) {
        SFormBuilderSettingsProvider.set_base_path('/static/ngtemplates/sform/builder');
    })
    .controller('CategoryFormController', function ($scope, CategoryManager, CategoryAPI, Category, Taxonomy,
                                                    TaxonomyAPI, mappdata, $timeout, PrivacyOptions, SFormBuilder,
                                                    $log) {
        $scope.category = CategoryManager.model;
        $scope.alert = false;
        $scope.description_error = false;
        $scope.taxonomy = [];
        $scope.privacyOptions = PrivacyOptions;

        $scope.loadData = function (id) {
            if (id == '') {
                return;
            }
            CategoryManager.load(id, function callbackSuccess() {
                if ($scope.category.custom_field_form) {
                    $scope.setSFormBuilderData($scope.category.custom_field_form.field_groups);
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
                    $scope.taxonomy.push(_model);
                }
            }
        );

        $scope.submit = function () {
            var _has_error = false;
            // $scope.category_form.not_unique = false;
            if ($scope.categories_form.$invalid) {
                _has_error = true;
            }

            //fixed for summernote
            $scope.category.description = angular.element('.note-editable').text();

            if ($scope.description_error = ($scope.category.description.length == 0)) {
                _has_error = true;
            }

            if (_has_error) {
                return;
            }
            $scope.category.custom_field_form = $scope.getSFormBuilderData();

            CategoryManager.save(function(response) {
                if(response.data.error !== null && response.data.error === "NotUniqueError"){
                    $log.error('Caught NotUniqueError, Tag Name not unique: ', $scope.category.name)
                    $scope.formErrorMessage = "NotUniqueError";
                    $scope.categories_form.not_unique = true;                    
                }else{
                    $log.info("Category Save Success", response);                    
                    window.location.href = '/maps-admin/categories';                    
                }
            },function(response) {
                $log.error("Category Save Failed", response);
                $scope.formErrorMessage = response.data;
            }
                                );
        };

    });
