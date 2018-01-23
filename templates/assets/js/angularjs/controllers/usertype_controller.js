angular.module('myApp')
    .config(function(SFormBuilderSettingsProvider) {
        SFormBuilderSettingsProvider.set_base_path('/static/ngtemplates/sform/builder');
    })
    .controller('UserTypeController', function ($scope, UserTypeManager) {
        $scope.deleteItem = function (id) {
            event.preventDefault();
            var msg = 'Are you sure delete the item?';
            if (window.confirm(msg)) {
                UserTypeManager.remove(id,
                    function callbackSuccess(data, status, headers, config) {
                        window.location.href = '/maps-admin/users/user-types/';
                    }
                );
            }
        };

    })
    .controller('UserTypeFormController', function ($scope, UserTypeManager, Permission, TrueFalse, SFormBuilder) {
        $scope.userType = UserTypeManager.model;

        $scope.formErrorMessage = '';
        $scope.canRegister = TrueFalse;
        $scope.needAuthorization = TrueFalse;

        $scope.permissions = Permission;

        $scope.loadData = function (id) {
            if (id === '') {
                return;
            }

            UserTypeManager.load(id, function callbackSuccess() {
                if ($scope.userType.custom_field_form) {
                    $scope.setSFormBuilderData($scope.userType.custom_field_form.field_groups);
                }
            });
        };

        $scope.setSFormBuilderData = function (data) {
            if (data === '') {
                data = [];
            } else {
                data = JSON.parse(data);
            }
            SFormBuilder.setData(data);
        };

        $scope.getSFormBuilderData = function () {
            return angular.toJson(SFormBuilder.getData());
        };

        $scope.submit = function () {
            $scope.formErrorMessage = '';
            if ($scope.user_type_form.$invalid) {
                return;
            }

            $scope.userType.custom_field_form = $scope.getSFormBuilderData();
            if($scope.userType.custom_field_form === "[]"){
                delete $scope.userType.custom_field_form;
            }

            UserTypeManager.save(function callbackSuccess(response) {
                    window.location.href = '/maps-admin/users/user-types/';
                },function callbackError(response) {
                    if(response.data.indexOf('duplicate') > 1){
                        $scope.formErrorMessage = "This name is taken";
                    }else{
                        $scope.formErrorMessage = response.data;                        
                    }
                }
            );
        };
    });
