from web3 import Web3
import os

endpoints = {'ethereum': os.environ.get('ETHEREUM_RPC'),
             'matic': os.environ.get('POLYGON_RPC')}

contract_address = {'ethereum': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
                    'matic': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619'}


def getWETHbalance(address):

    contract_abi = (
        '[{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
    )

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