angular.module('myApp')
    .controller('OrganizationController', function ($scope, OrganizationManager, PrivacyOptions) {
        $scope.organization = OrganizationManager.model;
        $scope.privacyOptions = PrivacyOptions;

        $scope.disableSubmit = false;

        $scope.formErrorMessage = '';

        $scope.loadData = function (id) {
            if (id == '') {
                return;
            }

            OrganizationManager.load(id);
        };

        $scope.submit = function () {
            $scope.disableSubmit = true;
            $scope.formErrorMessage = '';
            if ($scope.org_form.$invalid) {
                $scope.disableSubmit = false;
                return;
            }

            $scope.formErrorMessage = 'Sending data...';
            OrganizationManager.save(function callbackSuccess(response) {
                    $scope.formErrorMessage = 'Saved successfully.';
                    window.location.href = '/maps-admin/users/';
                },function callbackError(response) {
                    if(response.data.indexOf('duplicate') > 1){
                        $scope.formErrorMessage = "This name is taken";
                    }else{
                        $scope.formErrorMessage = response.data;
                    }                              
                    $scope.disableSubmit = false;
                }
            );
        };
    });
