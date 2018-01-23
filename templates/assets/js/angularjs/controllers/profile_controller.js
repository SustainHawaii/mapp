var app = angular.module('myApp')

    .config(function ($interpolateProvider, SFormRendererSettingsProvider, SFormBuilderSettingsProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');

        SFormRendererSettingsProvider.set_base_path('/static/ngtemplates/sform/renderer');
        SFormBuilderSettingsProvider.set_base_path('/static/ngtemplates/sform/builder');
    })

    .controller('ProfileController', function ($scope, UserProfileManager, SFormRenderer, SFormBuilder) {
        $scope.profile = UserProfileManager.model;
        $scope.formErrorMessage = '';
        $scope.formInfo = null;
        $scope.formMessage = '';
        $scope.avatar = '/static/img/avatars/male.png';

        $scope.loadData = function (id) {
            if (id == '') {
                return;
            }
            UserProfileManager.load(id, function callbackSuccess() {
                if ($scope.profile.image != 'null' && $scope.profile.image != '') {
                    $scope.avatar = '/media/' + $scope.profile.image;
                }

                angular.element('.note-editable').html($scope.profile.description);

                if ($scope.profile.custom_field_form) {
                    var front_end_fg = []
                    fg = $scope.profile.custom_field_form.field_groups;
                    for (i in fg) {
                        if (fg[i]['form_type'] == 'front-end') {
                            front_end_fg.push(fg[i]);
                        }
                    }
                    $scope.setSFormBuilderData(front_end_fg);
                }

                var form_data;
                for (var ut in $scope.profile.user_types) {
                    form_data = {};
                    if ($scope.profile.user_types[ut].custom_field_form) {
                        form_data = $scope.profile.user_types[ut].custom_field_form;
                        if ($scope.profile.custom_field_form) {
                            form_data = $.extend(true, form_data, $scope.profile.custom_field_form);
                        }
                        var back_end_fg = [];
                        for (i in form_data.field_groups) {
                            if (form_data.field_groups[i]['form_type'] == 'back-end') {
                                back_end_fg.push(form_data.field_groups[i]);
                            }
                        }
                        $scope.setSFormRendererData(back_end_fg);
                    }
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

        $scope.setSFormRendererData = function (data) {
            if (data === '') {
                data = [];
            }

            SFormRenderer.setData(data);
        };

        $scope.getSFormRendererData = function () {
            return angular.toJson(SFormRenderer.getData());
        };

        $scope.files = [];
        $scope.$on("fileSelected", function (event, args) {
            $scope.$apply(function () {
                reader = new FileReader();
                reader.onload = function(e) {
                        $scope.avatar = e.target.result;
                        $scope.$apply();
                    };
                reader.readAsDataURL(args.file);
                $scope.files.push(args.file);
            });
        });

        $scope.submit = function () {
            $scope.formErrorMessage = '';
            if ($scope.profile_form.$invalid) {
                return;
            }

            var builder_data = JSON.parse($scope.getSFormBuilderData());
            var renderer_data = JSON.parse($scope.getSFormRendererData());
            $scope.profile.custom_field_form = [];
            if (builder_data.length > 0) {
                for (i in builder_data) {
                    $scope.profile.custom_field_form.push(builder_data[i]);
                }
            }
            if (renderer_data.length > 0) {
                for (i in renderer_data) {
                    $scope.profile.custom_field_form.push(renderer_data[i]);
                }
            }
            $scope.profile.custom_field_form = JSON.stringify($scope.profile.custom_field_form);

            $scope.profile.description = angular.element('.note-editable').html();

            UserProfileManager.save(function callbackSuccess(response) {
                    $scope.formErrorMessage = 'Saved successfully.';
                    window.location.href = '/maps-admin/profile/';
                },
                function callbackError(response) {
                    $scope.formErrorMessage = response.data;
                },
                $scope.files
            );
        }
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
    }
});

app.directive('fileUpload', function () {
    return {
        link: function (scope, el, attrs) {
            el.bind('change', function (event) {
                var files = event.target.files;
                for (var i = 0;i<files.length;i++) {
                    scope.$emit("fileSelected", { file: files[i] });
                }
            });
        }
    }
});
