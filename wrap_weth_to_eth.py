from web3 import Web3
from data.constants import contract_abi, contract_address, balance_left_dict, gas_limit_wrap_dict, chain_id_dict, tx_fee_wrap_dict, wrap_when_amount_dict, bidding_contracts_eth
from data.variables import endpoints, address, private_key
from decimal import ROUND_DOWN, Decimal
from src.swap_params import getSwapParams

def getBiddingBalance(address:str, w3:Web3, bidding_contract:str) -> float:

    account_address = w3.to_checksum_address(address)

    contract = w3.eth.contract(w3.to_checksum_address(bidding_contract), abi=contract_abi)

    try:
        balance_in_wei = contract.functions.balanceOf(account_address).call()
        balance_in_eth = balance_in_wei / 1E18
    except:
        balance_in_eth = 0.15

    return balance_in_eth


for key,value in contract_address.items():

    weth_contract = value

    w3 = Web3(Web3.HTTPProvider(endpoints[key]))

    account_address = w3.to_checksum_address(address)

    if key == 'ethereum':
        beth_contract_eth = bidding_contracts_eth['Blur']
        bidding_balance_opensea = getBiddingBalance(address, w3, value)
        bidding_balance_blur = getBiddingBalance(address, w3, beth_contract_eth)
        if bidding_balance_opensea>bidding_balance_blur:
            weth_contract = beth_contract_eth

    contract = w3.eth.contract(w3.to_checksum_address(weth_contract), abi=contract_abi)

    try:
        balance_wei = w3.eth.get_balance(account_address)
    except ValueError as e:
        print("VALUE ERROR: balance wei")
        print(e)
        continue

    balance_eth = w3.from_wei(balance_wei, 'ether')

    balance_left = balance_left_dict[key]
    balance_left_decimal = Decimal(f"{balance_left}")

    if balance_eth-balance_left_decimal < 0:
        continue

    try:
        amount_to_wrap = w3.to_wei(balance_eth-balance_left_decimal, 'ether')
    except ValueError as e:
        print("VALUE ERROR: amount to wrap")
        print(e)
        continue

    gas_price_wei = w3.eth.gas_price
    gas_price_eth = w3.from_wei(gas_price_wei, 'ether')

    gas_limit = gas_limit_wrap_dict[key]

    chain_id = chain_id_dict[key]
    tx_fee = tx_fee_wrap_dict[key]
    wrap_when_amount_is = wrap_when_amount_dict[key]

    to = ""
    data = ""
    if key == 'matic':
        gas_price_gwei = w3.from_wei(gas_price_wei, 'gwei')
        amount_to_swap = w3.from_wei(amount_to_wrap, 'ether')
        amount_to_swap = Decimal(f"{amount_to_swap}").quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
        tx_params = getSwapParams(account_address, token_out=weth_contract, swap_amount=amount_to_swap, gas_price=gas_price_gwei)
        status_code:int = tx_params.get('code', 400)
        if tx_params and status_code == 200:
            gas_limit = int(int(tx_params['data']['estimatedGas']) * 1.1)
            to = tx_params['data']['to']
            to_formatted = w3.to_checksum_address(to)
            data = tx_params['data']['data']
            amount_to_wrap = int(tx_params['data']['value'])
        else:
            continue
    else:
        try:
            transaction = contract.functions.deposit().build_transaction({
                'from': account_address,
                'value': amount_to_wrap,
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
        if balance_eth > wrap_when_amount_is:
            if key == 'matic':
                transaction = {
                    'from': account_address,
                    'to': to_formatted,
                    'value': amount_to_wrap,
                    'gas': gas_limit,
                    'maxFeePerGas': gas_price_wei,
                    'maxPriorityFeePerGas': gas_price_wei,
                    'data': data,
                    'nonce': w3.eth.get_transaction_count(account_address),
                    'chainId': chain_id,
                }
            else:
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