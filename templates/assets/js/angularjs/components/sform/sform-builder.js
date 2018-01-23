/**
 * sForm.Builder module contains the custom directives handle how the item to be shown.
 */
angular.module('sForm.Builder', ['sForm', 'ui.bootstrap'])
/**
 * SFormBuilderSettings allows reconfigure the settings for SFormBuilder.
 */
.provider('SFormBuilderSettings', function () {
    var BASE_PATH = './ngtemplates/sform/builder';
    var MODAL_URL = '/modals.html';
    var FORM_TEMPLATE_URL = '/form.html';
    var FIELD_GROUP_TEMPLATE_URL = '/field-group.html';
    var FIELD_TEMPLATE_URL = '/field.html';

    return {
        //set the base path for all other items.
        set_base_path: function (value) {
            BASE_PATH = value;
        },
        //set the url of the modal. The modal url will auto prepend with base path.
        set_modal_url: function (value) {
            MODAL_URL = value;
        },
        //set the url of the builder form template. The modal url will auto prepend with base path.
        set_form_template_url: function (value) {
            FORM_TEMPLATE_URL = value;
        },
        //set the url of the builder field group template. The modal url will auto prepend with base path.
        set_field_group_template_url: function (value) {
            FIELD_GROUP_TEMPLATE_URL = value;
        },
        //set the url of the builder field template. The modal url will auto prepend with base path.
        set_field_template_url: function (value) {
            FIELD_TEMPLATE_URL = value;
        },
        $get: function () {
            return {
                MODAL_URL: BASE_PATH + MODAL_URL,
                FORM_TEMPLATE_URL: BASE_PATH + FORM_TEMPLATE_URL,
                FIELD_GROUP_TEMPLATE_URL: BASE_PATH + FIELD_GROUP_TEMPLATE_URL,
                FIELD_TEMPLATE_URL: BASE_PATH + FIELD_TEMPLATE_URL
            };
        }
    };
})
/**
 * SFormBuilderUtil contains useful functions for buider only.
 */
.service('SFormBuilderUtil', function ($modal, FieldTypes, TrueFalseOptions, SFormBuilderSettings) {
    /**
     * openFieldModal will show the modal for add/update field.
     * the callback function will be called if click 'OK'.
     */
    this.openFieldModal = function (data, callback) {
        var modalInstance = $modal.open({
            templateUrl: SFormBuilderSettings.MODAL_URL,
            size: 'lg',
            backdrop: 'static', //prevent click anyway to close the modal.
            controller: function ($scope, $modalInstance, $window) {
                $scope.modalContent = '/modal-field.html';
                $scope.data = data;
                $scope.FieldTypes = FieldTypes;
                $scope.TrueFalseOptions = TrueFalseOptions;

                $scope.addChoice = function () {
                    data.addChoice();
                };

                $scope.removeChoice = function (choice) {
                    data.removeChoice(choice);
                };

                $scope.ok = function () {
                    $modalInstance.close($scope.data);
                };

                $scope.cancel = function () {
                    $modalInstance.dismiss('cancel');
                };
            }
        });

        modalInstance.result.then(callback);
    };

    /**
     * openFieldGroupModal will show the modal for add/update field group.
     * the callback function will be called if click 'OK'.
     */
    this.openFieldGroupModal = function (data, callback) {
        var modalInstance = $modal.open({
            templateUrl: SFormBuilderSettings.MODAL_URL,
            backdrop: 'static', //prevent click anyway to close the modal.
            controller: function ($scope, $modalInstance, $window) {
                $scope.modalContent = '/modal-field-group.html';
                $scope.data = data;

                $scope.ok = function () {
                    $modalInstance.close($scope.data);
                };

                $scope.cancel = function () {
                    $modalInstance.dismiss('cancel');
                };
                
                $scope.formAvailable = function () {
                    //Determine if Backend Forms are 'addable' in the context
                    if($window.location.href.includes("locations-addlocation") &&
                      !$window.location.href.includes("locations-addlocationtype")){
                        console.log("Disabling backend forms in this context");
                        return false;
                    }
                    return true;
                };

            }
        });

        modalInstance.result.then(callback);
    };

    /**
     * openDeleteModal will show the modal for delete field/field group.
     * the callback function will be called if click 'OK'.
     */
    this.openDeleteModal = function (data, callback) {
        var modalInstance = $modal.open({
            templateUrl: SFormBuilderSettings.MODAL_URL,
            backdrop: 'static', //prevent click anyway to close the modal.
            controller: function ($scope, $modalInstance) {
                $scope.modalContent = '/modal-delete.html';
                $scope.data = data;

                $scope.ok = function () {
                    $modalInstance.close(data);
                };

                $scope.cancel = function () {
                    $modalInstance.dismiss('cancel');
                };

            }
        });

        modalInstance.result.then(callback);
    };
})
/**
 * SFormBuilder service is the main subject that provides API to controller.
 */
.service('SFormBuilder', function (SFormForm) {
    /**
     * the master form object.
     */
    this.sform = new SFormForm();

    /**
     * Return the complete form data.
     */
    this.getData = function () {
        return this.sform.getData();
    };

    /**
     * set the form data. Must follow the same format generated from the 'getData' function.
     */
    this.setData = function (data) {

        if (typeof (data) !== 'object') {
            throw 'Invalid data. Must be an JSON object.';
        }
        this.sform.reset()
        this.sform.setData(data);
    };
})
/**
 * sformBuilder is the top level directive of Builder.
 */
.directive('sformBuilder', function (SFormBuilder) {
    return {
        restrict: 'ACE',
        scope: true,
        controller: function ($scope) {
            $scope.sform = SFormBuilder.sform;
        }
    };
})
/**
 * sformBuilderForm is the second level directive of Builder.
 * It will handle the sformBuilderForm directive.
 * sformBuilderForm also handle create/update/delete of field groups under the form.
 */
.directive('sformBuilderForm', function (SFormBuilderSettings, SFormBuilderUtil) {
    return {
        restrict: 'ACE',
        require: '^sformBuilder',
        terminal: true,
        templateUrl: SFormBuilderSettings.FORM_TEMPLATE_URL,
        controller: function ($scope) {
            $scope.addFieldGroupModal = function (sform) {
                SFormBuilderUtil.openFieldGroupModal({
                    isNew: true,
                }, function (data) {
                    sform.addFieldGroup(data);
                });
            };

            $scope.updateFieldGroupModal = function (fieldGroup) {
                SFormBuilderUtil.openFieldGroupModal(
                angular.extend({isNew: false}, fieldGroup),
                function (data) {
                    fieldGroup.update(data);
                });
            };

            $scope.deleteFieldGroupModal = function (sform, fieldGroup) {
                SFormBuilderUtil.openDeleteModal(
                {
                    title: 'Delete Field Group',
                    message: 'Are you sure?'
                },
                function () {
                    // have result
                    sform.removeFieldGroup(fieldGroup);
                });
            };
        }
    };
})
/**
 * sformBuilderFieldGroup is the fieldGroup directive for Builder.
 * It will handle the sformBuilderFieldGroup directive.
 * sformBuilderFieldGroup also handle create/update/delete of fields under the group.
 */
.directive('sformBuilderFieldGroup', function (SFormBuilderSettings, SFormBuilderUtil, SFormUtil, FieldTypes, SFormField) {
    return {
        restrict: 'ACE',
        require: '^sformBuilderForm',
        terminal: true,
        templateUrl: SFormBuilderSettings.FIELD_GROUP_TEMPLATE_URL,
        controller: function ($scope) {
            $scope.addFieldModal = function (fieldGroup) {
                var lastId = 0;

                SFormBuilderUtil.openFieldModal(
                angular.extend({
                    isNew: true,
                    addChoice: function () {
                        this.choices.push({
                            id: SFormUtil.getNextId(lastId, this.choices),
                            value: '',
                            label: '',
                            default_value: false
                        });
                    },
                    removeChoice: function (choice) {
                        for (var item in this.choices) {
                            if (this.choices[item].id == choice.id) {
                                this.choices.splice(item, 1);
                            }
                        }
                    }
                }, new SFormField({})),
                function (data) {
                    fieldGroup.addField(data);
                });
            };

            $scope.updateFieldModal = function (field) {
                var lastId = 0;

                SFormBuilderUtil.openFieldModal(
                angular.extend({
                    isNew: false,
                    addChoice: function () {
                        this.choices.push({
                            id: SFormUtil.getNextId(lastId, this.choices),
                            value: '',
                            label: '',
                            default_value: false
                        });
                    },
                    removeChoice: function (choice) {
                        for (var item in this.choices) {
                            if (this.choices[item].id == choice.id) {
                                this.choices.splice(item, 1);
                            }
                        }
                    }
                }, field),
                function (data) {
                    field.update(data);
                });
            };

            $scope.deleteFieldModal = function (fieldGroup, field) {
                SFormBuilderUtil.openDeleteModal(
                {
                    title: 'Delete Field',
                    message: 'Are you sure?'
                },
                function () {
                    // have result
                    fieldGroup.removeField(field);
                });
            };
        }
    };
})
/**
 * sformBuilderField is the field directive for Builder.
 * It will handle the sformBuilderField directive.
 */
.directive('sformBuilderField', function (SFormBuilderSettings) {
    return {
        restrict: 'A',
        require: '^sformBuilderFieldGroup',
        templateUrl: SFormBuilderSettings.FIELD_TEMPLATE_URL,
    };
});
