import urllib, urllib2
from xml.etree.ElementTree import XML, SubElement, tostring

url = 'http://localhost:8080/paymentnotify'

pay_req = {}
pay_req["timestamp"] = '2009-12-03 10:00'
pay_req["p1"] = '1364'
pay_req["p2"] = 'YCHT-4W7-9ZD'
pay_req["p3"] = '123456APPROVED'
pay_req["p4"] = ""
pay_req["p5"] = "J O'GROATS"
pay_req["p6"] = "-0.10" 
pay_req["p7"] = "VISA"
pay_req["p8"] = "Polokelo Sport Tours Accommodation: YHT-4W7-9ZJ Refund"
pay_req["p9"] = "jurgen@upfrontsystems.co.za"
pay_req["p10"] = "00"
pay_req["p11"] = "1105"
pay_req["p12"] = "00"
# pay_req["p12"] = "05"
pay_req["pam"] = ""
pay_req["m_1"] = "YCHT-4W7-9ZD"
pay_req["m_2"] = "YEK8-DQN-2PH"
pay_req["m_3"] = "REFUND"
pay_req["m_4"] = ""
pay_req["CardHolderIpAddr"] = "10.0.0.128"
pay_req["MaskedCardNumber"] = "************1234"
pay_req["TransactionType"] = "Authorisation"

payment = urllib.urlencode(pay_req)

req = urllib2.Request(url, payment)
response = urllib2.urlopen(req)
result = response.read()
print result
