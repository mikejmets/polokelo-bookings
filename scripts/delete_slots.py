import urllib
import urllib2


def main(): 
  key = None
  url = 'http://www.polokelo-bookings.co.za/tasks/deleteberthslots'
  url = 'http://localhost:8080/tasks/deleteberthslots'
  cnt = 0
  action='delete'
  limit = 2 #Set limit here
  limit = max(2, limit) # No less than 2 else it doesn't work
  while True:
      next_url = url
      context = {'action':action, 'limit':limit}
      if key:
          context['last_key'] = key
      try:
          data = urllib.urlencode(context)
          next_url = url + '?' + data
          response = urllib2.urlopen(next_url)
          results = eval(response.read())
          action = results['action']
          key = results['last_key']
          report = results['report']
          if action == 'Ooops':
              print 'Ooops'
              break
          if action == 'stop':
              break
          cnt += 1
          if len(report) > 0:
              print '---- Report:\n%s' % (report)
          print '-- %s: %s' % (cnt, key)
      except Exception, e:
          print 'Exceptiotn %s' % e
          print 'Reset last -------- %s: %s' % (cnt, key)
      
  print 'Done'

if __name__ == "__main__":
    main()
