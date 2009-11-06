#!/bin/bash
APP_DIR=$1
DATA_DIR=$2
HOST=$3
rm -rf $DATA_DIR
mkdir $DATA_DIR
bulkloader.py --dump --kind=Owner --url=$HOST/unload --filename=$DATA_DIR/owners $APP_DIR
bulkloader.py --dump --kind=Venue --url=$HOST/unload --filename=$DATA_DIR/venues $APP_DIR
bulkloader.py --dump --kind=PhoneNumber --url=$HOST/unload --filename=$DATA_DIR/number $APP_DIR
bulkloader.py --dump --kind=Address --url=$HOST/unload --filename=$DATA_DIR/addresses $APP_DIR
bulkloader.py --dump --kind=EmailAddress --url=$HOST/unload --filename=$DATA_DIR/emails $APP_DIR
bulkloader.py --dump --kind=Inspection --url=$HOST/unload --filename=$DATA_DIR/inspections $APP_DIR
bulkloader.py --dump --kind=Complaint --url=$HOST/unload --filename=$DATA_DIR/complaints $APP_DIR
bulkloader.py --dump --kind=Bedroom --url=$HOST/unload --filename=$DATA_DIR/bedrooms $APP_DIR
bulkloader.py --dump --kind=Bathroom --url=$HOST/unload --filename=$DATA_DIR/bathrooms $APP_DIR
bulkloader.py --dump --kind=Bed --url=$HOST/unload --filename=$DATA_DIR/beds $APP_DIR
rm -rf bulkloader-*
