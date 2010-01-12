import urllib2

url = 'http://localhost:8080/externalbookings'
# url = 'http://0-9-alpha.latest.bookings-dev.appspot.com/externalbookings'


xml = """
<testgenerator>
    <action>generate enquiry number</action>
</testgenerator>
"""
req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()


xml = """
<testgenerator>
    <action>generate collection number</action>
</testgenerator>
"""
req = urllib2.Request(url, xml, headers={'Content-Type':'text/plain'})
response = urllib2.urlopen(req)
print response.read()
