from web3 import Web3
import os


def isApprovedForAll(asset_contract, chain='matic'):

    operator_address_dict = {
        "ethereum": "0x1E0049783F008A0085193E00003D00cd54003c71",
        "matic": "0x1E0049783F008A0085193E00003D00cd54003c71",
        "arbitrum": "",
        "optimism": "",
    }

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

    endpoint_dict = {
        "ethereum": 'ETHEREUM_RPC',
        "matic": "POLYGON_RPC",
    }

    endpoint = os.environ.get(endpoint_dict[chain])
    web3 = Web3(Web3.HTTPProvider(endpoint))

    operator_address = operator_address_dict[chain]
    operator_address = web3.to_checksum_address(operator_address)

    account_address = os.environ.get('ADDRESS')
    account_address = web3.to_checksum_address(account_address)
    asset_contract = web3.to_checksum_address(asset_contract)

    contract = web3.eth.contract(asset_contract, abi=contract_abi)

    try:
        is_approved = contract.functions.isApprovedForAll(account_address, operator_address).call()
    except:
        is_approved = True

    return is_approved


def setApproved(asset_contract, chain='matic'):

    operator_address_dict = {
        "ethereum": "0x1E0049783F008A0085193E00003D00cd54003c71",
        "matic": "0x1E0049783F008A0085193E00003D00cd54003c71",
        "arbitrum": "",
        "optimism": "",
    }

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

    endpoint_dict = {
        "ethereum": 'ETHEREUM_RPC',
        "matic": "POLYGON_RPC",
    }

    endpoint = os.environ.get(endpoint_dict[chain])
    web3 = Web3(Web3.HTTPProvider(endpoint))

    operator_address = operator_address_dict[chain]
    operator_address = web3.to_checksum_address(operator_address)

    account_address = os.environ.get('ADDRESS')
    account_address = web3.to_checksum_address(account_address)
    asset_contract = web3.to_checksum_address(asset_contract)
    private_key = os.environ.get('PRIVATE_KEY')

    contract = web3.eth.contract(asset_contract, abi=contract_abi)

    balance_wei = web3.eth.get_balance(account_address)
    balance_eth = web3.from_wei(balance_wei, 'ether')

    gas_price_wei = web3.eth.gas_price
    gas_price_eth = web3.from_wei(gas_price_wei, 'ether')

    limit_gas_dict = {
        "ethereum": 0.004,
        "matic": 0.5,
    }

    chain_id_dict = {
        "ethereum": 1,
        "matic": 137,
        "arbitrum": 42161,
        "optimism": 10,
    }

    limit_gas = limit_gas_dict[chain]
    chain_id = chain_id_dict[chain]

    if (gas_price_eth * 69335) < limit_gas:
        if balance_eth > limit_gas:
            transaction = contract.functions.setApprovalForAll(operator_address, True).build_transaction({
                'from': account_address,
                'value': 0,
                'gas': 69335,
                'maxFeePerGas': gas_price_wei,
                'maxPriorityFeePerGas': gas_price_wei,
                'nonce': web3.eth.get_transaction_count(account_address),
                'chainId': chain_id,
            })

            signed_txn = web3.eth.account.sign_transaction(
                transaction, private_key=private_key)

            web3.eth.send_raw_transaction(signed_txn.rawTransaction)