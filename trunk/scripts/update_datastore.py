import urllib
import urllib2


def main():
  data = urllib.urlencode({'last_key':'None'})
  url = 'http://www.polokelo-bookings.co.za/tasks/update_datastore'
  #url = 'http://localhost:8080/tasks/update_datastore'
  cnt = 0
  while True:
      next_url = url + '?' + data
      response = urllib2.urlopen(next_url)
      results = response.read()
      #print '--------%s' % results
      results = eval(results)
      next_url = results['next_url']
      if next_url == '/':
          break
      #url = next_url.split('?')[0]
      key = next_url.split('=')[1]
      data = urllib.urlencode({'last_key':key})
      
      print '-- %s: %s' % (cnt, key)
      cnt += 1
  print 'Done'

if __name__ == "__main__":
    main()
