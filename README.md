## New project Start

The "historic" project stuff including, ckan, original html designs, etc... is stored in a branch called "historic".

Moving forward this will house the Django project for Mapps


Make sure the libjpeg is installed before install the Pillow.

```
sudo apt-get install libjpeg libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev
```

If Pillow already installed before the libjpeg, please reinstall Pillow.
-

## The Maps DB Bacckup
We have implemented an automated backup of the mongodb database that syncs to S3 on an hourly basis. Below is the script we have implemented to run as a cronjob:
```
#!/bin/bash

sudo mongodump --out /opt
cd opt
sudo zip -r mapsdb_$(date +'%Y_%m_%d_%H:%M').zip Maps
aws s3 cp /opt/mapsdb_$(date +'%Y_%m_%d_%H:%M').zip s3://elasticbeanstalk-ap-southeast-1-130579119144/
sudo rm -rf mapsdb_$(date +'%Y_%m')*.zip
```
This will create a zip file like 'mapsdb_2015_10_07_01:40.zip' and store it in the bucket 'elasticbeanstalk-ap-southeast-1-130579119144'.

To restore the db, we grab the backup from s3, unzip it and run commands like below to restore:
```
mongorestore -d Maps ~/Downloads/Maps

```