import firmware
import json
from common import *
import redisdb
import UniswapPair

print("Current timestamp", get_current_timestamp())

redisdb.init_info_db()

UniswapPair.fetch_all_pairs()

#all_pairs = json.load(open('files/pairs.json'))
#all_pairs = json.load(open('files/main_pairs.json'))
#analysis = firmware.Analysis(all_pairs)
#analysis.scan_cycles()
