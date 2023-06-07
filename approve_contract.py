from web3 import Web3
import os


def setApproved(asset_contract, chain='matic'):

    contract_address_dict = {
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

    contract_address = contract_address_dict[chain]
    contract_address = web3.to_checksum_address(contract_address)

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

    if (gas_price_eth * 102682) < limit_gas:
        if balance_eth > limit_gas:
            transaction = contract.functions.setApprovalForAll(contract_address, True).build_transaction({
                'from': account_address,
                'value': 0,
                'gas': 102682,
                'maxFeePerGas': gas_price_wei,
                'maxPriorityFeePerGas': gas_price_wei,
                'nonce': web3.eth.get_transaction_count(account_address),
                'chainId': chain_id,
            })

            signed_txn = web3.eth.account.sign_transaction(
                transaction, private_key=private_key)

            web3.eth.send_raw_transaction(signed_txn.rawTransaction)
