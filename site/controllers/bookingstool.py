import logging
from datetime import datetime, timedelta
from google.appengine.ext.db import Query
from models.hostinfo import Slot

logger = logging.getLogger('BookingsTool')

class BookingsTool():

  def checkAvailability(self, city, type, start, nights, people):
      return len(findBerths(city, type, start, nights, people)) > 0

  def findBerths(self, city, type, start, nights, people):
        logger.info('Search for %s, %s, %s(%s), %s', \
            city, type, start, nights, people)
        berths = self.findValidBerths(city, type, start, nights)

        #for key, slots in berths:
        #  logger.info("valid pairing %s: %s", key, slots)
        if len(berths) >= people:
            logger.info("Found %s pairings for %s people", 
                len(berths), people)
            return berths
        else:
            logger.info("Sorry, only found %s pairings for %s people", 
                len(berths), people)
            return []

  def findValidBerths(self, city, type, start, nights):
        end = start + timedelta(days = (nights-1))
        #logger.info('Search for %s, %s, %s -> %s(%s)', \
        #    city, type, start, end, nights)

        query = Slot.all()
        query.filter('occupied =', False)
        query.filter('city =', city)
        query.filter('type =', type)
        query.filter('startDate >=', start)
        query.filter('startDate <=', end)
        query.order('startDate')

        slots = query.fetch(1000)
        logger.info("Found %s results", len(slots))
        #group by berth
        berths = {}
        for slot in slots:
            #logger.info("Found berth %s", slot.berth.key())
            berthkey = slot.berth.key()
            if berths.has_key(berthkey):
                berths[berthkey]['slots'].append(slot)
            else:
                berths[berthkey] = {'slots': [slot], 'valid':False}
        #check for complete and continuous pairings
        for key in berths.keys():
            #logger.info("Check pair %s", key)
            valid = True #until proven otherwise
            #Check completeness
            if len(berths[key]['slots']) != nights:
                logger.info("INVALID: Pairing for %s is incomplete", key)
                break #it remains false
            #Check continuous - not required
            #current = None
            #for slot in berths[key]['slots']:
            #    #logger.info("Check %s against %s", slot.startDate, current)
            #    if current is None:
            #        current = slot.startDate
            #    else:
            #        if slot.startDate != current + timedelta(days = 1):
            #            valid = False
            #            break
            #        else:
            #            current = slot.startDate
            if valid:
                berths[key]['valid'] = True
                
        valid_berths = []
        for key in berths.keys():
            #logger.info("Valid pairing %s", berths[key]['valid'])
            if berths[key]['valid']:
                valid_berths.append((key, berths[key]['slots']))

        #for key, slots in valid_berths:
        #  logger.info("valid pairing %s: %s", key, slots)

        return valid_berths



