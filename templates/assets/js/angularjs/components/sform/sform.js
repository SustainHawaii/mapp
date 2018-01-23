/**
 * The core engine of the sForm module. This module mainly contains the factories
 * of the models.
 */
angular.module('sForm', [])
/**
 * FieldTypes contains list of the supported field types.
 * This is used in the ng-options for select.
 */
.value('FieldTypes', [
    'text',
    'textarea',
    'number',
    'email',
    'date',
    'select',
])
/**
 * FieldTypesMap is the output value for the field types' id.
 * This is used to convert the type id to better value.
 */
.value('FieldTypesMap', [
    {id: 'text', value: 'Text'},
    {id: 'textarea', value: 'Text Area'},
    {id: 'number', value: 'Number'},
    {id: 'email', value: 'Email'},
    {id: 'date', value: 'Date'},
    {id: 'select', value: 'Select'},
])
/**
 * TrueFalseOptions contains valid value for True/False options.
 * Used this to avoid the value being stored as string.
 */
.value('TrueFalseOptions', [
    true,
    false
])
/**
 * TrueFalseOptionsMap convert the True/False to Yes/No.
 */
.value('TrueFalseOptionsMap', [
    {id: 'true', value: 'Yes'},
    {id: 'false', value: 'No'},
])
/**
 * toFieldTypeString filter convert the field type id to better value.
 */
.filter('toFieldTypeString', function (FieldTypesMap) {
    return function (value) {
        for (var type in FieldTypesMap) {
            if (value == FieldTypesMap[type].id) {
                return FieldTypesMap[type].value;
            }
        }
        return '#Error: invalid field type.';
    };
})
/**
 * TrueFalsetoYesNo filter convert the True/False to Yes/No.
 */
.filter('TrueFalsetoYesNo', function (TrueFalseOptionsMap) {
    return function (value) {
        for (var type in TrueFalseOptionsMap) {
            if (String(value) == TrueFalseOptionsMap[type].id) {
                return TrueFalseOptionsMap[type].value;
            }
        }
        return '#Error: invalid value.';
    };
})
/**
 * SFormField is a model factory to create a standard Field object.
 * SFormField can set to many types including Text, Text Area, Number, Email, Date, Select.
 */
.factory('SFormField', function (FieldTypes, SFormUtil) {
    return function (data) {
        /**
         * Initialize default settings.
         */

        /**
         * id of the field. No limitation on the value.
         * Can be assigned any value that suit your system.
         */
        this.id = null;

        /**
         * field's name to be show on HTML. Required.
         */
        this.name = '';

        /**
         * field's type from FieldTypes. default to 'text'.
         */
        this.type = FieldTypes[0];

        /**
         * field requirement. if set to true, the renderer form will not submit if the field is empty.
         * default to true.
         */
        this.required = true;

        /**
         * field description. for private used only. Description will not show on renderer form.
         */
        this.description = '';

        /**
         * Instructions are extra text below the field.
         */
        this.instructions = '';

        /**
         * Placeholder are the grey text in the input element. Not apply to select element.
         * (Can use other plugin to show placeholder e.g. select2)
         */
        this.placeholder = '';

        /**
         * The Default value of the field. Not apply to select element.
         */
        this.default_value = '';

        /**
         * Total character limit for the text area type only.
         */
        this.character_limit = '';

        /**
         * The minimum value for the number field type. Set empty string to no limit.
         */
        this.min_value = '';

        /**
         * The maximum value for the number field type. Set empty string to no limit.
         */
        this.max_value = '';

        /**
         * The display format for the date field type. See the jQuery datepicker for the supported format.
         */
        this.display_format = '';

        /**
         * The choices for select field type.
         */
        this.choices = [];

        /**
         * Set the select field type to accept multiple values.
         * @type {boolean}
         */
        this.multiple = false;

        /**
         * The actual value input from renderer form.
         */
        this.value = '';

        /**
         * Update current object based on 'data' parameter.
         * @param data
         */
        this.update = function (data) {
            this.setData(data);
        };

        /**
         * Return data from current object.
         */
        this.getData = function () {
            return {
                id: this.id,
                name: this.name,
                type: this.type,
                required: this.required,
                description: this.description,
                instructions: this.instructions,
                placeholder: this.placeholder,
                default_value: this.default_value,
                character_limit: this.character_limit,
                min_value: this.min_value,
                max_value: this.max_value,
                display_format: this.display_format,
                choices: this.choices,
                multiple: this.multiple,
                value: this.value
            };
        };

        this.setData = function(data) {
            for (var k in data) {
                if (k in this) {
                    this[k] = data[k];
                }
            }
        }

        this.init = function (data) {
            this.setData(data);

            // set default value
            if (this.default_value != '' && this.value == '') {
                if (this.type == 'textarea') {
                    if (this.character_limit >= this.default_value.length) {
                        this.value = this.default_value;
                    }
                }
                else if (this.type == 'number') {
                    this.default_value = parseFloat(this.default_value);
                    if (!(
                        (this.min_value != '' && this.min_value > this.default_value) ||
                        (this.max_value != '' && this.max_value < this.default_value)
                        )) {
                            this.value = this.default_value;
                    }
                }
                else if (this.type == 'text') {
                    this.value = this.default_value;
                }
                else if (this.type == 'date') {
                    var isValid = SFormUtil.validateDate(this.display_format, this.default_value);
                    if (isValid) {
                        this.value = this.default_value;
                    }
                }
            }

            // add blank option for single select
            if (this.type == 'select') {
                if (this.multiple == false && this.required == false) {
                    this.choices.unshift({
                                        "default_value": true,
                                         "id": 0,
                                        "value": "",
                                        "label": ""
                                   });
                }
            }
        }

        this.init(data);
    };
})
/**
 * SFormFieldGroup is a model factory to create a standard Field Group object.
 * SFormFieldGroup can contains many fields.
 */
.factory('SFormFieldGroup', function (SFormField, SFormUtil) {
    /**
     * lastId keep the last assigned ID of the fields in this group.
     * This is temporary used to make new field id unique.
     */
    var lastId = 0;

    return function (data) {
        /**
         * The list of fields under this group.
         */
        this.fields = [];

        /**
         * Update current object based on 'data' parameter.
         * @param data
         */
        this.update = function (data) {
            this.id = data.id;
            this.name = data.name;
            this.form_type = data.form_type;
        };

        /**
         * Append a new field into the fields list.
         */
        this.addField = function (data) {
            data.id = SFormUtil.getNextId(lastId, this.fields);
            this.fields.push(new SFormField(data));
        };

        /**
         * Remove a field from the fields list.
         */
        this.removeField = function (field) {
            for (var f in this.fields) {
                if (this.fields[f].id == field.id) {
                    this.fields.splice(f, 1);
                }
            }
        };

        /**
         * Automatically load fields from existing data.
         */
        this.loadFields = function (data) {
            for (var f in data) {
                this.addField(data[f]);
            }
        };

        /**
         * Return data from current object and fields.
         */
        this.getData = function () {
            var data = {
                id: this.id,
                name: this.name,
                form_type: this.form_type,
                fields: []
            };

            for (var i in this.fields) {
                data.fields.push(this.fields[i].getData());
            }

            return data;
        };

        this.update(data);

        //check have existing data.
        if (data.fields) {
            this.loadFields(data.fields);
        }
    };
})
/**
 * SFormForm is a model factory to create a standard Form object.
 * SFormForm can contains many field groups.
 * Usually, we just need one SFormForm as the master object.
 */
.factory('SFormForm', function (SFormFieldGroup, SFormUtil) {
    /**
     * lastId keep the last assigned ID of the field groups in this form.
     * This is temporary used to make new field group id unique.
     */
    var lastId = 0;

    return function () {
        /**
         * The list of field groups under this form.
         */
        this.fieldGroups = [];

        /**
         * Append a new field group into the fieldGroups list.
         */
        this.addFieldGroup = function (data) {
            if (!data.id) {
                data.id = SFormUtil.getNextId(lastId, this.fieldGroups);
            }

            var newGroup = new SFormFieldGroup(data);
            this.fieldGroups.push(newGroup);
        };

        /**
         * Automatically load field groups from existing data.
         */
        this.loadFieldGroups = function (data) {
            for (var fg in data) {
                this.addFieldGroup(data[fg]);
            }
        };

        /**
         * Remove a field group from the fieldGroups list.
         */
        this.removeFieldGroup = function (group) {
            for (var g in this.fieldGroups) {
                if (this.fieldGroups[g].id == group.id) {
                    this.fieldGroups.splice(g, 1);
                }
            }
        };

        /**
         * Return data from current object and fieldGroups.
         */
        this.getData = function () {
            var fieldGroups = [];
            for (var i in this.fieldGroups) {
                fieldGroups.push(this.fieldGroups[i].getData());
            }

            return fieldGroups;
        };

        /**
         * The main function to load existing data.
         */
        this.setData = function (data) {
            this.loadFieldGroups(data);
        };
        
        this.reset = function() {
            this.fieldGroups = [];
        }
    };
})
/**
 * SFormUtil service contains helpful reusable functions.
 */
.service('SFormUtil', function () {
    this.getNextId = function (lastId, items) {
        if (items.length !== 0) {
            for (var i in items) {
                lastId = Math.max(items[i].id, lastId);
            }
        }
        return lastId + 1;
    };
    this.validateDate = function(date_format, date) {
        dict = {};
        arrFormat = date_format.split('/');
        arrDate = date.split('/');

        for (i in arrFormat) {
            dict[arrFormat[i]] = arrDate[i];
        }

        d = new Date(dict['y'], dict['m'], dict['d']);

        return d.getFullYear() == dict['y'] && d.getMonth() == dict['m'] && d.getDate() == dict['d'];
    }
})
;
