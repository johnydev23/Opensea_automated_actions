from web3 import Web3
from data.constants import operator_address_dict, tx_fee_approval_dict, chain_id_dict, gas_limit_approval_dict
from data.variables import endpoints, address, private_key


def isApprovedForAll(asset_contract, chain='matic'):

    contract_abi = [
        {
            "inputs": [{"internalType": "address", "name": "", "type": "address"},
                       {"internalType": "address", "name": "", "type": "address"}],
            "name": "isApprovedForAll",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]

    endpoint = endpoints[chain]
    w3 = Web3(Web3.HTTPProvider(endpoint))

    operator_address = operator_address_dict[chain]
    operator_address = w3.to_checksum_address(operator_address)

    account_address = w3.to_checksum_address(address)
    asset_contract = w3.to_checksum_address(asset_contract)

    contract = w3.eth.contract(asset_contract, abi=contract_abi)

    try:
        is_approved = contract.functions.isApprovedForAll(account_address, operator_address).call()
    except:
        is_approved = True

    return is_approved

approval_contracts_global = []

def setApproved(asset_contract:str, chain='matic'):
    global approval_contracts_global

    if asset_contract.upper() in approval_contracts_global:
        return

    contract_abi = [
        {
            "constant": False,
            "inputs": [
                {
                    "name": "operator",
                    "type": "address"
                },
                {
                    "name": "approved",
                    "type": "bool"
                }
            ],
            "name": "setApprovalForAll",
            "outputs": [],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]

    endpoint = endpoints[chain]
    w3 = Web3(Web3.HTTPProvider(endpoint))

    operator_address = operator_address_dict[chain]
    operator_address = w3.to_checksum_address(operator_address)

    account_address = w3.to_checksum_address(address)
    asset_contract = w3.to_checksum_address(asset_contract)

    contract = w3.eth.contract(asset_contract, abi=contract_abi)

    balance_wei = w3.eth.get_balance(account_address)
    balance_eth = w3.from_wei(balance_wei, 'ether')

    gas_price_wei = w3.eth.gas_price
    gas_price_eth = w3.from_wei(gas_price_wei, 'ether')

    tx_fee = tx_fee_approval_dict[chain]
    chain_id = chain_id_dict[chain]

    gas_limit = gas_limit_approval_dict[chain]

    try:
        transaction = contract.functions.setApprovalForAll(operator_address, True).build_transaction({
            'from': account_address,
            'value': 0,
            'gas': gas_limit,
            'maxFeePerGas': gas_price_wei,
            'maxPriorityFeePerGas': gas_price_wei,
            'nonce': w3.eth.get_transaction_count(account_address),
            'chainId': chain_id,
        })

        gas_limit = int(w3.eth.estimate_gas(transaction=transaction, block_identifier='latest') * 1.2)
    except:
        pass

    if (gas_price_eth * gas_limit) < tx_fee:
        if balance_eth > tx_fee:
            transaction = contract.functions.setApprovalForAll(operator_address, True).build_transaction({
                'from': account_address,
                'value': 0,
                'gas': gas_limit,
                'maxFeePerGas': gas_price_wei,
                'maxPriorityFeePerGas': gas_price_wei,
                'nonce': w3.eth.get_transaction_count(account_address),
                'chainId': chain_id,
            })

            signed_txn = w3.eth.account.sign_transaction(
                transaction, private_key=private_key)

            w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            approval_contracts_global.append(asset_contract.upper())