from web3 import Web3
import os

ethereum_endpoint = os.environ.get('ETHEREUM_RPC')
contract_address_weth = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
web3 = Web3(Web3.HTTPProvider(ethereum_endpoint))

def getWETHbalance(address):
    address = web3.to_checksum_address(address)
    
    contract_abi = (
        '[{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        )

    contract = web3.eth.contract(web3.to_checksum_address(contract_address_weth), abi=contract_abi)
    weth_balance = contract.functions.balanceOf(address).call()
    return weth_balance/1E18