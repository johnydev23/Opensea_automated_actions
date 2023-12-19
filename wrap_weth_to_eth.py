from web3 import Web3
import os
from data.constants import contract_abi, contract_address

weth_contract = contract_address['ethereum']

ethereum_endpoint = os.environ.get('ETHEREUM_RPC')
web3 = Web3(Web3.HTTPProvider(ethereum_endpoint))

account_address = os.environ.get('ADDRESS')
account_address = web3.to_checksum_address(account_address)
private_key = os.environ.get('PRIVATE_KEY')

contract = web3.eth.contract(web3.to_checksum_address(weth_contract), abi=contract_abi)

balance_wei = web3.eth.get_balance(account_address)
balance_eth = web3.from_wei(balance_wei, 'ether')

try:
    amount_to_wrap = web3.to_wei(float(balance_eth)-0.0515, 'ether')
except ValueError:
    quit()

gas_price_wei = web3.eth.gas_price
gas_price_eth = web3.from_wei(gas_price_wei, 'ether')

if (gas_price_eth * 40000) < 0.0035:
    if balance_eth > 0.20:
        transaction = contract.functions.deposit().build_transaction({
            'from': account_address,
            'value': amount_to_wrap,
            'gas': 40000,
            'maxFeePerGas': gas_price_wei,
            'maxPriorityFeePerGas': gas_price_wei,
            'nonce': web3.eth.get_transaction_count(account_address),
            'chainId': 1,
        })

        signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

        transaction_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)