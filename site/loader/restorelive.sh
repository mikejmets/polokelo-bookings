#!/bin/bash
EMAIL=$1
HOST=http://www.polokelo-bookings.co.za

loader/restoreadmin.sh $HOST $EMAIL
loader/restorehosts.sh $HOST $EMAIL

