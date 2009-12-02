#!/bin/bash
HOST=$1
EMAIL=$2
echo "-------------- Dump owners"
rm -rf loader/data/owners
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=Owner --url=$HOST/unload --filename=loader/data/owners .
echo "-------------- Dump venues"
rm -rf loader/data/venues
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=Venue --url=$HOST/unload --filename=loader/data/venues .
echo "-------------- Dump numbers"
rm -rf loader/data/numbers
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=PhoneNumber --url=$HOST/unload --filename=loader/data/numbers .
echo "-------------- Dump addresses"
rm -rf loader/data/addresses
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=Address --url=$HOST/unload --filename=loader/data/addresses .
echo "-------------- Dump emails"
rm -rf loader/data/emails
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=EmailAddress --url=$HOST/unload --filename=loader/data/emails .
echo "-------------- Dump complaints"
rm -rf loader/data/com plaints
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=Complaint --url=$HOST/unload --filename=loader/data/complaints .
echo "-------------- Dump inspections"
rm -rf loader/data/inspections
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=Inspection --url=$HOST/unload --filename=loader/data/inspections .
echo "-------------- Dump bedrooms"
rm -rf loader/data/bedrooms
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=Bedroom --url=$HOST/unload --filename=loader/data/bedrooms .
echo "-------------- Dump bathrooms"
rm -rf loader/data/bathrooms
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=Bathroom --url=$HOST/unload --filename=loader/data/bathrooms .
echo "-------------- Dump beds"
rm -rf loader/data/beds
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=Bed --url=$HOST/unload --filename=loader/data/beds .
echo "-------------- Dump berths"
rm -rf loader/data/berths
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=Berth --url=$HOST/unload --filename=loader/data/berths .
echo "-------------- Dump slots"
rm -rf loader/data/slots
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=Slot --url=$HOST/unload --filename=loader/data/slots .
echo "-------------- Dump photos"
rm -rf loader/data/photos
bulkloader.py --dump --app_id=bookings-dev --email=$EMAIL --kind=Photograph --url=$HOST/unload --filename=loader/data/photos .
rm -rf bulkloader-*

