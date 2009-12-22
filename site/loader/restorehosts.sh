#!/bin/bash
HOST=$1
EMAIL=$2
APP_ID=$3
echo "------------- Restore owners"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Owner --url=$HOST/unload --filename=loader/data/owners .
echo "------------- Restore venues"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Venue --url=$HOST/unload --filename=loader/data/venues .
echo "------------- Restore numbers"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=PhoneNumber --url=$HOST/unload --filename=loader/data/numbers .
echo "------------- Restore addresses"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Address --url=$HOST/unload --filename=loader/data/addresses .
echo "------------- Restore emails"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=EmailAddress --url=$HOST/unload --filename=loader/data/emails .
echo "------------- Restore complaints"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Complaint --url=$HOST/unload --filename=loader/data/complaints .
echo "------------- Restore inspections"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Inspection --url=$HOST/unload --filename=loader/data/inspections .
echo "------------- Restore bedrooms"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Bedroom --url=$HOST/unload --filename=loader/data/bedrooms .
echo "------------- Restore bathrooms"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Bathroom --url=$HOST/unload --filename=loader/data/bathrooms .
echo "------------- Restore beds"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Bed --url=$HOST/unload --filename=loader/data/beds .
echo "------------- Restore berths"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Berth --url=$HOST/unload --filename=loader/data/berths .
echo "------------- Restore photos"
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Photograph --url=$HOST/unload --filename=loader/data/photos .
#echo "------------- Restore slots"
#bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Slot --url=$HOST/unload --filename=loader/data/slots .
rm -rf bulkloader-*
