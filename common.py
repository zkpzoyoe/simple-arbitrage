import json
import requests
from decimal import Decimal
from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3 import WebsocketProvider
from uniswap.uniswap import UniswapV2Client
from uniswap.uniswap import UniswapV2Utils as utils
import threading
import random

config = json.load(open('config.json'))
network = config['network']
address = config['address']
privkey = config['privkey']
http_addr = config[network]['http']
wss_addr = config[network]['wss']


w3 = Web3(HTTPProvider(http_addr, request_kwargs={'timeout': 6000}))
ws = Web3(WebsocketProvider(wss_addr))

uni = UniswapV2Client(address, privkey, http_addr)

erc20abi = json.load(open('./abi/erc20.abi'))

def get_current_timestamp():
   block = w3.eth.getBlock('latest')
   return block['timestamp']

# gas
def gasnow():
    ret = requests.get(config['gasnow'])
    return ret.json()['data']

def getBalance(tokenAddress, address):
    c = w3.eth.contract(address=tokenAddress, abi=erc20abi)
    return c.functions.balanceOf(address).call()

def approve(tokenAddr, contractAddr, myAddr, amount, gasPrice):
    erc20Token = w3.eth.contract(address=tokenAddr, abi=erc20abi)
    approved_amount = erc20Token.functions.allowance(myAddr, contractAddr).call()
    if approved_amount >= amount:
        return True
    try:
        tx = erc20Token.functions.approve(contractAddr, 2**256-1).buildTransaction({
            'from': myAddr,
            'value': 0,
            'gasPrice': gasPrice,
            'gas': 1500000,
            "nonce": w3.eth.getTransactionCount(myAddr),
            })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=privkey)
        txhash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print('approving... ', txhash.hex())
        w3.eth.waitForTransactionReceipt(txhash.hex(), timeout=6000)
    except Exception as e:
        print('exception:', e)
        return False
    return True
