#!/bin/bash
APP_DIR=$1
DATA_DIR=$2
HOST=$3
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Owner --url=$HOST/unload --filename=$DATA_DIR/owners $APP_DIR
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Venue --url=$HOST/unload --filename=$DATA_DIR/venues $APP_DIR
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=PhoneNumber --url=$HOST/unload --filename=$DATA_DIR/number $APP_DIR
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Address --url=$HOST/unload --filename=$DATA_DIR/addresses $APP_DIR
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=EmailAddress --url=$HOST/unload --filename=$DATA_DIR/emails $APP_DIR
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Inspection --url=$HOST/unload --filename=$DATA_DIR/inspections $APP_DIR
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Complaint --url=$HOST/unload --filename=$DATA_DIR/complaints $APP_DIR
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Bedroom --url=$HOST/unload --filename=$DATA_DIR/bedrooms $APP_DIR
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Bathroom --url=$HOST/unload --filename=$DATA_DIR/bathrooms $APP_DIR
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Bed --url=$HOST/unload --filename=$DATA_DIR/beds $APP_DIR
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Berth --url=$HOST/unload --filename=$DATA_DIR/berths $APP_DIR
bulkloader.py --restore --app_id=bookings-dev --email=mikejmets@gmail.com --kind=Photograph --url=$HOST/unload --filename=$DATA_DIR/photos $APP_DIR
rm -rf bulkloader-*
