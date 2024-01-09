import os
import json
import csv
from services.bidding import getBiddingMessage
from services.listing import getListingMessage
from utils.add_element_utils import save_collection_info
from utils.set_actions import setActions
from utils.concurrent_utils import getBalanceAndUserAssets
from database.connection import closeConnection
from data.variables import address
import threading
import time

collection_list = []

with open("collection_info.json", "w") as jsonfile:
    json.dump(collection_list, jsonfile)

balance, data_user_contracts, data_user_contracts_info = getBalanceAndUserAssets(address)
if data_user_contracts is None:
    print("No user data")
    quit()

for filename in os.listdir('.'):
    if filename.endswith('.csv'):
        csv_file = filename
        break


with open(csv_file, 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        collection_list.append(row)

collection_list = sorted(collection_list, key=lambda x: (x['slug'], x['trait']), reverse=True)

def run(item:dict):
    action = str(item['action'])
    if action == 'make offer':
        getBiddingMessage(item, address, balance)
    elif action == 'list token':
        getListingMessage(item, address)


if __name__ == '__main__':

    action_list = setActions(collection_list, data_user_contracts, data_user_contracts_info)

    chunk_size = 10

    chunks = [action_list[i:i + chunk_size] for i in range(0, len(action_list), chunk_size)]

    for chunk in chunks:

        threads = []
        for item in chunk:
            thread = threading.Thread(target=run, args=(item,))
            threads.append(thread)
            time.sleep(0.25)
            thread.start()

        for thread in threads:
            thread.join()
        
    save_collection_info()

    closeConnection()