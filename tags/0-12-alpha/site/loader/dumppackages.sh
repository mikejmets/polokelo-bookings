#!/bin/bash
HOST=$1
EMAIL=$2
rm -rf loader/data/packages
bulkloader.py --dump --num_threads=1 --app_id=bookings-dev --email=$EMAIL --kind=Package --url=$HOST/unload --filename=loader/data/packages .
rm -rf bulkloader-*
