import urllib2
from xml.etree.ElementTree import XML, SubElement, tostring

url = 'http://localhost:8080/externalbookings'


xml = """
<enquirylist>
    <enquirybatchnumber>YCT-4W7-9ZF</enquirybatchnumber>
    <guestagentcode>Trafalgar-234234324</guestagentcode>
    <action>confirm enquiries</action>
    <creditcardholder>
        <name>John</name>
        <surname>O'Groats</surname>
        <passportnumber>777777777777</passportnumber>
        <email>john@ogroats.co.uk</email>
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
            <enquirynumber>YE8-DQN-2PG</enquirynumber>
            <city>CPT</city>
            <accommodation>
                <type>GH</type>
                <rooms>
                    <single>2</single>
                    <twin>0</twin>
                    <double>1</double>
                    <family>0</family>
                </rooms>
            </accommodation>
            <startdate>2010-06-10</startdate>
            <duration>3</duration>
            <adults>2</adults>
            <children>2</children>
            <disability>
                <wheelchairaccess>no</wheelchairaccess>
                <otherspecialneeds>no</otherspecialneeds>
            </disability>
            <quote>34600.00</quote>
            <vat>4844.00</vat>
        </enquiry>
        <enquiry>
            <enquirynumber>YE8-DQN-2P1</enquirynumber>
            <city>DUR</city>
            <accommodation>
                <type>GH</type>
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
            <quote>0.00</quote>
            <vat>0.00</vat>
        </enquiry>
        <enquiry>
            <enquirynumber>YE8-DQN-2PH</enquirynumber>
            <city>CPT</city>
            <accommodation>
                <type>GH</type>
                <rooms>
                    <single>2</single>
                    <twin>0</twin>
                    <double>1</double>
                    <family>0</family>
                </rooms>
            </accommodation>
            <startdate>2010-06-25</startdate>
            <duration>4</duration>
            <adults>2</adults>
            <children>2</children>
            <disability>
                <wheelchairaccess>no</wheelchairaccess>
                <otherspecialneeds>no</otherspecialneeds>
            </disability>
            <quote>20760.00</quote>
            <vat>2906.40</vat>
        </enquiry>
    </enquiries>
</enquirylist>
"""

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
