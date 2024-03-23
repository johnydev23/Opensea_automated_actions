from web3 import Web3
from data.constants import contract_abi, contract_address
from data.variables import endpoints


def getWETHbalance(address) -> dict:

    weth_balance = {}

    for key, value in contract_address.items():
        w3 = Web3(Web3.HTTPProvider(endpoints[key]))
        address = w3.to_checksum_address(address)

        contract = w3.eth.contract(w3.to_checksum_address(
            value), abi=contract_abi)

        try:
            balance_in_wei = contract.functions.balanceOf(address).call()
            balance_in_eth = balance_in_wei / 1E18
        except:
            balance_in_eth = 0.15
        
        weth_balance[key] = balance_in_eth

    return weth_balance
