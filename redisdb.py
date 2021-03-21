from rejson import Client, Path
# redis json client
rj = Client(host='localhost', port=6379, decode_responses=True)

def init_info_db():
  info = rj.jsonget("info", ".")
  if (info):
    print(info)
    return info
  else:
    info = {"uniswap":{"index": 0}}
    rj.jsonset('info', Path.rootPath(), info)
    rj.jsonset('pairs', Path.rootPath(), {})
    rj.jsonset('tokens', Path.rootPath(), {})
    rj.jsonset('paths', Path.rootPath(), {})
    return info

def get_info(path):
  print(path)
  path = Path("." + path)
  return rj.jsonget("info", path)

def set_info(path, info):
  path = Path("." + path)
  rj.jsonset("info", path, info)


def set_token_info(token_addr, info):
  path = Path("." + token_addr)
  rj.jsonset('tokens', path, info)

def get_token_info(token_addr):
  path = Path("." + token_addr)
  return rj.jsonget('tokens', path)

def set_pair_info(pair_addr, info):
  path = Path("." + pair_addr)
  rj.jsonset('pairs', path, info)

def get_pair_info(pair_addr):
  path = Path("." + pair_addr)
  return rj.jsonget('pairs', path)

def encode_path(path):
  code = ""
  for paddr in path:
    code += get_token_info(paddr)['uname']
  return code

def add_path_info(p):
  info = {'path':p, 'rate':0}
  path = Path("." + encode_path(p))
  rj.jsonset('paths', path, info)

def update_path_rate(info, rate):
  path = Path("." + encode_path(info))
  info = get_path_info(info)
  info['rate'] = rate
  rj.jsonset('paths', path, info)

def get_path_info(info):
  path = Path("." + encode_path(info))
  return rj.jsonget('paths', path)

def get_all_paths():
  return rj.jsonget("paths").values()
