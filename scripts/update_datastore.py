import urllib
import urllib2


def main(): 
  key = '2009-12-10 03:34:34.597862'
  url = 'http://www.polokelo-bookings.co.za/tasks/update_datastore'
  #url = 'http://localhost:8080/tasks/update_datastore'
  cnt = 0
  while True:
      data = urllib.urlencode({'last_key':key})
      next_url = url + '?' + data
      try:
          response = urllib2.urlopen(next_url)
          results = response.read()
          #print '--------%s' % results
          results = eval(results)
          next_url = results['next_url']
          if next_url == '/':
              break
          key = next_url.split('=')[1]
      except:
          print 'Reset key -------- %s: %s' % (cnt, key)
      
      print '-- %s: %s' % (cnt, key)
      cnt += 1
  print 'Done'

if __name__ == "__main__":
    main()
