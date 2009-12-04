import sys, os

sys.path.insert(0, os.path.abspath(".."))

from common import *

# Replication URL - change this to URL corresponding your application
#ROCKET_URL = "http://localhost:8080/rocket"
ROCKET_URL = "http://qa-mother-of-invention.appspot.com/rocket"

SERVICES = {    
    "ReplicateIdSequence": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "IdSequence",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateEnquiryCollection": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "EnquiryCollection",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateEnquiry": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Enquiry",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateCollectionTransaction": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "CollectionTransaction",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateAccommodationElement": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "AccommodationElement",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateGuestElement": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "GuestElement",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateContractedBooking": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "ContractedBooking",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateVCSPaymentNotification": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "VCSPaymentNotification",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateClient": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Client",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateFlight": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Flight",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateMatchTicket": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "MatchTicket",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateCodeLookup": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "CodeLookup",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateEnquiryRoot": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateAddress": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Address",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicatePhoneNumber": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "PhoneNumber",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateEmailAddress": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "EmailAddress",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateOwner": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Owner",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateVenue": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Venue",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicatePhotograph": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Photograph",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateInspection": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Inspection",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateComplaint": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Complaint",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "Replicate": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateBedroom": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Bedroom",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateBathroom": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Bathroom",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateBed": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Bed",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateBerth": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Berth",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateSlot": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Slot",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
    "ReplicateMatch": 
        {
            TYPE: REPLICATION_SERVICE,
            KIND: "Match",
            MODE: RECEIVE,
            TIMESTAMP_FIELD: "created",
        },
}

BATCH_SIZE = 150 # number of AppEngine entities to load in a single request, reduce this number if requests are using too much CPU cycles or are timing out

# MYSQL DATABASE CONFIGURATION
DATABASE_HOST = "localhost"
DATABASE_NAME = "approcket"
DATABASE_USER = "approcket"
DATABASE_PASSWORD = "approcket"
DATABASE_PORT = 3306
DATABASE_ENGINE = "InnoDB"

#LOGGING CONFIGURATION
import logging
LOG_LEVEL = logging.INFO

# DAEMON CONFIGURATION 
# This provides configuration for running AppRocket replicator (station.py) in daemon mode 
# (using -d command-line switch).
LOGFILE = '/var/log/approcket.log'
PIDFILE = '/var/run/approcket.pid'
GID = 103
UID = 103

# REQUEST TIMEOUT
import socket
socket.setdefaulttimeout(30)

"""
Documentation

# This is simplest format  where Comment and NotAComment are names of entities in AppEngine application.
#    "": {
#        }
#    "ReplicateNotAComment": {TYPE: REPLICATION_SERVICE, KIND: "NotAComment",},
#    "ReplicateComment": {TYPE: REPLICATION_SERVICE, KIND: "Comment", EMBEDDED_LIST_FIELDS: ["list2"]},


# Optionally you can also provide few configuration parameters for each entity, for example like this:
#    "ReplicateEntityX": {
#        TYPE: REPLICATION_SERVICE, 
#        KIND: "EntityX",
#        MODE: RECEIVE, 
#        TIMESTAMP_FIELD: "t", 
#        TABLE_NAME: "test2", 
#        RECEIVE_FIELDS: ["prop1", "prop2"],
#        IDLE_TIME: 10,
#    },

# Here's a full list of supported configuration parameters:
#    MODE: replication mode, possible values are:
#        RECEIVE_SEND: first replicate from AppEngine to MySql and then from Mysql to AppEngine. If some properties
#                      are replicated both ways and there is a replication conflict (entity has been updated
#                      in both MySql and AppEngine since last replication), AppEngine changes will overwrite
#                      MySql changes.
#        SEND_RECEIVE: first replicate from MySql to AppEngine and then from AppEngine to MySql. If some properties
#                      are replicated both ways and there is a replication conflict, MySql changes will overwrite
#                      AppEngine changes.
#        RECEIVE:      only replicate given entity from AppEngine to MySql, changes in MySql are ignored
#        SEND:         only replicate given entity from MySql to AppEngine, changes in AppEngine are ignored
#
#    TABLE_NAME: name of the table for this entity in MySQL, by default it's the same as AppEngine entity name
# 
#    TIMESTAMP_FIELD: name of the timestamp property for this entity, by default "timestamp". 
#                     Each entity that needs to be replicated must have a timestamp property, 
#                     defined in AppEngine model like this: timestamp = db.DateTimeProperty(auto_now=True). 
#                     In MySql timestamp field is created using data type TIMESTAMP.
# 
#    TABLE_KEY_FIELD: name of MySql table column that stores entity key id or name, by default "k".
#
#    RECEIVE_FIELDS: list of properties that are replicated from AppEngine to MySql. If omitted, all properties are replicated.
#
#    SEND_FIELDS: list of properties that are replicated from MySql to AppEngine. If omitted, all properties are replicated.
#
#    SEND_FIELDS_EXCLUDE: list of properties that are excluded from replication from MySQL to AppEngine
#    
#    EMBEDDED_LIST_FIELDS: list of properties that will be stored in single TEXT column in MySql as |-separated list. By 
#                          default lists are stored in a separate table (with one to many relationship). Values of embedded lists 
#                          will always be stored a string values in AppEngine.
#
#    IDLE_TIME: idle time in seconds between replication cycles (i.e. after no more updates are pending). Only used for for daemon (-d) and loop modes (-s) 
"""
