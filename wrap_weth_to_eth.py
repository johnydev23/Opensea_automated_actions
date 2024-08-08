from data.constants import contract_address
from utils.wrap_eth_utils import wrapEthtoWeth


if __name__ == '__main__':

    for key,value in contract_address.items():

        wrapEthtoWeth(key, value)
