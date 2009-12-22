#!/bin/bash
EMAIL=$1
HOST=http://backup-pb.appspot.com
APP_ID=backup-pb

loader/restoreadmin.sh $HOST $EMAIL $APP_ID
loader/restorehosts.sh $HOST $EMAIL $APP_ID

