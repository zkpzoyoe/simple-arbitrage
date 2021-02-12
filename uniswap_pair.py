import common
import json
import click
from rejson import Client, Path

pairABI = json.load(open('abi/IUniswapV2Pair.json'))['abi']

# redis json client
rj = Client(host='localhost', port=6379, decode_responses=True)
rj.jsonset('pairs', Path.rootPath(), {})
rj.jsonset('tokens', Path.rootPath(), {})

def set_token_info(token_addr, force):
  path = Path("." + token_addr)
  if not force:
    try:
      return rj.jsonget('tokens', path)
    except Exception:
      force = True
  if force:
    erc20 = common.w3.eth.contract(address=token_addr, abi=common.erc20abi)
    symbol = erc20.functions.symbol().call()
    decimal = erc20.functions.decimals().call()
    ret = {'symbol':symbol, 'decimal':decimal, 'address':token_addr}
    rj.jsonset('tokens', path, ret)
    return ret

def set_pair_info(pair_addr, force):
  path = Path("." + pair_addr)
  if not force:
    try:
      return rj.jsonget('pairs', path)
    except Exception:
      force = True
  if force:
    token0 = common.uni.get_token_0(pair_addr)
    token1 = common.uni.get_token_1(pair_addr)
    token0 = set_token_info(token0, False)
    token1 = set_token_info(token1, False)
    reserves = common.uni.get_reserves(pair_addr)
    pair = {
      'address': pair_addr,
      'token0': token0,
      'token1': token1,
      'reserve0': reserves[0],
      'reserve1': reserves[1],
    }
    rj.jsonset('pairs', path, pair)
    return pair

# update reserves
def updateResJob(pairs, start, end):
    while start < end:
        reserves = common.uni.get_reserves(pairs[start]['address'])
        pairs[start]['reserve0'] = reserves[0]
        pairs[start]['reserve1'] = reserves[1]
        start += 1

def updateReservesMT(pairs):
    if len(pairs) < 10:
        updateResJob(pairs, 0, len(pairs))
    else:
        start = 0
        threads = []
        while start < len(pairs):
            end = start + 50
            if end > len(pairs):
                end = len(pairs)
            t = threading.Thread(target=updateResJob, args=(pairs, start, end))
            t.start()
            threads.append(t)
            start = end
        for t in threads:
            t.join()

def updateReserves(pairs):
    for pair in pairs:
        reserves = common.uni.get_reserves(pair['address'])
        pair['reserve0'] = reserves[0]
        pair['reserve1'] = reserves[1]
    return pairs

def fetch_all_pairs():
  num = common.uni.get_num_pairs()
  print("Total pairs:", num)
  start = 0
  with click.progressbar(range(num), item_show_func=(lambda x: str(x) + "/" + str(num))) as bar:
    for i in bar:
      pair_addr = common.uni.get_pair_by_index(i)
      try:
        pair = set_pair_info(pair_addr, False)
      except Exception as e:
        pass
      #print("sleep({})".format(i))

def getPairs(symbol='USDC', thresh = 500):
    pairs = json.load(open('files/pairs.json'))
    ret = []
    for pair in pairs:
        if pair['token0']['symbol'] == symbol:
            if pair['reserve0'] / pow(10, pair['token0']['decimal']) >= thresh:
                ret.append(pair)
        if pair['token1']['symbol'] == symbol:
            if pair['reserve1'] / pow(10, pair['token1'][decimal]) >= thresh:
                ret.append(pair)
    print('count:', len(ret))
    json.dump(ret, open('files/'+symbol+'_pairs.json', 'w'))


