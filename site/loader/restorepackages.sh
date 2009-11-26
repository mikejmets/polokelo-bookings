#!/bin/bash
HOST=$1
EMAIL=$2
bulkloader.py --restore --app_id=bookings-dev --email=$EMAIL --kind=Package --url=$HOST/unload --filename=loader/data/packages .
rm -rf bulkloader-*
