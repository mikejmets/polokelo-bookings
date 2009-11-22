xml = """
<enquiry>
    <email>john@ogroats.co.uk</email>
    <guestagentcode>Trafalgar-234234234</guestagentcode>
    <action>check availability</action>
    <enquirynumber>PBC-ABC-ABC</enquirynumber>
    <city>PCS</city>
    <accommodationtype>ACFAM</accommodationtype>
    <startdate>2010-06-17</startdate>
    <duration>4</duration>
    <guestgendersensitive>no</guestgendersensitive>
    <adults>
        <male>2</male>
        <female>0</female>
    </adults>
    <children>
        <male>0</male>
        <female>0</female>
    </children>
    <disability>
        <wheelchairaccess>no</wheelchairaccess>
        <otherspecialneeds>no</otherspecialneeds>
    </disability>
</enquiry>
"""

url = 'http://localhost:8080/externalbookings'
#url = 'http://0-9-alpha.latest.bookings-dev.appspot.com/externalbookings'

import urllib2

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
