from web3 import Web3
import os
from data.constants import contract_abi, contract_address

endpoints = {'ethereum': os.environ.get('ETHEREUM_RPC'),
             'matic': os.environ.get('POLYGON_RPC')}

def getWETHbalance(address):

    weth_balance = {}

    for key, value in contract_address.items():
        web3 = Web3(Web3.HTTPProvider(endpoints[key]))
        address = web3.to_checksum_address(address)

        contract = web3.eth.contract(web3.to_checksum_address(
            value), abi=contract_abi)

        try:
            balance_in_wei = contract.functions.balanceOf(address).call()
            balance_in_eth = balance_in_wei / 1E18
        except:
            balance_in_eth = 0.15
        
        weth_balance[key] = balance_in_eth

    return weth_balance