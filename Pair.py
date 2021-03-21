import UniswapPair
def build(pair):
  return UniswapPair.build_pair(pair)

def exchange(pair, src, dest, amount):
  if (pair['format'] == "uniswap"):
    return UniswapPair.exchange(pair['address'], src, dest, amount)
  else:
    return None

