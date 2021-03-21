# "WETH_c02a"
import erc20address
import decimal
import common
import Pair

class NotFound(Exception):
  pass

def reorder(c, key):
  l = len (c)
  pos = l
  d = []
  for i in range(l):
    uname = erc20address.get_token_info(c[i])['uname']
    if (uname == key):
      pos = i
      break
    else:
      pass
  if (pos == l):
    raise NotFound
  for i in range(l):
    d.append(c[(pos+i)%l])
  return d

def get_output(tg, path, root):
  #print("get_output", path)
  info = []
  try:
    c = reorder(path, root)
  except NotFound as e:
    c = path
  try:
    wei = erc20address.get_token_info(c[0])['decimal']
    base = pow(10, wei)
    rate = common.switch_decimal(base)
    swap_estimate = [rate]
    l = len(c)
    for i in range(l):
      src = c[i]
      dest = c[(i+1)%l]
      pair = tg[src][dest] or tg[src][dest]
      pair = pair['pair']
      rate = Pair.exchange(pair, c[i], c[(i+1)%l], rate)
      info.append(pair['address'])
      swap_estimate.append(rate)
    return {'rate':rate/base, 'path':c, 'info':info, 'swap':swap_estimate}
  except Exception as e:
    raise e


