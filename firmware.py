import json
import requests
import decimal
import time
import random
from common import *
import networkx as nx

class NotFound(Exception):
  pass

class CalFault(Exception):
  pass

uni = UniswapV2Client(address, privkey, http_addr)

def switch_decimal(c):
  if not isinstance(c, Decimal):
    return Decimal(c)
  else:
    return c

def unique_name(token):
  tok = token['address'].lower()
  return token['symbol'] + "_" + tok[2:6]

class UniSwapPair:
  def __init__(self, uni, pair):
    self.addr = pair['address']
    self.tokens = [unique_name(pair['token0']), unique_name(pair['token1'])]
    self.reserves = {
      self.tokens[0]:0,
      self.tokens[1]:0
    }

  def update(self):
    reserves = uni.get_reserves(self.addr)
    self.reserves = {
      self.tokens[0]:reserves[0],
      self.tokens[1]:reserves[1]
    }

  def exchange(self, input, output, amount):
    d997 = Decimal(997)
    d1000 = Decimal(1000)
    reserve_in = switch_decimal(self.reserves[input])
    reserve_out = switch_decimal(self.reserves[output])
    try:
      return d997*amount*reserve_out/(d1000*reserve_in+d997*amount)
    #except decimal.DivisionUndefined as e:
    except Exception as e:
      raise e

  def info(self):
    return {"address":self.addr, "reserves":self.reserves}

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
      pair = UniSwapPair(uni, p)
      src = unique_name(p['token0'])
      dest = unique_name(p['token1'])
      self.add_token(src, p['token0'])
      self.add_token(dest, p['token1'])
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
