#!/bin/bash
HOST=$1
EMAIL=$2
echo "-------------- Dump Lookup Tables"
rm -rf loader/data/lookups
bulkloader.py --dump --num_threads=1 --app_id=bookings-dev --email=$EMAIL --kind=CodeLookup --url=$HOST/unload --filename=loader/data/lookups .
echo "-------------- Dump Packages"
rm -rf loader/data/packages
bulkloader.py --dump --num_threads=1 --app_id=bookings-dev --email=$EMAIL --kind=Package --url=$HOST/unload --filename=loader/data/packages .
echo "-------------- Dump Match Schedules"
rm -rf loader/data/matches
bulkloader.py --dump --num_threads=1 --app_id=bookings-dev --email=$EMAIL --kind=Match --url=$HOST/unload --filename=loader/data/matches .
#echo "-------------- Dump Workflows"
#rm -rf loader/data/workflows
#bulkloader.py --dump --num_threads=1 --app_id=bookings-dev --email=$EMAIL --kind=Workflow --url=$HOST/unload --filename=loader/data/workflows .
#echo "-------------- Dump States"
#rm -rf loader/data/states
#bulkloader.py --dump --num_threads=1 --app_id=bookings-dev --email=$EMAIL --kind=State --url=$HOST/unload --filename=loader/data/states .
#echo "-------------- Dump Transitions"
#rm -rf loader/data/transitions
#bulkloader.py --dump --num_threads=1 --app_id=bookings-dev --email=$EMAIL --kind=Transition --url=$HOST/unload --filename=loader/data/transitions .
rm -rf bulkloader-*
