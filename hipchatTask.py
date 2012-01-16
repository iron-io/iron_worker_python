# Uncomment the following to get list of python modules on IronWorker
#help('modules')
import json
import urllib2
import hashlib
import cloudcache 
import ConfigParser
import os
import sys

print "args:  " + str(sys.argv)
try:
  dr = sys.argv[2]
  print "directory:  " + dr
except:
  dr = './'
config = ConfigParser.RawConfigParser()
pth = os.path.abspath(dr + 'config.ini')
#path = "config.ini"
fp = open(pth, 'r')
print "path = " + pth
#config.read('./config.ini')
#config.read(pth)
config.readfp(fp)

print "Config sections:  " + str(config.sections())
token = config.get("HipChat", "token")

url = "https://api.hipchat.com/v1/rooms/list?auth_token="+token
request = urllib2.Request(url)
response = urllib2.urlopen(request)

rooms = json.loads(response.read())
rooms = rooms['rooms']
#print str(rooms)

cc = cloudcache.CloudCache("174.129.12.177", "4567", "na", "ironChat001", "na")

kz = []
tmsgs = {}
for room in rooms:
  #print json.dumps(room, sort_keys=True, indent = 4)
  id = str(room['room_id'])
  url = "https://api.hipchat.com/v1/rooms/history?room_id=" + id + "&date=recent&format=json&auth_token="+token 
  #print "url = " + url
  request = urllib2.Request(url)
  response = urllib2.urlopen(request)
  #print "messages:  " 
  msgs = json.loads(response.read())
  msgs = msgs['messages']
  for msg in msgs:
    chksm = hashlib.md5(str(msg)).hexdigest()
    tmsgs[chksm] = msg
    kz.append(chksm)
    #print "chksum = " + str(chksm)
    #print json.dumps(msg, sort_keys=True, indent = 4)

kvz = json.loads(cc.getmulti(kz))

nNew = 0
for k in kvz.keys():
  #print k, kvz[k]
  if kvz[k] == None:
    nNew = nNew + 1
    # We have not seen this one:
    msg = tmsgs[k]
    cc.set(k,"1", 48*3600)
    print "New message:  " 
    print json.dumps(msg, sort_keys = True, indent = 4)
   
if nNew == 0:
  print "No new messages." 
