import urllib2
from xml.etree.ElementTree import XML, SubElement, tostring

url = 'http://localhost:8080/externalbookings'


xml = """
<enquirylist>
    <enquirybatchnumber>YCT-4W7-9Z5</enquirybatchnumber>
    <guestagentcode>Trafalgar-234234324</guestagentcode>
    <action>confirm enquiries</action>
    <creditcardholder>
        <name>John</name>
        <surname>O'Groats</surname>
        <passportnumber>777777777777</passportnumber>
        <email>jurgen@upfrontsystems.co.za</email>
        <telephone>+4493213123123</telephone>
        <address>
            <streetpobox>34 Shady Lane</streetpobox>
            <suburb>Shady Pines</suburb>
            <city>Shadowville</city>
            <country>UK</country>
            <postcode>E1 W3</postcode>
        </address>
        <languages>
            <language>English</language>
        </languages>
    </creditcardholder>
    <enquiries>
        <enquiry>
            <enquirynumber>YE8-DQN-2P1</enquirynumber>
            <city>PCS</city>
            <accommodation>
                <type>HOM</type>
                <rooms>
                    <single>0</single>
                    <twin>0</twin>
                    <double>1</double>
                    <family>0</family>
                </rooms>
            </accommodation>
            <startdate>2010-06-03</startdate>
            <duration>5</duration>
            <adults>2</adults>
            <children>1</children>
            <disability>
                <wheelchairaccess>no</wheelchairaccess>
                <otherspecialneeds>no</otherspecialneeds>
            </disability>
            <quote>18300.00</quote>
            <vat>2562.00</vat>
        </enquiry>
    </enquiries>
</enquirylist>
"""

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
