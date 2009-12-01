import urllib, urllib2
from xml.etree.ElementTree import XML, SubElement, tostring

url = 'http://localhost:8080/paymentnotify'

pay_req = {}
pay_req["timestamp"] = '2009-11-30 10:00'
pay_req["p1"] = '1364'
pay_req["p2"] = 'YHT-4W7-9ZJ'
pay_req["p3"] = '123456APPROVED'
# pay_req["p3"] = 'Insufficient funds'
pay_req["p4"] = ""
# pay_req["p4"] = "DUPLICATE"
pay_req["p5"] = "J O'GROATS"
pay_req["p6"] = "49699.44" 
pay_req["p7"] = "VISA"
# pay_req["p7"] = "MASTERCARD"
pay_req["p8"] = "Accommodation for 4 people, 4 nights, from 2010/06/30"
pay_req["p9"] = "john@ogroats.co.uk"
pay_req["p10"] = "00"
pay_req["p11"] = "1105"
pay_req["p12"] = "00"
# pay_req["p12"] = "05"
pay_req["pam"] = ""
pay_req["m_1"] = "YHT-4W7-9ZJ"
pay_req["m_2"] = "YK8DQN2P0,YK8DQN2P8"
pay_req["m_3"] = "INV"
pay_req["m_4"] = "100"
pay_req["CardHolderIpAddr"] = "10.0.0.128"
pay_req["MaskedCardNumber"] = "************1234"
pay_req["TransactionType"] = "Authorisation"

payment = urllib.urlencode(pay_req)

req = urllib2.Request(url, payment)
response = urllib2.urlopen(req)
result = response.read()
print result
