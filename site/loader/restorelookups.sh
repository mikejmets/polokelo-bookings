#!/bin/bash
HOST=$1
bulkloader.py --restore --app_id=bookings-dev --email=jurgen.blignaut@gmail.com --kind=CodeLookup --url=$HOST/unload --filename=loader/data/lookups .
rm -rf bulkloader-*
