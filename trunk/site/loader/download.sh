#!/bin/bash
DEST=$1
SRC=$2
rm -rf $DEST
mkdir $DEST
appcfg.py download_data --kind=Owner --filename=$DEST/owners.csv --config_file=owner_loader.py --email=mikejmets@gmail.com -v --url=http://localhost:8080/unload $SRC
#appcfg.py download_data --kind=Venue --filename=$DEST/venues.csv --config_file=venue_loader.py --email=mikejmets@gmail.com -v --url=http://localhost:8080/unload $SRC
rm -rf bulkloader-*
