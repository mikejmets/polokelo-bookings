#!/bin/bash
SRC=$1
DIR=$2
appcfg.py upload_data --kind=Owner --filename=$SRC/owners.csv --config_file=loader/owner_loader.py --email=mikejmets@gmail.com -v --url=http://localhost:8080/unload $DIR
#appcfg.py upload_data --kind=Venue --filename=$SRC/venues.csv --config_file=loader/venue_loader.py --email=mikejmets@gmail.com -v --url=http://localhost:8080/unload $DIR

