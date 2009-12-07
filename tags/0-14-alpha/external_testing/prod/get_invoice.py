xml = """
<invoice>
    <action>retrieve invoice</action>
    <enquirybatchnumber>YCHT-4W7-9Z2</enquirybatchnumber>
</invoice>
"""

url = 'http://0-14-alpha.latest.bookings-dev.appspot.com/externalbookings'

import urllib2

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
