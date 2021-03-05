import common
import json
import click
import erc20
import redisdb

pairABI = json.load(open('abi/IUniswapV2Pair.json'))['abi']

class UniSwapPair:
  def __init__(self, pair_address):
    pair = redisdb.get_pair_info(pair_address)
    self.addr = pair['address']
    self.src_addr = erc20.unique_name(pair['token0'])
    self.dest_addr = erc20.unique_name(pair['token2'])
    self.reserves = {
      self.src_addr:0,
      self.dest_addr:0,
      timestamp:pair['timestamp'],
    }

  def update(self):
    reserves = common.uni.get_reserves(self.addr)
    self.reserves = {
      self.src_addr:reserves[0],
      self.src_addr:reserves[1],
      timestamp:pair['timestamp'],
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

def init_pair_info(pair_addr, force):
  if not force:
    try:
      return redisdb.get_pair_info(pair_addr)
    except Exception:
      force = True
  if force:
    token0 = common.uni.get_token_0(pair_addr)
    token1 = common.uni.get_token_1(pair_addr)
    token0 = erc20.get_token_info(token0, False)
    token1 = erc20.get_token_info(token1, False)
    pair = {
      'format': "uniswap",
      'address': pair_addr,
      'token0': token0,
      'token1': token1,
      'timestamp': 0,
    }
    print("set pair info", pair_addr)
    redisdb.set_pair_info(pair_addr, pair)
    return pair

def build_pair(pair):
  if (pair['format'] == "uniswap"):
    print(pair['address'])
    return UniSwapPair(pair['address'])
  else:
    return None

def fetch_all_pairs():
  num = common.uni.get_num_pairs()
  print("Total pairs:", num)
  start = 0
  with click.progressbar(range(num), item_show_func=(lambda x: str(x) + "/" + str(num))) as bar:
    for i in bar:
      pair_addr = common.uni.get_pair_by_index(i)
      try:
        pair = init_pair_info(pair_addr, False)
      except Exception as e:
        raise e
