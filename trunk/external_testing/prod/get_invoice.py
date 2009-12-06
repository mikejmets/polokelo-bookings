xml = """
<invoice>
    <action>retrieve invoice</action>
    <enquirybatchnumber>PAC-DTL-HKF</enquirybatchnumber>
</invoice>
"""

url = 'http://bookings-dev.appspot.com/externalbookings'

import urllib2

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
