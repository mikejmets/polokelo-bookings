xml = """
<invoice>
    <action>retrieve invoice</action>
    <enquirybatchnumber>YCT-4W7-9ZF</enquirybatchnumber>
</invoice>
"""

url = 'http://localhost:8080/externalbookings'

import urllib2

req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
