import urllib
import urllib2


def main(): 
  last = None
  url = 'http://www.polokelo-bookings.co.za/tasks/venuevalidation'
  #url = 'http://localhost:8080/tasks/venuevalidation'
  cnt = 0
  while True:
      next_url = url
      if last:
          data = urllib.urlencode({'last':last})
          next_url = url + '?' + data
      try:
          response = urllib2.urlopen(next_url)
          results = eval(response.read())
          last = results['last']
          report = results['report']
          if last == '0':
              break
          cnt += 1
          print '%s' % (report)
      except Exception, e:
          print 'Exceptiotn %s' % e
          print 'Reset last -------- %s: %s' % (cnt, last)
      
  print 'Done'

if __name__ == "__main__":
    main()
