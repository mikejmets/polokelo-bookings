import urllib2
from xml.etree.ElementTree import XML, SubElement, tostring

url = 'http://bookings-dev.appspot.com/externalbookings'

# post the check availability request
xml = """
<enquiry>
    <enquirybatchnumber>PAC-DTV-YRA</enquirybatchnumber>
    <email>jan@eduplay.co.za</email>
    <guestagentcode>GA000</guestagentcode>
    <action>check availability</action>
    <enquirynumber>PAC-DTW-XGU</enquirynumber>
    <city>PCS</city>
    <accommodation>
        <type>HOM</type>
        <rooms>
            <single>2</single>
            <twin>0</twin>
            <double>0</double>
            <family>0</family>
        </rooms>
    </accommodation>
    <startdate>2010-6-10</startdate>
    <duration>5</duration>
    <adults>1</adults>
    <children>1</children>
    <disability>
        <wheelchairaccess>no</wheelchairaccess>
        <otherspecialneeds>no</otherspecialneeds>
    </disability>
</enquiry>
"""

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
