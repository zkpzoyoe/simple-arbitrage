import common
from redisdb import *

def update_token_info(token_addr):
  erc20 = common.w3.eth.contract(address=token_addr, abi=common.erc20abi)
  symbol = erc20.functions.symbol().call()
  decimal = erc20.functions.decimals().call()
  ret = {'symbol':symbol, 'decimal':decimal, 'address':token_addr}
  set_token_info(token_addr, ret)
  return ret

def get_token_info(token_addr, update):
  if not update:
    try:
      return redisdb.get_token_info('tokens', path)
    except Exception:
      update = True
  if update:
    update_token_info(token_addr)

def unique_name(token_addr):
  token = get_token_info(token_addr, False)
  tok = token_addr.lower()
  return token['symbol'] + "_" + tok[2:6]




