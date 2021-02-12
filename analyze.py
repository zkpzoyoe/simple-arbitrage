import firmware
import json
from common import *
from rejson import Client, Path
rj = Client(host='localhost', port=6379, decode_responses=True)

print("Current timestamp", get_current_timestamp())
all_pairs = rj.jsonget("pairs").values()
print(all_pairs)
#all_pairs = json.load(open('files/main_pairs.json'))
analysis = firmware.Analysis(all_pairs)
analysis.scan_cycles()
