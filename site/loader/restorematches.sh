#!/bin/bash
HOST=$1
EMAIL=$2
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Match --url=$HOST/unload --filename=loader/data/matches .
rm -rf bulkloader-*
