#!/bin/bash
HOST=$1
EMAIL=$2
APP_ID=polokelo-bookings
echo "-------------- Dump Lookup Tables"
rm -rf loader/data/lookups
bulkloader.py --dump --num_threads=1 --app_id=$APP_ID --email=$EMAIL --kind=CodeLookup --url=$HOST/unload --filename=loader/data/lookups .
echo "-------------- Dump Packages"
rm -rf loader/data/packages
bulkloader.py --dump --num_threads=1 --app_id=$APP_ID --email=$EMAIL --kind=Package --url=$HOST/unload --filename=loader/data/packages .
echo "-------------- Dump Match Schedules"
rm -rf loader/data/matches
bulkloader.py --dump --num_threads=1 --app_id=$APP_ID --email=$EMAIL --kind=Match --url=$HOST/unload --filename=loader/data/matches .
echo "-------------- Dump userRoles"
rm -rf loader/data/userroles
bulkloader.py --dump --num_threads=1 --app_id=$APP_ID --email=$EMAIL --kind=UserRole --url=$HOST/unload --filename=loader/data/userroles .
rm -rf bulkloader-*
