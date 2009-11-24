import urllib2
from xml.etree.ElementTree import XML, SubElement, tostring

url = 'http://localhost:8080/externalbookings'
#url = 'http://0-9-alpha.latest.bookings-dev.appspot.com/externalbookings'


xml = """
<enquirylist>
    <enquirynumber>YK8-DQN-XX4</enquirynumber>
    <guestagentcode>Trafalgar-234234324</guestagentcode>
    <action>confirm enquiries</action>
    <creditcardholder>
        <name>John</name>
        <surname>O'Groats</surname>
        <passportnumber>3453534533476657</passportnumber>
        <email>john@scotland.com</email>
        <telephone>+4493213123123</telephone>
        <address>
            <streetpobox>34 Shady Lane</streetpobox>
            <suburb>Northside</suburb>
            <city>Glasgow</city>
            <country>UK</country>
            <postcode>E34 N1</postcode>
        </address>
        <languages>
            <language>English</language>
            <language>French</language>
        </languages>
    </creditcardholder>
    <enquiries>
        <enquiry>
            <number>YK8-DQN-2PH</number>
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
            <quote>134.56</quote>
        </enquiry>
    </enquiries>
</enquirylist>
"""

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
