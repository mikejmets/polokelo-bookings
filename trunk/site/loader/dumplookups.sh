#!/bin/bash
HOST=$1
EMAIL=$2
rm -rf loader/data/lookups
bulkloader.py --dump --num_threads=1 --app_id=bookings-dev --email=$EMAIL --kind=CodeLookup --url=$HOST/unload --filename=loader/data/lookups .
rm -rf bulkloader-*
