import json
from src.create_offer import createOffer
from src.create_single_offer import createSingleOffer
from src.create_listing_order import createListingOrder
from data.constants import chainId_dict

with open("collection_info.json") as jsonfile:
    collection_info = json.load(jsonfile)

for j in collection_info:
    try:
        bought = j['bought']
    except KeyError:
        continue
    if bought==True:
        if j['typed_message'] is not None:
            parameters = j['typed_message']['message']
            signature = j['signature']
            chainId = j['typed_message']['domain']['chainId']
            chain = chainId_dict[chainId]
            createListingOrder(parameters, signature, chain)
    else:
        if j['typed_message'] is not None:
            slug = j['slug']
            _type = None if (j['type'] == '' or j['trait']=="no") else j['type']
            _value = None if (j['type'] == '' or j['trait']=="no") else j['value']
            parameters = j['typed_message']['message']
            signature = j['signature']
            if j['assets'] == '':
                createOffer(slug, _type, _value, parameters, signature)
            else:
                chainId = j['typed_message']['domain']['chainId']
                chain = chainId_dict[chainId]
                createSingleOffer(parameters, signature, chain)
