xml = """
<testgenerator>
    <action>generate enquiry number</action>
</testgenerator>
"""

url = 'http://localhost:8080/externalbookings'
# url = 'http://0-9-alpha.latest.bookings-dev.appspot.com/externalbookings'

import urllib2

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
