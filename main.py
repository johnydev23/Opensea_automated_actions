import os
import json
import csv
from actions.user_tokens_info import getAssetInfo, getAssetInfo2
from actions.bidding import getBiddingMessage
from actions.listing import getListingMessage
from actions.token_listed_price import getListedPrice
from weth_balance import getWETHbalance

address = os.environ.get('ADDRESS')
balance = getWETHbalance(address)
collection_list = []
data_user_contracts, data_user_contracts_info = getAssetInfo2(address)

for filename in os.listdir('.'):
    if filename.endswith('.csv'):
        csv_file = filename
        break

with open(csv_file, 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        collection_list.append(row)

collection_list = sorted(collection_list, key=lambda x: (x['slug'], x['trait']), reverse=True)
collection_info = []

with open("collection_info.json", "w") as jsonfile:
    json.dump(collection_info, jsonfile)

token_id_list = []

def add_element(element):
    try:
        with open("collection_info.json") as jsonfile:
            collection_info = json.load(jsonfile)
    except FileNotFoundError:
        collection_info = []
    collection_info.append(element)
    with open("collection_info.json", "w") as jsonfile:
        json.dump(collection_info, jsonfile)

for i,v in enumerate(collection_list):
    collection_element = collection_list[i]
    slug = v['slug']
    message = None
    number_offers = int(v['number offers']) if v['number offers'] != '' else 1
    if i>0:
        if slug != collection_list[i-1]['slug']:
            token_id_list = []
    asset = v['assets'] if v['assets'] != '' else None
    if data_user_contracts is None:
        assetInfo = getAssetInfo(address, slug, asset)
        try:
            num_assets = len(assetInfo['assets'])
        except KeyError:
            continue
    else:
        asset_contract = v['contract'].lower()
        if asset_contract in data_user_contracts:
            num_assets = data_user_contracts_info[asset_contract]['owns_total']
            chain = data_user_contracts_info[asset_contract]['chain']
            assetInfo = data_user_contracts_info[asset_contract]
        else:
            num_assets = 0
    for z in range(number_offers):
        print(z)
        print(v)
        if (num_assets > 0) and (num_assets > len(token_id_list)-z):
            trait = v['trait'] == 'yes'
            if trait:
                _type = v['type']
                _value = v['value']
                found = False
                for j in assetInfo['assets']:
                    if data_user_contracts is None:
                        traits = j['traits']
                    else:
                        metadata = j['metadata_json']
                        metadata_json = json.loads(metadata)
                        traits = metadata_json['attributes']
                    for k in traits:
                        if k['trait_type'] == _type and k['value'] == _value:
                            token_id = j['token_id']
                            if token_id not in token_id_list:
                                last_sale_price = float(j['last_sale']['total_price'])/1E18 if data_user_contracts is None else j['latest_trade_price']
                                limit_price = last_sale_price if v['limit price']=='' else float(v['limit price'])
                                limit_price = limit_price * (1 + float(v['limit variation'])/100) if v['limit price']!='' else limit_price
                                collection_element.update({"limit price": limit_price, "bought": True, "token id": token_id})
                                token_id_list.append(token_id)
                                print("List token")
                                found = True
                                if data_user_contracts is None:
                                    listed = j['seaport_sell_orders']
                                    if listed is None:
                                        message = getListingMessage(collection_element, address)
                                else:
                                    listed = getListedPrice(asset_contract,token_id,chain)
                                    try:
                                        offerer = listed['orders'][0]['protocol_data']['parameters']['offerer'].upper()
                                    except KeyError:
                                        offerer = address.upper()
                                    except IndexError:
                                        offerer = None
                                    except TypeError:
                                        offerer = address.upper()
                                    if address.upper() != offerer:
                                        message = getListingMessage(collection_element, address)
                                break
                            if found:
                                break
            else:
                for j in assetInfo['assets']:
                    token_id = j['token_id']
                    if v['assets'] != '':
                        asset_id = v['assets']
                        if asset_id != token_id:
                            continue
                    if token_id not in token_id_list:
                        last_sale_price = float(j['last_sale']['total_price'])/1E18 if data_user_contracts is None else j['latest_trade_price']
                        limit_price = last_sale_price
                        collection_element.update({"limit price": limit_price, "bought": True, "token id": token_id})
                        token_id_list.append(token_id)
                        print("List token")
                        if data_user_contracts is None:
                            listed = j['seaport_sell_orders']        
                            if listed is None:
                                message = getListingMessage(collection_element, address)
                            elif v['token standard']=='ERC-1155':
                                offerer = j['seaport_sell_orders'][0]['protocol_data']['parameters']['offerer'].upper()             
                                if address.upper() != offerer:
                                    message = getListingMessage(collection_element, address)
                        else:
                            listed = getListedPrice(asset_contract,token_id,chain)
                            try:
                                offerer = listed['orders'][0]['protocol_data']['parameters']['offerer'].upper()
                            except KeyError:
                                offerer = address.upper()
                            except IndexError:
                                offerer = None
                            except TypeError:
                                offerer = address.upper()
                            if address.upper() != offerer:
                                message = getListingMessage(collection_element, address)
                        break
        else:
            print("Make offer")
            limit_price, message = getBiddingMessage(v, address, balance, z)
            collection_element.update({"limit price": limit_price, "bought": False})
        collection_element.update({"typed_message": message})
        add_element(collection_element)
