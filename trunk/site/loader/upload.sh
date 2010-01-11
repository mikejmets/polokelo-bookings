#!/bin/bash
SRC=$1
DEST=$2
DIR=$3
EMAIL=$4
appcfg.py upload_data --kind=Owner --filename=$SRC/owners.csv --config_file=loader/owner_loader.py --email=$EMAIL -v --url=$DEST/unload $DIR
#appcfg.py upload_data --kind=Venue --filename=$SRC/venues.csv --config_file=loader/venue_loader.py --email=$EMAIL -v --url=$DEST/unload $DIR

