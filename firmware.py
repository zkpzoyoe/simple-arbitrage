import json
import requests
import decimal
import time
import random
from common import *
import networkx as nx
import Pair
import Cycle
import erc20address
import redisdb

class CalFault(Exception):
  pass

class Analysis:
  def __init__(self, pairs):
    self.tg = nx.Graph()
    self.cycles = [] # all cycles
    self.pairs = {}
    self.tokens = {}
    for p in pairs:
      src = p['token0']['address']
      dest = p['token1']['address']
      self.tg.add_edge(src, dest, pair = p)
    tc = nx.algorithms.cycles.cycle_basis(self.tg)
    for c in tc:
      if len(c) > 1: # only interested in cycles with more than 3 node
        redisdb.add_path_info(c)

  def scan_cycles(self):
    for c in redisdb.get_all_paths():
      try:
        base = 1000000000000000000
        p = c['path']
        r = Cycle.get_output(self.tg, p, "WETH_c02a")
        if r['rate'] > 0.9:
          print(r,"\n")
        else:
          print(r['rate'])
          pass
        redisdb.update_path_rate(c['path'], float(r['rate']))
      except Cycle.NotFound as e:
        print("NotFound")
        pass
      except CalFault as e:
        raise e
