import urllib, urllib2
from xml.etree.ElementTree import XML, SubElement, tostring

url = 'http://localhost:8080/paymentnotify'

pay_req = {}
pay_req["timestamp"] = '2009-12-03 10:00'
pay_req["p1"] = '1364'
pay_req["p2"] = 'YCT-4W7-9ZF'
pay_req["p3"] = '123456APPROVED'
# pay_req["p3"] = 'Insufficient funds'
pay_req["p4"] = ""
# pay_req["p4"] = "DUPLICATE"
pay_req["p5"] = "J BLIGNAUT"
pay_req["p6"] = "3460" 
pay_req["p7"] = "VISA"
# pay_req["p7"] = "MASTERCARD"
pay_req["p8"] = "Polokelo Sport Tours Accommodation: Deposit REF YHT-4W7-9ZJ  CPT 4 people 5 nights from 2010-06-10  CPT 4 people 3 nights from 2010-06-25"
pay_req["p9"] = "jurgen@upfrontsystems.co.za"
pay_req["p10"] = "00"
pay_req["p11"] = "1105"
pay_req["p12"] = "00"
# pay_req["p12"] = "05"
pay_req["pam"] = ""
pay_req["m_1"] = "YCT-4W7-9ZF"
pay_req["m_2"] = "YE8DQN2PH"
pay_req["m_3"] = "DEP"
pay_req["m_4"] = "10"
pay_req["CardHolderIpAddr"] = "10.0.0.128"
pay_req["MaskedCardNumber"] = "************1234"
pay_req["TransactionType"] = "Authorisation"

payment = urllib.urlencode(pay_req)

req = urllib2.Request(url, payment)
response = urllib2.urlopen(req)
result = response.read()
print result
