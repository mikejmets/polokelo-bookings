from google.appengine.ext import db

from models.codelookup import getChoices


class Package(db.Model):
    """ define the unit price per night for a 
        city and accommodation type
    """
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    city = db.StringProperty(verbose_name='City', required=True,
                                choices = getChoices('CTY'))
    accommodationType = db.StringProperty(verbose_name='Accommodation Type',
                                required=True,
                                choices=getChoices('ACTYP'))
    basePriceInZAR = db.IntegerProperty(verbose_name='Base Price in ZAR (no cents)')


    def calculateQuote(self, accommodationElement):
        """ calculate a quote for an accommodation element and return in ZAR
        """
        result = 0.0

        # check for scpecial needs and move on
        if accommodationElement.specialNeeds == True:
            return result

        # calculate the quote for the accommodation element parameters
        people = accommodationElement.adults + accommodationElement.children
        nights = accommodationElement.nights
        price = self.basePriceInZAR
        result += people * nights * price

        # subract discounts
        result -= self.calculateDiscounts(price, accommodationElement)

        # add penalties
        result += self.calculatePenalties(price, accommodationElement)

        # return the final result in ZAR
        return result

    def calculateDiscounts(self, price, accommodation):
        """ apply any discount rules and return the discount value
        """
        # at this stage, no discount rules are in place
        return 0.0

    def calculatePenalties(self, price, accommodation):
        """ apply any penalty rules and return the penalty amount
        """
        # at this stage, no penalty rules are in place
        return 0.0
