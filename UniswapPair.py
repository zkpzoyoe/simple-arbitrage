import common
import json
import click
import erc20address
import redisdb
from decimal import Decimal

pairABI = json.load(open('abi/IUniswapV2Pair.json'))['abi']

def exchange(pair_address, input, output, amount):
  pair = redisdb.get_pair_info(pair_address)
  addr = pair['address']
  src_addr = pair['token0']['address']
  dest_addr = pair['token1']['address']
  reserves = common.uni.get_reserves(addr)
  r = {
    src_addr:reserves[0],
    dest_addr:reserves[1],
    'timestamp':reserves[2],
  }
  d997 = Decimal(997)
  d1000 = Decimal(1000)
  reserve_in = common.switch_decimal(r[input])
  reserve_out = common.switch_decimal(r[output])
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
    token0 = erc20address.get_token_info(token0)
    token1 = erc20address.get_token_info(token1)
    pair = {
      'format': "uniswap",
      'address': pair_addr,
      'token0': token0,
      'token1': token1,
      'timestamp': 0,
    }
    redisdb.set_pair_info(pair_addr, pair)
    return pair

def fetch_all_pairs():
  num = common.uni.get_num_pairs()
  print("Total pairs:", num)
  start = redisdb.get_info("uniswap.index")
  with click.progressbar(range(start, num), item_show_func=(lambda x: str(x) + "/" + str(num))) as bar:
    for i in bar:
      pair_addr = common.uni.get_pair_by_index(i)
      try:
        pair = init_pair_info(pair_addr, False)
      except Exception as e:
        pass
        #raise e
      redisdb.set_info("uniswap.index", i)
