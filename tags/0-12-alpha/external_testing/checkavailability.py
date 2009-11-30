import urllib2
from xml.etree.ElementTree import XML, SubElement, tostring

url = 'http://localhost:8080/externalbookings'
#url = 'http://0-9-alpha.latest.bookings-dev.appspot.com/externalbookings'


# get a new enquiry number
xml = """
<testgenerator>
    <action>generate enquiry number</action>
</testgenerator>
"""

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
result = response.read()

xmlroot = XML(result)
enquiry_number = xmlroot.findtext('enquirynumber')


# post the check availability request
xml = """
<enquiry>
    <email>john@ogroats.co.uk</email>
    <guestagentcode>Trafalgar-234234234</guestagentcode>
    <action>check availability</action>
    <enquirynumber>%s</enquirynumber>
    <city>PCS</city>
    <accommodation>
        <type>HOM</type>
        <rooms>
            <single>0</single>
            <twin>0</twin>
            <double>0</double>
            <family>1</family>
        </rooms>
    </accommodation>
    <startdate>2010-06-17</startdate>
    <duration>4</duration>
    <adults>2</adults>
    <children>3</children>
    <disability>
        <wheelchairaccess>no</wheelchairaccess>
        <otherspecialneeds>no</otherspecialneeds>
    </disability>
</enquiry>
""" % enquiry_number


req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
