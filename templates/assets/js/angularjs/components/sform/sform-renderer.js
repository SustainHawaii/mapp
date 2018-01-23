angular.module('sForm.Renderer', ['sForm', 'ui.bootstrap'])
.provider('SFormRendererSettings', function () {
    var BASE_PATH = './ngtemplates/sform/renderer';
    var FORM_TEMPLATE_URL = '/form.html';
    var FIELD_GROUP_TEMPLATE_URL = '/field-group.html';
    var FIELD_TEMPLATE_URL = '/field.html';

    return {
        set_base_path: function(value) {
            BASE_PATH = value;
        },
        set_form_template_url: function(value) {
            FORM_TEMPLATE_URL = value;
        },
        set_field_group_template_url: function(value) {
            FIELD_GROUP_TEMPLATE_URL = value;
        },
        set_field_template_url: function(value) {
            FIELD_TEMPLATE_URL = value;
        },
        $get: function() {
            return {
                FORM_TEMPLATE_URL: BASE_PATH + FORM_TEMPLATE_URL,
                FIELD_GROUP_TEMPLATE_URL: BASE_PATH + FIELD_GROUP_TEMPLATE_URL,
                FIELD_TEMPLATE_URL: BASE_PATH + FIELD_TEMPLATE_URL,
            };
        }
    };
})
.service('SFormRenderer', function (SFormForm) {
    this.sform = new SFormForm();
    this.getData = function () {
        return this.sform.getData();
    };

    this.setData = function (data) {
        if (typeof(data) !== 'object') {
            throw 'Invalid data. Must be a JSON object.';
        }
        this.sform.setData(data);
    };
    this.reset = function() {
        this.sform.reset();
    }
})
.directive('sformRenderer', function (SFormRenderer) {
    return {
        restrict: 'ACE',
        scope: true,
        controller: function ($scope) {
            $scope.sform = SFormRenderer.sform;
        }
    };
})
.directive('sformRendererForm', function (SFormRendererSettings) {
    return {
        restrict: 'ACE',
        require: '^sformRenderer',
        terminal: true,
        templateUrl: SFormRendererSettings.FORM_TEMPLATE_URL,
        controller: function ($scope) {
        }
    };
})
.directive('sformRendererFieldGroup', function (SFormRendererSettings) {
    return {
        restrict: 'ACE',
        require: '^sformRendererForm',
        terminal: true,
        templateUrl: SFormRendererSettings.FIELD_GROUP_TEMPLATE_URL,
        controller: function ($scope) {
        }
    };
})
.directive('sformRendererField', function (SFormRendererSettings) {
    return {
        restrict: 'A',
        require: '^sformRendererFieldGroup',
        templateUrl: SFormRendererSettings.FIELD_TEMPLATE_URL,
    };
});
