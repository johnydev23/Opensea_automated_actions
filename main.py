import os
import json
import csv
from src.user_tokens_info import getAssetInfo2
from services.bidding import getBiddingMessage
from services.listing import getListingMessage
from utils.get_num_assets import getNumAssets
from utils.find_asset import findTrait, findAsset
from utils.check_listing import checkListing
from utils.concurrent_utils import getBalanceAndUserAssets
from weth_balance import getWETHbalance
from database.connection import closeConnection

address = os.environ.get('ADDRESS')

balance, data_user_contracts, data_user_contracts_info = getBalanceAndUserAssets(getWETHbalance, getAssetInfo2, address)
if data_user_contracts is None:
    print("No user data")
    quit()

for filename in os.listdir('.'):
    if filename.endswith('.csv'):
        csv_file = filename
        break

collection_list = []
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
    asset_contract = v['contract'].upper()
    number_offers = int(v['number offers']) if v['number offers'] != '' else 1
    asset = v['assets'] if v['assets'] != '' else None
    token_standard = v['token standard']
    limit_price_enabled:bool = v['limit price enabled'] == "yes"

    if i>0:
        if slug != collection_list[i-1]['slug']:
            token_id_list = []


    num_assets, chain, assetInfo = getNumAssets(data_user_contracts, data_user_contracts_info, asset, asset_contract)
    if num_assets == None:
        continue

    found = False
    check_listing = False
    for z in range(number_offers if number_offers > 0 else 1):
        message = None
        trait = v['trait'] == 'yes'
        asset_flag = False

        if (num_assets > 0) and (num_assets > len(token_id_list)-z):
            asset_flag = True

        if trait and asset_flag:
            _type = v['type']
            _value = v['value']
            find_trait_results = findTrait(_type, _value, assetInfo, token_id_list)
            if find_trait_results:
                limit_price, token_id, j = find_trait_results
                found = True
                collection_element.update({"limit price": limit_price, "bought": True, "token id": token_id})
                token_id_list.append(token_id)
            
            if found:
                print("Found Token: ", slug, asset_contract, token_id)
                check_listing = checkListing(data_user_contracts, j, address, asset_contract, token_id, chain, limit_price_enabled)
            
            if check_listing:
                print("List token")
                message = getListingMessage(collection_element, address)

        elif asset_flag:
            find_asset_results = findAsset(assetInfo, asset, token_id_list, token_standard, chain, asset_contract)
            if find_asset_results:
                limit_price, token_id, j = find_asset_results
                found = True
                collection_element.update({"limit price": limit_price, "bought": True, "token id": token_id})
                token_id_list.append(token_id)
            
            if found:
                print("Found Token: ", slug, asset_contract)
                check_listing = checkListing(data_user_contracts, j, address, asset_contract, token_id, chain, limit_price_enabled)
            
            if check_listing:
                print("List token")
                message = getListingMessage(collection_element, address)
            
        if found == False and number_offers>0:
            print("Make offer")
            limit_price, message = getBiddingMessage(v, address, balance, z)
            collection_element.update({"limit price": limit_price, "bought": False})
        collection_element.update({"typed_message": message})
        add_element(collection_element)

closeConnection()
