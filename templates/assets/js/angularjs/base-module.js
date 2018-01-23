(function(){
    "use strict";
    angular.module('myApp', ['angularFileUpload','summernote', 'UserProfileModule', 'CategoryModule', 'TaxonomyModule',
                             'UserModule', 'UserTypeModule', 'OrganizationModule', 'ui.select', 'ui.select2',
                             'sForm.Renderer', 'sForm.Builder', 'ui.bootstrap', 'checklist-model',
                             'smart-table', 'highcharts-ng', 'ngRoute', 'ngSanitize', 'socialLinks', 'ngMaps',
                             'mapp_data', 'datavizApp', 'previewLocation', 'ResourceModule'
                            ])
        .config(baseConfig)
        .value('PrivacyOptions', [
            'Everyone',
            'Logged In',
            'Product',
            'Landholders'
        ])
        .value('Compares', [
            'Is Equal To',
            'Is Not Equal To'
        ])
        .value('ModelGroup', [
            'User Types',
            'Locations',
            'Categories'
        ])
        .value('TrueFalse', [
            true,
            false
        ])
        .filter('trueFalseToYesNo', function () {
            return function (value) {
                return value ? 'Yes' : 'No';
            };
        })
        .filter('excludeOption', function() {
            return function (items, id) {
                return items.reduce(function(lastVal, currVal) {
                    return (currVal.id != id) ? lastVal.concat(currVal): lastVal;
                }, []);
            };
        })
        .directive("passwordVerify", function () {
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
        })
        .filter('CapitalizeFilter', function() {
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

    function baseConfig($interpolateProvider, $httpProvider, SFormRendererSettingsProvider, SFormBuilderSettingsProvider){
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');

        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

        SFormRendererSettingsProvider.set_base_path('/static/ngtemplates/sform/renderer');
        SFormBuilderSettingsProvider.set_base_path('/static/ngtemplates/sform/builder');        
    }
    baseConfig.$index = ["$interpolateProvider", "$httpProvider", "SFormRendererSettingsProvider", "SFormBuilderSettingsProvider"];
})();
