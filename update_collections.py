import csv
from database.get_collections import getCollections

collections = getCollections()

def assets_as_number(item):
    assets_str = item['assets']
    return int(assets_str) if assets_str else 0

collection_list = sorted(collections, key=lambda x: (x['slug'], assets_as_number(x)), reverse=False)
fields = list(collection_list[0].keys())

fields.insert(0, 'ID')

file_name = 'Collections.csv'

with open(file_name, mode='w', newline='') as file_csv:

    writer_csv = csv.DictWriter(file_csv, fieldnames=fields)
    
    writer_csv.writeheader()

    for idx, item in enumerate(collection_list):
        item['ID'] = idx + 1
        writer_csv.writerow(item)
