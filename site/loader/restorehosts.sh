#!/bin/bash
HOST=$1
EMAIL=$2
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Owner --url=$HOST/unload --filename=loader/data/owners .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Venue --url=$HOST/unload --filename=loader/data/venues .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=PhoneNumber --url=$HOST/unload --filename=loader/data/numbers .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Address --url=$HOST/unload --filename=loader/data/addresses .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=EmailAddress --url=$HOST/unload --filename=loader/data/emails .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Complaint --url=$HOST/unload --filename=loader/data/complaints .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Inspection --url=$HOST/unload --filename=loader/data/inspections .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Bedroom --url=$HOST/unload --filename=loader/data/bedrooms .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Bathroom --url=$HOST/unload --filename=loader/data/bathrooms .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Bed --url=$HOST/unload --filename=loader/data/beds .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Berth --url=$HOST/unload --filename=loader/data/berths .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Slot --url=$HOST/unload --filename=loader/data/slots .
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Photograph --url=$HOST/unload --filename=loader/data/photographs .
rm -rf bulkloader-*
