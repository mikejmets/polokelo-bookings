#!/bin/bash
DEST=$1
SRC=$2
DIR=$3
rm -rf $DEST/owners.csv
appcfg.py download_data --kind=Owner --filename=$DEST/owners.csv --config_file=loader/owner_loader.py --email=mikejmets@gmail.com -v --url=$SRC/unload $DIR
rm -rf $DEST/venues.csv
appcfg.py download_data --kind=Venue --filename=$DEST/venues.csv --config_file=loader/venue_loader.py --email=mikejmets@gmail.com -v --url=$SRC/unload $DIR
rm -rf $DEST/addresses.csv
appcfg.py download_data --kind=Address --filename=$DEST/addresses.csv --config_file=loader/address_loader.py --email=mikejmets@gmail.com -v --url=$SRC/unload $DIR
rm -rf $DEST/phonenumbers.csv
appcfg.py download_data --kind=PhoneNumber --filename=$DEST/phonenumbers.csv --config_file=loader/phonenumber_loader.py --email=mikejmets@gmail.com -v --url=$SRC/unload $DIR
rm -rf $DEST/emailaddresses.csv
appcfg.py download_data --kind=EmailAddress --filename=$DEST/emailaddresses.csv --config_file=loader/emailaddress_loader.py --email=mikejmets@gmail.com -v --url=$SRC/unload $DIR
rm -rf $DEST/bedrooms.csv
appcfg.py download_data --kind=Bedroom --filename=$DEST/bedrooms.csv --config_file=loader/bedroom_loader.py --email=mikejmets@gmail.com -v --url=$SRC/unload $DIR
rm -rf $DEST/beds.csv
appcfg.py download_data --kind=Bed --filename=$DEST/beds.csv --config_file=loader/bed_loader.py --email=mikejmets@gmail.com -v --url=$SRC/unload $DIR
rm -rf $DEST/bathrooms.csv
appcfg.py download_data --kind=Bathroom --filename=$DEST/bathrooms.csv --config_file=loader/bathroom_loader.py --email=mikejmets@gmail.com -v --url=$SRC/unload $DIR
rm -rf $DEST/photographs.csv
appcfg.py download_data --kind=Photograph --filename=$DEST/photographs.csv --config_file=loader/photograph_loader.py --email=mikejmets@gmail.com -v --url=$SRC/unload $DIR
rm -rf bulkloader-*
