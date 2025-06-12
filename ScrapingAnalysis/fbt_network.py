from . import nx #Networkx
from . import plt #Pyplot
from . import pd #Pandas
from . import time,random,copy
from .TokenManager import TokenManager
from .scraping_functions import get_item_data, extract_item_id, initialize_chromedriver
from common_imports import json

from selenium.webdriver.common.by import By
from .scraping_functions import show_graph_summary

def customers_also_bought(URL, XPATH):
    web = initialize_chromedriver()
    web.get(URL)
    delay2 = random.uniform(1, 3)

    max_wait_time = 10  # Max total wait
    check_interval = 0.5  # Check every 0.5s for new elements
    max_checks = int(max_wait_time / check_interval)

    last_count = -1
    stable_count = 0
    also_bought = []

    try:
        for _ in range(max_checks):
            elements = web.find_elements(By.XPATH, XPATH)
            current_count = len(elements)

            if current_count == last_count:
                stable_count += 1
            else:
                stable_count = 0

            last_count = current_count
            also_bought = elements

            if stable_count >= 3:  # e.g., stable for 1.5s
                break

            time.sleep(check_interval)

        if not also_bought:
            print(f"No 'also bought' elements found after {max_wait_time} seconds.")
    except Exception as e:
        print(f"Failed to collect 'also bought' items:\n{e}")
        web.quit()
        return []

    print(f"Found {len(also_bought)} elements")
    print(f"Sleeping for {delay2:.2f} seconds...")

    links = [x.get_attribute("href") for x in also_bought if x.get_attribute("href")]
    item_ids = [extract_item_id(x) for x in links]

    web.quit()
    time.sleep(delay2)
    return item_ids


def frequently_bought_together(items:dict)->pd.DataFrame:
    for item in items.values():
        item['Also Bought'] = []
    scraped_ids = set(items.keys())
    duplicates = 0
    if items:
        items_copy = copy.deepcopy(items)
        for key,value in items.items():
            also_bought_IDs = customers_also_bought(value['Link'], "//a[contains(@class, 'cHK7')]")
            if also_bought_IDs:
                items_copy[key].update({"Also Bought": also_bought_IDs})

            scraped_ids.add(key)
            last_scraped = {}
            also_bought = items_copy[key]['Also Bought']

            also_bought = list(set(also_bought))
            ebay_token_manager = TokenManager()
            for ID in also_bought:
                if not ID.startswith("v1|"):
                    formatted_ID = f"v1|{ID}|0"
                else:
                    formatted_ID = ID


                if formatted_ID not in scraped_ids:
                    print("Get Data Key is: ",formatted_ID)
                    access_token = ebay_token_manager.get_token()
                    last_scraped = get_item_data(formatted_ID, access_token,'EBAY_US')
                    if last_scraped is not None:
                        last_scraped['Also Bought'] = [key]
                        items_copy[last_scraped['Item ID']] = last_scraped
                        scraped_ids.add(formatted_ID)
                else:
                    if key not in items_copy[formatted_ID]['Also Bought']:
                        items_copy[formatted_ID]['Also Bought'].append(key)
                        print('Added relationship: ', formatted_ID)
                    else:
                        print('Cycle detected, skipping: ', formatted_ID)
                        duplicates += 1
                        continue

        print(len(items_copy))
        print(duplicates, " duplicates found!")

        all_items = list(items_copy.values())

        df = pd.DataFrame(all_items)

        return df
    else:
        print('No items found')

def bought_together_analysis(items:dict,df:pd.DataFrame=None):
    if df is None:
        print("Trying to scrape live data...")
        df = frequently_bought_together(items)
    df["Also Bought"] = df["Also Bought"].fillna("[]")
    df["Also Bought"] = df["Also Bought"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else x
    )

    print(df)
    df["Item ID"] = df["Item ID"].apply(lambda x: f"v1|{x}|0" if not str(x).startswith("v1|") else x)
    # merge duplicate items without deleting them
    # merge them by also bought values while keeping the other attributes from the first item
    try:
        df = df.groupby("Item ID").agg({
            "Title": "first",
            "Price": "first",
            "Seller": "first",
            "Feedback Score": "first",
            "Also Bought": lambda x: list(set().union(*x))
        }).reset_index()
    except Exception as e:
        print(e)
    print(len(df))

    G = nx.Graph()


    item_id_map = {row["Item ID"]: row["Title"] for index, row in df.iterrows()}
    numbered_items = {item_id: i+1 for i, item_id in enumerate(item_id_map.keys())}

    for item_id, title in item_id_map.items():
        G.add_node(numbered_items[item_id],title=title,font_size = 5)


    for _, row in df.iterrows():
        source_id = row["Item ID"]
        if isinstance(row["Also Bought"], list):
            for bought_id in row["Also Bought"]:
                if not bought_id.startswith("v1|"):
                    formatted_bought_id = f"v1|{bought_id}|0"
                else:
                    formatted_bought_id = bought_id
                if formatted_bought_id in item_id_map:
                    if not G.has_edge(numbered_items[source_id], numbered_items[formatted_bought_id]):
                        G.add_edge(numbered_items[source_id], numbered_items[formatted_bought_id])


    betweenness = nx.betweenness_centrality(G,normalized = False)
    betweenness_normalized = dict(nx.betweenness_centrality(G))

    sorted_centrality = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)

    show_graph_summary(G)

    print("Ranked Nodes by Betweenness Centrality (Non-Zero Only):")
    for item_num,centrality in sorted_centrality:
        node = [x for x in numbered_items.keys() if numbered_items[x] == item_num][0]
        if centrality == 0:
            break
        print(f"{item_num}: {item_id_map.get(node, 'Unknown')} - "
            f"Normalized Betweenness Centrality: {betweenness_normalized[item_num]:.5f} - Non-Normalized : {centrality:.5f} ")
        print("-" * 150)




    pos = nx.kamada_kawai_layout(G)

    fig = plt.figure(figsize=(16, 12))

    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=150)

    return fig



