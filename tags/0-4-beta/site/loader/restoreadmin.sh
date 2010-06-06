#!/bin/bash
HOST=$1
EMAIL=$2
APP_ID=$3
echo ---------- Restore Loopkup tables
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=CodeLookup --url=$HOST/unload --filename=loader/data/lookups .
echo ---------- Restore Packages
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Package --url=$HOST/unload --filename=loader/data/packages .
echo ---------- Restore matches schedules
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Match --url=$HOST/unload --filename=loader/data/matches .
echo ---------- Restore user roles
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=UserRole --url=$HOST/unload --filename=loader/data/userroles .
rm -rf bulkloader-*
