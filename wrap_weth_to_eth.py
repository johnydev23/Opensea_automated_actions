from web3 import Web3
from data.constants import contract_abi, contract_address, balance_left_dict, gas_limit_wrap_dict, chain_id_dict, tx_fee_wrap_dict, wrap_when_amount_dict
from data.variables import endpoints, address, private_key


for key,value in contract_address.items():
    if key == 'matic':
        continue

    weth_contract = value

    w3 = Web3(Web3.HTTPProvider(endpoints[key]))

    account_address = w3.to_checksum_address(address)

    contract = w3.eth.contract(w3.to_checksum_address(weth_contract), abi=contract_abi)

    try:
        balance_wei = w3.eth.get_balance(account_address)
    except ValueError as e:
        print("VALUE ERROR")
        print(e)
        continue

    balance_eth = w3.from_wei(balance_wei, 'ether')

    balance_left = balance_left_dict[key]

    try:
        amount_to_wrap = w3.to_wei(float(balance_eth)-balance_left, 'ether')
    except ValueError:
        continue

    gas_price_wei = w3.eth.gas_price
    gas_price_eth = w3.from_wei(gas_price_wei, 'ether')

    gas_limit = gas_limit_wrap_dict[key]

    chain_id = chain_id_dict[key]
    tx_fee = tx_fee_wrap_dict[key]
    wrap_when_amount_is = wrap_when_amount_dict[key]

    if (gas_price_eth * gas_limit) < tx_fee:
        if balance_eth > wrap_when_amount_is:
            transaction = contract.functions.deposit().build_transaction({
                'from': account_address,
                'value': amount_to_wrap,
                'gas': gas_limit,
                'maxFeePerGas': gas_price_wei,
                'maxPriorityFeePerGas': gas_price_wei,
                'nonce': w3.eth.get_transaction_count(account_address),
                'chainId': chain_id,
            })

            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

            transaction_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)