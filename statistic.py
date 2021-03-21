import firmware
import json
import redisdb
from common import *
from rejson import Client, Path
rj = Client(host='localhost', port=6379, decode_responses=True)

print("Current timestamp", get_current_timestamp())
cycles = redisdb.get_all_paths()
for c in cycles:
  print(c)
  if (c['rate'] > 0.0001):
    print(c)
