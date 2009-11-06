#!/bin/bash
APP_DIR=$1
DATA_DIR=$2
bulkloader.py --restore --kind=Owner --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/owners $APP_DIR
bulkloader.py --restore --kind=Venue --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/venues $APP_DIR
bulkloader.py --restore --kind=PhoneNumber --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/number $APP_DIR
bulkloader.py --restore --kind=Address --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/addresses $APP_DIR
bulkloader.py --restore --kind=EmailAddress --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/emails $APP_DIR
bulkloader.py --restore --kind=Inspection --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/inspections $APP_DIR
bulkloader.py --restore --kind=Complaint --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/complaints $APP_DIR
bulkloader.py --restore --kind=Bedroom --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/bedrooms $APP_DIR
bulkloader.py --restore --kind=Bathroom --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/bathrooms $APP_DIR
bulkloader.py --restore --kind=Bed --url=http://bookings-dev.appspot.com/unload --filename=$DATA_DIR/beds $APP_DIR
