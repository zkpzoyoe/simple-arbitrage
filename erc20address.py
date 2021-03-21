import common
from redisdb import *

def unique_name(symbol, token_addr):
  tok = token_addr.lower()
  return symbol + "_" + tok[2:6]


def update_token_info(token_addr):
  erc20 = common.w3.eth.contract(address=token_addr, abi=common.erc20abi)
  symbol = erc20.functions.symbol().call()
  decimal = erc20.functions.decimals().call()
  ret = {'symbol':symbol,
    'decimal':decimal,
    'address':token_addr,
    'uname':unique_name(symbol, token_addr)
  }
  set_token_info(token_addr, ret)
  return ret

def get_token_info(token_addr):
  path = Path("." + token_addr)
  try:
    return redisdb.get_token_info(path)
  except Exception:
    return update_token_info(token_addr)
