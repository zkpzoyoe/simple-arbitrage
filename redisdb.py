from rejson import Client, Path
# redis json client
rj = Client(host='localhost', port=6379, decode_responses=True)

def init_info_db():
  rj.jsonset('pairs', Path.rootPath(), {})
  rj.jsonset('tokens', Path.rootPath(), {})

def set_token_info(token_addr, info):
  path = Path("." + token_addr)
  rj.jsonset('tokens', path, info)

def get_token_info(token_addr, info):
  path = Path("." + token_addr)
  rj.jsonget('tokens', path)

def set_pair_info(pair_addr, info):
  path = Path("." + pair_addr)
  rj.jsonset('pairs', path, info)

def get_pair_info(pair_addr):
  path = Path("." + pair_addr)
  rj.jsonget('pairs', path)


