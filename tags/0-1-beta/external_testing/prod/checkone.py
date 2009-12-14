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
<email>jurgen.blignaut@gmail.com</email>
<guestagentcode>GA000</guestagentcode>
<action>check availability</action>
<enquirynumber>%s</enquirynumber>
<city>PCS</city>
<accommodation>
<type>HOM</type>
<rooms><single>1</single>
<twin>0</twin>
<double>0</double>
<family>0</family>
</rooms>
</accommodation>
<startdate>2010-6-18</startdate>
<duration>3</duration>
<adults>1</adults>
<children>0</children>
<disability>
<wheelchairaccess>no</wheelchairaccess>
<otherspecialneeds>no</otherspecialneeds>
</disability>
</enquiry>
""" % (collection_number, enquiry_number)

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
