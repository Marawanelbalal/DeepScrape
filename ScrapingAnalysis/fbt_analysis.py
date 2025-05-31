import copy
from .scraping_functions import get_item_data, ebay_api
from .scraping_functions import customers_also_bought
import pandas as pd


def frequently_bought_together(items:dict,access_token):

    scraped_ids = set(items.keys())
    duplicates = 0
    if items:
        items_copy = copy.deepcopy(items)
        for key,value in items.items():
            also_bought_IDs = customers_also_bought(value['Link'], "//a[contains(@class, 'cHK7')]")
            if also_bought_IDs:
                items_copy[key].update({"Also Bought": also_bought_IDs})
            else:
                items_copy[key].update({"Also Bought": [value['Item ID']]})
            scraped_ids.add(key)
            last_scraped = {}
            also_bought = items_copy[key]['Also Bought']
            for ID in also_bought:

                if f"v1|{ID}|0" not in scraped_ids:
                    last_scraped = get_item_data(ID, access_token, 'US')
                    if last_scraped is not None:
                        last_scraped['Also Bought'] = [key]
                        items_copy[last_scraped['Item ID']] = last_scraped
                        scraped_ids.add(ID)
                else:
                    items_copy[f"v1|{ID}|0"]['Also Bought'].append(key)

                    print('Duplicate not scraped: ', ID)

                    duplicates += 1
        print(len(items_copy))
        print(duplicates, " duplicates found!")
        for ID,item in items_copy.items():
            print(ID,": ",item)
        all_items = list(items_copy.values())

        df = pd.DataFrame(all_items)

        for item in items_copy.items():
                print(item)

        return df
    else:
        print('No items found')
