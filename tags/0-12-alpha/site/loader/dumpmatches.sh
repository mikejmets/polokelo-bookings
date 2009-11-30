#!/bin/bash
HOST=$1
EMAIL=$2
rm -rf loader/data/matches
bulkloader.py --dump --num_threads=1 --app_id=bookings-dev --email=$EMAIL --kind=Match --url=$HOST/unload --filename=loader/data/matches .
rm -rf bulkloader-*
