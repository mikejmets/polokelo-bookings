def str2datetime(x):
  if x != 'None':
      x = x.split(".")[0]
      x = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
  return x

def str2datetimedate(x):
  if x != 'None':
      x = str2datetime(x).date()
  return x


