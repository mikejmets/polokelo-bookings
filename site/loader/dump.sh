#!/bin/bash
APP_DIR=$1
DATA_DIR=$2
rm -rf $DATA_DIR
mkdir $DATA_DIR
bulkloader.py --dump --kind=Owner --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/owners $APP_DIR
bulkloader.py --dump --kind=Venue --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/venues $APP_DIR
bulkloader.py --dump --kind=PhoneNumber --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/number $APP_DIR
bulkloader.py --dump --kind=Address --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/addresses $APP_DIR
bulkloader.py --dump --kind=EmailAddress --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/emails $APP_DIR
bulkloader.py --dump --kind=Inspection --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/inspections $APP_DIR
bulkloader.py --dump --kind=Complaint --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/complaints $APP_DIR
bulkloader.py --dump --kind=Bedroom --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/bedrooms $APP_DIR
bulkloader.py --dump --kind=Bathroom --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/bathrooms $APP_DIR
bulkloader.py --dump --kind=Bed --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/beds $APP_DIR
rm -rf bulkloader-*
