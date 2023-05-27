import json
from actions.create_offer import createOffer
from actions.create_single_offer import createSingleOffer
from actions.create_listing_order import createListingOrder


with open("collection_info.json") as jsonfile:
    collection_info = json.load(jsonfile)

with open("sign_message_list.json") as jsonfile:
    sign_message_list = json.load(jsonfile)

for i, j in zip(sign_message_list, collection_info):
    try:
        bought = j['bought']
    except KeyError:
        continue
    if bought==True:
        if i[0] is not None:
            parameters = i[0]['message']
            signature = i[1]
            chainId = i[0]['domain']['chainId']
            chainId_dict = {
                "42161": "arbitrum",
                "43114": "avalanche",
                "1": "ethereum",
                "8217": "klaytn",
                "137": "matic",
                "10": "optimism"
            }
            chain = chainId_dict[chainId]
            createListingOrder(parameters, signature, chain)
    else:
        if i[0] is not None:
            if i[0]['message']['consideration'][0]['token'].upper() == j['contract'].upper():
                slug = j['slug']
                _type = None if (j['type'] == '' or j['trait']=="no") else j['type']
                _value = None if (j['type'] == '' or j['trait']=="no") else j['value']
                parameters = i[0]['message']
                signature = i[1]
                if j['assets'] == '':
                    createOffer(slug, _type, _value, parameters, signature)
                else:
                    chainId = i[0]['domain']['chainId']
                    chainId_dict = {
                        "42161": "arbitrum",
                        "43114": "avalanche",
                        "1": "ethereum",
                        "8217": "klaytn",
                        "137": "matic",
                        "10": "optimism"
                    }
                    chain = chainId_dict[chainId]
                    createSingleOffer(parameters, signature, chain)
