import urllib2
from xml.etree.ElementTree import XML, SubElement, tostring

url = 'http://localhost:8080/externalbookings'
#url = 'http://0-9-alpha.latest.bookings-dev.appspot.com/externalbookings'


xml = """
<enquirylist>
    <enquirybatchnumber>YCHT-4W7-9Z6</enquirybatchnumber>
    <guestagentcode>Trafalgar-234234324</guestagentcode>
    <action>confirm enquiries</action>
    <creditcardholder>
        <name>Jurgen</name>
        <surname>Blignaut</surname>
        <passportnumber>6008105006081</passportnumber>
        <email>jurgen@webtide.co.za</email>
        <telephone>+27829227239</telephone>
        <address>
            <streetpobox>64 Union Street</streetpobox>
            <suburb>Lochnerhof</suburb>
            <city>Strand</city>
            <country>South Africa</country>
            <postcode>7140</postcode>
        </address>
        <languages>
            <language>English</language>
            <language>Afrikaans</language>
        </languages>
    </creditcardholder>
    <enquiries>
        <enquiry>
            <enquirynumber>YEK8-DQN-2P0</enquirynumber>
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
            <startdate>2010-07-10</startdate>
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
    </enquiries>
</enquirylist>
"""

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
