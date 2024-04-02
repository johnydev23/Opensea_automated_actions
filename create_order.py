import json
import time
import threading
from src.create_offer import createOffer
from src.create_single_offer import createSingleOffer
from src.create_listing_order import createListingOrder
from data.constants import chainId_dict
from utils.sign_str_message import signTypedMessage

def createOrder(j:dict):
    try:
        bought:bool = j['bought']
    except KeyError:
        return
    
    _id = str(j['ID'])


    if j['typed_message']:
        startTime = int(j['typed_message']['message']['startTime'])
        endTime = int(j['typed_message']['message']['endTime'])
        order_duration = endTime - startTime
        new_startTime = int(time.time())
        j['typed_message']['message']['startTime'] = str(new_startTime)
        j['typed_message']['message']['endTime'] = str(new_startTime + order_duration)
    
    if bought==True:
        if j['typed_message'] is not None:
            signature = signTypedMessage(j['typed_message'])
            parameters = j['typed_message']['message']
            # signature = j['signature']
            chainId = j['typed_message']['domain']['chainId']
            chain = chainId_dict[chainId]
            createListingOrder(parameters, signature, chain, _id)
    else:
        if j['typed_message'] is not None:
            slug = str(j['slug'])
            trait:bool = j['trait']=="yes"
            _type = None if (j['type'] == '' or not trait) else j['type']
            _value = None if (j['type'] == '' or not trait) else j['value']
            signature = signTypedMessage(j['typed_message'])
            parameters = j['typed_message']['message']
            # signature = j['signature']
            if j['assets'] == '' or trait:
                createOffer(slug, _type, _value, parameters, signature, _id)
            else:
                chainId = j['typed_message']['domain']['chainId']
                chain = chainId_dict[chainId]
                createSingleOffer(parameters, signature, chain, _id)
    
if __name__ == '__main__':

    with open("collection_info.json") as jsonfile:
        collection_info = json.load(jsonfile)
    
    for item in collection_info:
        print("=============================")
        print(item)

    threads = []
    for item in collection_info:
        thread = threading.Thread(target=createOrder, args=(item,))
        threads.append(thread)
        time.sleep(1)
        thread.start()
    
    for thread in threads:
        thread.join()
