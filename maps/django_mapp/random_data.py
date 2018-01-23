import json


def random():
    with open('maps/datastore/data.json') as data_file:
        data = json.loads(data_file.read())

    return data
