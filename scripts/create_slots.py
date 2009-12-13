import urllib
import urllib2


def main(): 
  key = None
  url = 'http://www.polokelo-bookings.co.za/tasks/createberthslots'
  url = 'http://localhost:8080/tasks/createberthslots'
  cnt = 0
  while True:
      next_url = url
      if key:
          data = urllib.urlencode({'last_key':key})
          next_url = url + '?' + data
      try:
          response = urllib2.urlopen(next_url)
          results = eval(response.read())
          next_url = results['next_url']
          report = results['report']
          if next_url == '/':
              break
          key = next_url.split('=')[1]
          cnt += 1
          if len(report) > 0:
              print '---- Report:\n%s' % (report)
          print '-- %s: %s' % (cnt, key)
      except:
          print 'Reset key -------- %s: %s' % (cnt, key)
      
  print 'Done'

if __name__ == "__main__":
    main()
