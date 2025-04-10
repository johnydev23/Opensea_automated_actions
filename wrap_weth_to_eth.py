from data.constants import contract_address, blockchains
from utils.wrap_eth_utils import wrapEthtoWeth


if __name__ == '__main__':

    for key,value in contract_address.items():
        if key in blockchains:
            wrapEthtoWeth(key, value)
