#!/bin/bash
EMAIL=$1
HOST=http://www.polokelo-bookings.co.za
APP_ID=polokelo-bookings

loader/restoreadmin.sh $HOST $EMAIL $APP_ID
loader/restorehosts.sh $HOST $EMAIL $APP_ID

