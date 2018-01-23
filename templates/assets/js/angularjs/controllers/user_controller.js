angular.module('myApp')
    .config(function ($interpolateProvider, SFormRendererSettingsProvider, SFormBuilderSettingsProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');

        SFormRendererSettingsProvider.set_base_path('/static/ngtemplates/sform/renderer');
        SFormBuilderSettingsProvider.set_base_path('/static/ngtemplates/sform/builder');
    })

    .controller('UserController', function ($scope, UserManager, UserTypeAPI, OrganizationAPI, SFormRenderer, SFormBuilder) {
        $scope.user = UserManager.model;
        $scope.usertypes = [];
        $scope.orgs = [];
        $scope.formErrorMessage = '';

        UserTypeAPI.list().then(function success(response) {
            for (var item in response.data) {
                $scope.usertypes.push(response.data[item]);

            }
        });

        OrganizationAPI.list().then(function success(response) {
            for (var item in response.data) {
                $scope.orgs.push(response.data[item]);
            }
        });

        $scope.loadData = function (id) {
            if (id == '') {
                return;
            }

            UserManager.load(id, function callbackSuccess() {
                angular.element('.note-editable').html($scope.user.description);

                if ($scope.user.custom_field_form) {
                    var front_end_fg = []
                    fg = $scope.user.custom_field_form.field_groups;
                    for (i in fg) {
                        if (fg[i]['form_type'] == 'front-end') {
                            front_end_fg.push(fg[i]);
                        }
                    }
                    $scope.setSFormBuilderData(front_end_fg);
                }

                var form_data;
                for (var ut in $scope.user.user_types) {
                    form_data = {};
                    if ($scope.user.user_types[ut].custom_field_form) {
                        form_data = $scope.user.user_types[ut].custom_field_form;
                        if ($scope.user.custom_field_form) {
                            form_data = $.extend(true, form_data, $scope.user.custom_field_form);
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

        $scope.submit = function () {
            $scope.formErrorMessage = '';
            if ($scope.user_form.$invalid) {
                return;
            }

            var ut_list = [];
            for (ut in $scope.user.user_types) {
                var tmp = $scope.user.user_types[ut]['id'] || $scope.user.user_types[ut]
                ut_list.push(tmp);
            }
            $scope.user.user_types = ut_list;
            $scope.user.description = angular.element('.note-editable').html();

            var builder_data = JSON.parse($scope.getSFormBuilderData());
            var renderer_data = JSON.parse($scope.getSFormRendererData());
            $scope.user.custom_field_form = [];
            if (builder_data.length > 0) {
                for (i in builder_data) {
                    $scope.user.custom_field_form.push(builder_data[i]);
                }
            }
            if (renderer_data.length > 0) {
                for (i in renderer_data) {
                    $scope.user.custom_field_form.push(renderer_data[i]);
                }
            }
            $scope.user.custom_field_form = JSON.stringify($scope.user.custom_field_form);

            //adding a user on the backend.. means user should be automatically
            //set to active
            $scope.user.is_active = true;
            UserManager.save(function callbackSuccess(response) {
                    $scope.formErrorMessage = 'Saved successfully.';
                    window.location.href = '/maps-admin/users/';
                },
                function callbackError(response) {
                    $scope.formErrorMessage = response.data;
                }
            );
        }
    });
