from web3 import Web3
import os

contract_address = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
contract_abi = [
    {
        "constant": False,
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

ethereum_endpoint = os.environ.get('ETHEREUM_RPC')
web3 = Web3(Web3.HTTPProvider(ethereum_endpoint))

account_address = os.environ.get('ADDRESS')
account_address = web3.to_checksum_address(account_address)
private_key = os.environ.get('PRIVATE_KEY')

contract = web3.eth.contract(web3.to_checksum_address(contract_address), abi=contract_abi)

balance_wei = web3.eth.get_balance(account_address)
balance_eth = web3.from_wei(balance_wei, 'ether')

try:
    amount_to_wrap = web3.to_wei(float(balance_eth)-0.0115, 'ether')
except ValueError:
    quit()

gas_price_wei = web3.eth.gas_price
gas_price_eth = web3.from_wei(gas_price_wei, 'ether')

if (gas_price_eth * 55876) < 0.0035:
    if balance_eth > 0.1:
        transaction = contract.functions.deposit().build_transaction({
            'from': account_address,
            'value': amount_to_wrap,
            'gas': 55876,
            'maxFeePerGas': gas_price_wei,
            'maxPriorityFeePerGas': gas_price_wei,
            'nonce': web3.eth.get_transaction_count(account_address),
            'chainId': 1,
        })

        signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

        transaction_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)