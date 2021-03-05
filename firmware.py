import json
import requests
import decimal
import time
import random
from common import *
import networkx as nx
import Pair

class NotFound(Exception):
  pass

class CalFault(Exception):
  pass

def switch_decimal(c):
  if not isinstance(c, Decimal):
    return Decimal(c)
  else:
    return c

def reorder(c, key):
  l = len (c)
  pos = l
  d = []
  for i in range(l):
    if (c[i] == key):
      pos = i
      break
    else:
      pass
  if (pos == l):
    raise NotFound
  for i in range(l):
    d.append(c[(pos+i)%l])
  return d

class Cycle:
  def __init__(self, path, tg):
    self.tg = tg
    self.path = path

  # "WETH_c02a"
  def get_output(self, root, base):
    rate = switch_decimal(base)
    info = []
    wei = self.tg.lookup_token(root)['decimal']
    swap_estimate = [rate/(pow(10, wei))]
    try:
      c = reorder(self.path, root)
    except NotFound as e:
      c = self.path
    try:
      l = len(c)
      for i in range(l):
        src = c[i]
        dest = c[(i+1)%l]
        pair = self.tg.lookup_pair(src, dest)
        pair.update()
        rate = pair.exchange(c[i], c[(i+1)%l], rate)
        info.append(pair.info())
        wei = self.tg.lookup_token(dest)['decimal']
        swap_estimate.append(rate/(pow(10,wei)))
      return {'rate':rate/base, 'path':c, 'info':info, 'swap':swap_estimate}
    except Exception as e:
      raise e

class Analysis:
  def __init__(self, pairs):
    self.tg = nx.Graph()
    self.cycles = [] # all cycles
    self.pairs = {}
    self.tokens = {}
    for p in pairs:
      pair = Pair.build(p)
      src = erc20.unique_name(p.src)
      dest = erc20.unique_name(p.dest)
      self.add_token(src, erc20.get_token_info(p.src))
      self.add_token(dest, erc20.get_token_info(p.dest))
      self.add_pair(src, dest, pair)
      self.tg.add_edge(src, dest)
    tc = nx.algorithms.cycles.cycle_basis(self.tg)
    for c in tc:
      if len(c) > 1: # only interested in cycles with more than 3 node
        self.cycles.append(Cycle(c,self))

  def add_pair(self, key1, key2, pair):
    if not key1 in self.pairs:
      self.pairs[key1] = {}
    if not key2 in self.pairs:
      self.pairs[key2] = {}
    self.pairs[key1][key2] = pair
    self.pairs[key2][key1] = pair

  def add_token(self, key, token):
    if not key in self.tokens:
      self.tokens[key] = token

  def lookup_pair(self, src, dest):
    return self.pairs[src][dest]

  def lookup_token(self, key):
    return self.tokens[key]

  def scan_cycles(self):
    for c in self.cycles:
      try:
        base = 1000000000000000000
        r = c.get_output("WETH_c02a", base)
        if r['rate'] > 0.9:
          print(r,"\n")
        else:
          print(c, r['rate'])
          pass
      except NotFound as e:
        print("NotFound")
        pass
      except CalFault as e:
        raise e
