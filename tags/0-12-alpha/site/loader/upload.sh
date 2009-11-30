#!/bin/bash
DIR=$1
bulkloader.py --kind=Owner --url=http://bookings-dev.appspot.com/unload --filename=$DIR/owners.csv --config_file=owner_loader.py
bulkloader.py --kind=Venue --url=http://bookings-dev.appspot.com/unload --filename=$DIR/venues.csv --config_file=venue_loader.py
bulkloader.py --kind=PhoneNumber --url=http://bookings-dev.appspot.com/unload --filename=$DIR/phone_numbers.csv --config_file=number_loader.py

