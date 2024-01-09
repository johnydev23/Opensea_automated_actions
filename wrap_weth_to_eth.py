from web3 import Web3
from data.constants import contract_abi, contract_address
from data.variables import ethereum_endpoint, address, private_key

weth_contract = contract_address['ethereum']

w3 = Web3(Web3.HTTPProvider(ethereum_endpoint))

account_address = w3.to_checksum_address(address)

contract = w3.eth.contract(w3.to_checksum_address(weth_contract), abi=contract_abi)

try:
    balance_wei = w3.eth.get_balance(account_address)
except ValueError as e:
    print("VALUE ERROR")
    print(e)
    quit()

balance_eth = w3.from_wei(balance_wei, 'ether')

try:
    amount_to_wrap = w3.to_wei(float(balance_eth)-0.0515, 'ether')
except ValueError:
    quit()

gas_price_wei = w3.eth.gas_price
gas_price_eth = w3.from_wei(gas_price_wei, 'ether')

if (gas_price_eth * 40000) < 0.0035:
    if balance_eth > 0.20:
        transaction = contract.functions.deposit().build_transaction({
            'from': account_address,
            'value': amount_to_wrap,
            'gas': 40000,
            'maxFeePerGas': gas_price_wei,
            'maxPriorityFeePerGas': gas_price_wei,
            'nonce': w3.eth.get_transaction_count(account_address),
            'chainId': 1,
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

        transaction_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)