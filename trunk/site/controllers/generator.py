import logging
from google.appengine.ext.db import run_in_transaction
from models.bookinginfo import IdSequence
from google.appengine.api import users

class IdGenerator(object):
    """ Class to Generate a new ID """

    def __init__(self, seed, digits):
        """initialse the seed for 
        encoding the number"""
        self.seed = seed
        # set up the digit representation fo the number system
        self.digits = digits
        # set the correct base for the number system
        self.base = len(self.digits)

    def dec2Encoded(self, tbc):
        """
        the function works by converting the sequence
        to a base 48 number represented by the digit set above.
        It is then encoded by add the corresponding digit from 
        the seed to the converted base 48 number.
        """
        result = ''

        # compute the max power using the length of the seed
        power = len(self.seed)
        # start on the leftmost digit of the seed
        seedidx = 0
        
        # count down the powers of the base 
        while power > 0:
            # start with the left-most digit in the digit set
            digit = 0
            # calculate the base to the power to convert the w
            number = self.base**(power-1)

            # determine how many times the base 48 power 
            # goes into the number to get a digit representation 
            while tbc >= number:
                digit += 1
                tbc -= number

            # get the current seed digit for encoding the 
            seedchar = self.seed[seedidx]
            # find the seed digit in the digit set
            pos = self.digits.find(seedchar)
            # add it to the conversion digit we calculated
            # and mod it with the base to roll it over
            index = (pos+digit) % self.base
            # add the encoded digit to the result
            result += self.digits[index]

            # set up the next loop
            power -= 1
            seedidx += 1
            
        # return the encoded number
        return result


def _incrementSequence(key_name):
    sequencer = IdSequence.get_by_key_name(key_name)
    if sequencer is None:
        sequencer = IdSequence(key_name=key_name)
    current = sequencer.sequence
    sequencer.sequence += 1
    sequencer.creator = users.get_current_user()
    sequencer.put()
    return current


def _generateNumber(seed, number_type):
    """ generate a new number of the required type
    """
    # get hold of the generator and the last sequence number
    generator = IdGenerator(seed, '3QW7B4CD5FG1HJ6KL8MN0PR2STVX9Z')

    # get the current sequence to use
    current = run_in_transaction(_incrementSequence, number_type)

    # generate the new id and up the sequence by 1            
    result = generator.dec2Encoded(current)
    logging.info ("Generated %s '%s' for sequence '%s'", \
                                                number_type, result, current)

    #return the result
    return result


def generateEnquiryCollectionNumber():
    """ generate a new enquiry number
    """
    number = _generateNumber('HT4W79ZD', 'enquirycollectionnumber')
    return 'Y' + number[:2] + '-' + number[2:5] + '-' + number[5:]


def generateEnquiryNumber():
    """ generate a new enquiry number
    """
    number = _generateNumber('K8DQN2PG', 'enquirynumber')
    return 'Y' + number[:2] + '-' + number[2:5] + '-' + number[5:]


def generateBookingNumber():
    """ generate a new booking number
    """
    number = _generateNumber('S5HKZ3CE', 'bookingnumber')
    return 'Y' + number[:2] + '-' + number[2:5] + '-' + number[5:]


def generateClientNumber():
    """ generate a new client number
    """
    number = _generateNumber('A9TLW6FV', 'clientnumber')
    return 'Y' + number
