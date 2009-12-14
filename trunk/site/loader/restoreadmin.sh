#!/bin/bash
HOST=$1
EMAIL=$2
APP_ID=polokelo-bookings
echo ---------- Restore Loopkup tables
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=CodeLookup --url=$HOST/unload --filename=loader/data/lookups .
echo ---------- Restore Packages
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Package --url=$HOST/unload --filename=loader/data/packages .
echo ---------- Restore matches schedules
bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Match --url=$HOST/unload --filename=loader/data/matches .
#echo ---------- Restore workflows
#bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Workflow --url=$HOST/unload --filename=loader/data/workflows .
#echo ---------- Restore states
#bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=State --url=$HOST/unload --filename=loader/data/states .
#echo ---------- Restore transitions
#bulkloader.py --restore --app_id=$APP_ID --email=$EMAIL --kind=Transition --url=$HOST/unload --filename=loader/data/transitions .
rm -rf bulkloader-*
