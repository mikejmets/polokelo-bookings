#!/bin/bash
APP_DIR=$1
DATA_DIR=$2
HOST=$3
bulkloader.py --restore --app_id=bookings-dev --email=jurgen.blignaut@gmail.com --kind=CodeLookup --url=$HOST/unload --filename=$DATA_DIR/lookups $APP_DIR
rm -rf bulkloader-*
