#!/bin/bash
EMAIL=$1
HOST=http://localhost:8080

loader/restoreadmin.sh $HOST $EMAIL
loader/restorehosts.sh $HOST $EMAIL

