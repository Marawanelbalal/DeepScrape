import sys

from . import nx #Networkx
from . import By,Options,uc #Selenium imports
from . import plt #Pyplot
from . import pd #Pandas
from . import time,random,copy
from .scraping_functions import get_item_data,extract_item_id
from common_imports import json,re


def customers_also_bought(URL,XPATH):
    options = Options()
    # options.add_argument("--headless")  #run in headless mode (no browser will open)
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-features=SharedStorageWorklet")
    #some of the extra arguments are not always helpful, but including them doesn't hurt.


    web = uc.Chrome(options = options)
    web.set_window_size(1366, 768)


    web.get(URL)
    content = web.page_source[:1000]

    delay = random.uniform(random.randint(55, 65), random.randint(75, 85))
    delay2 = random.uniform(1,3)
    print(f"Sleeping for {delay2:.2f} seconds...")
    time.sleep(delay)

    also_bought = web.find_elements(By.XPATH, XPATH)

    print(f"Found {len(also_bought)} elements")

    if also_bought:
      links = [x.get_attribute("href") for x in also_bought]
      item_ids = [extract_item_id(x) for x in links]
      web.quit()
      return item_ids
    else:
      web.quit()
      return []

def frequently_bought_together(items:dict,access_token:str,csv_path:str="")->pd.DataFrame:

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

            def extract_id(s):
                match = re.search(r'\|([^|]+)\|', s)
                if match:
                    return match.group(1)
                return None
            also_bought = list(set(also_bought))
            for ID in also_bought:
                if not ID.startswith("v1|"):
                    formatted_ID = f"v1|{ID}|0"
                    get_data_key = ID
                else:
                    formatted_ID = ID

                    get_data_key = extract_id(formatted_ID)

                if formatted_ID not in scraped_ids:

                    last_scraped = get_item_data(get_data_key, access_token, 'EBAY_US')
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

        if csv_path:
            df_to_save = df.copy()
            df_to_save["Also Bought"] = df_to_save["Also Bought"].apply(json.dumps)
            df_to_save.to_csv(csv_path, index=False)
            try:
                df_to_save.to_pickle(csv_path.rstrip(".csv")+".pkl")
            except Exception as e:
                print(e)


        return df
    else:
        print('No items found')

def bought_together_analysis(items:dict,access_token:str,csv_path:str=""):
    start_time = time.time()
    if csv_path:
        df = pd.read_csv(csv_path)
    else:
        df = frequently_bought_together(items,access_token,csv_path)
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

    print("Top 10 Nodes by Betweenness Centrality:")
    for item_num,centrality in sorted_centrality:
        node = [x for x in numbered_items.keys() if numbered_items[x] == item_num][0]
        print(f"{item_num}: {item_id_map.get(node, 'Unknown')} - "
              f"Normalized Betweenness Centrality: {betweenness_normalized[item_num]} - Non-Normalized : {centrality:.5f} ")
        print("-" * 150)



    pos = nx.kamada_kawai_layout(G)

    fig = plt.figure(figsize=(16, 12))

    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=150)

    print(type(fig))
    runtime = time.time() - start_time
    print(f"Function ran for: {runtime}")
    return fig



