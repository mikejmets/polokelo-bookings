import urllib2
from xml.etree.ElementTree import XML, SubElement, tostring

url = 'http://www.polokelo-bookings.co.za/externalbookings'


# get a new collection number
xml = """
<testgenerator>
    <action>generate collection number</action>
</testgenerator>
"""

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
xmlroot = XML(response.read())
collection_number = xmlroot.findtext('collectionnumber')


# get a new enquiry number
xml = """
<testgenerator>
    <action>generate enquiry number</action>
</testgenerator>
"""

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
xmlroot = XML(response.read())
enquiry_number = xmlroot.findtext('enquirynumber')


# post the check availability request
xml = """
<enquiry>
    <enquirybatchnumber>%s</enquirybatchnumber>
    <email>john@ogroats.co.uk</email>
    <guestagentcode>Trafalgar-234234234</guestagentcode>
    <action>check availability</action>
    <enquirynumber>%s</enquirynumber>
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
    <duration>5</duration>
    <adults>2</adults>
    <children>2</children>
    <disability>
        <wheelchairaccess>no</wheelchairaccess>
        <otherspecialneeds>no</otherspecialneeds>
    </disability>
</enquiry>
""" % (collection_number, enquiry_number)

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()


# get a new enquiry number
xml = """
<testgenerator>
    <action>generate enquiry number</action>
</testgenerator>
"""

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
xmlroot = XML(response.read())
enquiry_number = xmlroot.findtext('enquirynumber')


# post the check availability request
xml = """
<enquiry>
    <enquirybatchnumber>%s</enquirybatchnumber>
    <email>john@ogroats.co.uk</email>
    <guestagentcode>Trafalgar-234234234</guestagentcode>
    <action>check availability</action>
    <enquirynumber>%s</enquirynumber>
    <city>DBN</city>
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
    <duration>5</duration>
    <adults>2</adults>
    <children>2</children>
    <disability>
        <wheelchairaccess>no</wheelchairaccess>
        <otherspecialneeds>no</otherspecialneeds>
    </disability>
</enquiry>
""" % (collection_number, enquiry_number)

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()


# get a new enquiry number
xml = """
<testgenerator>
    <action>generate enquiry number</action>
</testgenerator>
"""

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
xmlroot = XML(response.read())
enquiry_number = xmlroot.findtext('enquirynumber')


# post the check availability request
xml = """
<enquiry>
    <enquirybatchnumber>%s</enquirybatchnumber>
    <email>john@ogroats.co.uk</email>
    <guestagentcode>Trafalgar-234234234</guestagentcode>
    <action>check availability</action>
    <enquirynumber>%s</enquirynumber>
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
    <duration>3</duration>
    <adults>2</adults>
    <children>2</children>
    <disability>
        <wheelchairaccess>no</wheelchairaccess>
        <otherspecialneeds>no</otherspecialneeds>
    </disability>
</enquiry>
""" % (collection_number, enquiry_number)

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
