#!/bin/bash
APP_DIR=$1
DATA_DIR=$2
HOST=$3
rm -rf $DATA_DIR
mkdir $DATA_DIR
echo Dumping Owner
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Owner --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/owners $APP_DIR
echo Dumping Venue
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Venue --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/venues $APP_DIR
echo Dumping Numbers
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=PhoneNumber --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/number $APP_DIR
echo Dumping Addresses
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Address --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/addresses $APP_DIR
echo Dumping Emails
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=EmailAddress --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/emails $APP_DIR
echo Dumping Inspections
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Inspection --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/inspections $APP_DIR
echo Dumping Complaints
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Complaint --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/complaints $APP_DIR
echo Dumping Bedrooms
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Bedroom --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/bedrooms $APP_DIR
echo Dumping Bathrooms
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Bathroom --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/bathrooms $APP_DIR
echo Dumping Beds
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Bed --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/beds $APP_DIR
echo Dumping Berths
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Berth --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/berths $APP_DIR
#echo Dumping Slots
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Slot --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/slots $APP_DIR
echo Dumping Photos
bulkloader.py --dump --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Photograph --url=$HOST/unload --num_threads=1 --filename=$DATA_DIR/photos $APP_DIR
echo Complete
rm -rf bulkloader-*
