from google.appengine.ext import db

class Package(db.Model):
    """ define the unit price per night for a 
        city and accommodation type
    """
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    city = db.StringProperty(verbose_name='City', required=True)
    accommodationType = db.StringProperty(
        verbose_name='Accommodation Type', required=True)
    basePriceInZAR = db.IntegerProperty(verbose_name='Base Price in ZAR (no cents)')


    def calculateQuote(self, accommodationElement):
        """ calculate a quote for an accommodation element and return in ZAR cents
        """
        resultInCents = 0L

        # check for scpecial needs and move on
        if accommodationElement.specialNeeds == True:
            return resultInCents

        # calculate the quote for the accommodation element parameters
        people = accommodationElement.adults + accommodationElement.children
        nights = accommodationElement.nights
        price = self.basePriceInZAR * 100     # convert to cents
        resultInCents += people * nights * price

        # subract discounts
        resultInCents -= self.calculateDiscounts(price, accommodationElement)

        # add penalties
        resultInCents += self.calculateExtras(price, accommodationElement)

        # return the final result IN CENTS
        return resultInCents

    def calculateDiscounts(self, price, accommodation):
        """ apply any discount rules and return the discount value in cents
        """
        # at this stage, no discount rules are in place
        return 0L

    def calculateExtras(self, price, accommodation):
        """ apply any extras or fee rules and return the penalty amount in cents
        """
        # at this stage, no penalty rules are in place
        return 0L
