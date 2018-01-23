DATA_IMPORT_OPTIONS = {
    'upload_type': {
        '0': 'File',
        '1': 'Live Feed',
    },
    'upload_format': {
        '0': 'CSV',
        '1': 'JSON',
        '2': 'Shape File (zipped)',
        '3': 'GeoJSON',
    },
    'system_upload_format': {
        '0': 'CSV',
        '1': 'JSON',
        '2': 'GEOJSON'
    },
    'content_status': {
        '0': 'Published',
        '1': 'Not Published',
    },
    'upload_freq': {
        '1': '1 day',
        '3': '3 day',
    },
    'duplicate_content': {
        '0': 'Replace',
        '1': 'Add New',
    },
    'content_type': {
        '0': 'Locations',
        '1': 'Location Types',
        '2': 'Users',
        '3': 'Categories',
        '4': 'Organizations',
        '5': 'Tags',
    },
}

DATA_NORMALIZATION_FIELDS = [
    'name',
    'description',
    'formatted_address',
    'image_url',
    'icon_url',
    'geometry_type',
    'coordinates',
]

PRIVACY_OPTION = {
    'allow_user_type': {
        '0': 'Everyone',
        '1': 'Logged In',
        '2': 'Provider',
        '3': 'Buyer',
        '4': 'Landholder',
        '5': 'Grower'
    },
    'model_type': {
        '0': 'Location Type',
        '1': 'User Type',
        '2': 'Page',
        '3': 'Category',
        '4': 'Taxonomy'
    }
}

PERMISSION = {
    'Locations': {
        '0': 'Can Add Locations',
        '1': 'Can Edit Own Locations',
        '2': 'Can Delete Own Locations',
        '3': 'Can Edit Custom Location Types',
        '4': 'Can Edit Others Locations',
        '5': 'Can Delete Others Locations',
        '6': 'Can Add Custom Location Types',
        '7': 'Can Delete Custom Location Types'
    },
    'Categories': {
        '0': 'Can Add Tag',
        '1': 'Can Edit Own Tags',
        '2': 'Can Delete Own Tags',
        '3': 'Can Add Category',
        '4': 'Can Edit Others Categories',
        '5': 'Can Delete Others Categories',
        '6': 'Can Add Custom Categories',
        '7': 'Can Delete Custom Categories'
    },
    'Users': {
        '0': 'Can Add Users',
        '1': 'Can Edit Own Users',
        '2': 'Can Delete Own Users',
        '3': 'Can Edit Custom User Types',
        '4': 'Can Edit Others Users',
        '5': 'Can Delete Others Users',
        '6': 'Can Add Custom User Types',
        '7': 'Can Delete Custom User Types'
    },
    'Forms': {
        '0': 'Can Add Forms',
        '1': 'Can Edit Own Forms',
        '2': 'Can Delete Own Forms',
        '3': 'Can Edit Custom Form Types',
        '4': 'Can Edit Others Forms',
        '5': 'Can Delete Others Forms',
        '6': 'Can Add Custom Forms',
        '7': 'Can Delete Custom Forms'
    },
    'Resources': {
        '0': 'Can Add Resources',
        '1': 'Can Edit Own Resources',
        '2': 'Can Delete Own Resources',
        '3': 'Can Edit Others Resources',
        '4': 'Can Delete Others Resources',
        '5': 'Can Edit Resources Settings'
    },
    'Settings': {
        '0': 'Can Edit Global  Settings',
    }
}
