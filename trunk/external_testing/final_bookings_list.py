import urllib2
from xml.etree.ElementTree import XML, SubElement, tostring

url = 'http://localhost:8080/externalbookings'
#url = 'http://0-9-alpha.latest.bookings-dev.appspot.com/externalbookings'


xml = """
<enquirylist>
    <enquirybatchnumber>YHT-4W7-9ZK</enquirybatchnumber>
    <guestagentcode>Trafalgar-234234324</guestagentcode>
    <action>confirm enquiries</action>
    <creditcardholder>
        <name>Michael</name>
        <surname>Jacksonroats</surname>
        <passportnumber>777777777777</passportnumber>
        <email>michael@neverland.com</email>
        <telephone>+4493213123123</telephone>
        <address>
            <streetpobox>34 Shady Lane</streetpobox>
            <suburb>Shady Pines</suburb>
            <city>Shadowville</city>
            <country>USAK</country>
            <postcode>435345</postcode>
        </address>
        <languages>
            <language>English</language>
        </languages>
    </creditcardholder>
    <enquiries>
        <enquiry>
            <enquirynumber>YK8-DQN-2PM</enquirynumber>
            <city>PCS</city>
            <accommodation>
                <type>HOM</type>
                <rooms>
                    <single>2</single>
                    <twin>0</twin>
                    <double>1</double>
                    <family>0</family>
                </rooms>
            </accommodation>
            <startdate>2010-06-17</startdate>
            <duration>4</duration>
            <adults>2</adults>
            <children>2</children>
            <disability>
                <wheelchairaccess>no</wheelchairaccess>
                <otherspecialneeds>no</otherspecialneeds>
            </disability>
            <quote>0.0</quote>
            <vat>0.0</vat>
        </enquiry>
    </enquiries>
</enquirylist>
"""

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
