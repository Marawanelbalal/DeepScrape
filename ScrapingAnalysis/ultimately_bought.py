from networkx.algorithms.centrality import in_degree_centrality

from . import nx #Networkx
from . import plt #Pyplot
from . import pd #Pandas
from . import time,random,copy
from .TokenManager import TokenManager
from .scraping_functions import get_item_data, extract_item_id, initialize_chromedriver
from common_imports import json

from selenium.webdriver.common.by import By
from .scraping_functions import show_graph_summary

def customers_ultimately_bought(URL, XPATH):
    web = initialize_chromedriver()
    web.get(URL)
    delay2 = random.uniform(1, 3)

    max_wait_time = 10  # Max total wait
    check_interval = 0.5  # Check every 0.5s for new elements
    max_checks = int(max_wait_time / check_interval)

    last_count = -1
    stable_count = 0
    ultimately_bought = []

    try:
        for _ in range(max_checks):
            elements = web.find_elements(By.XPATH, XPATH)
            current_count = len(elements)

            if current_count == last_count:
                stable_count += 1
            else:
                stable_count = 0

            last_count = current_count
            ultimately_bought = elements

            if stable_count >= 3:  # e.g., stable for 1.5s
                break

            time.sleep(check_interval)

        if not ultimately_bought:
            print(f"No 'Ultimately Bought' elements found after {max_wait_time} seconds.")
    except Exception as e:
        print(f"Failed to collect 'Ultimately Bought' items:\n{e}")
        web.quit()
        web = None
        return []

    print(f"Found {len(ultimately_bought)} elements")
    print(f"Sleeping for {delay2:.2f} seconds...")

    links = [x.get_attribute("href") for x in ultimately_bought if x.get_attribute("href")]
    item_ids = [extract_item_id(x) for x in links]

    web.quit()
    web = None #To help the garbage collector know the driver is gone
    time.sleep(delay2)
    return item_ids


def ultimately_bought_dataframe(items:dict)->pd.DataFrame:
    for item in items.values():
        item['Ultimately Bought'] = []
    scraped_ids = set(items.keys())
    duplicates = 0
    if items:
        items_copy = copy.deepcopy(items)
        for key,value in items.items():
            ultimately_bought_IDs = customers_ultimately_bought(value['Link'], "//a[contains(@class, 'NEvY')]")
            if ultimately_bought_IDs:
                items_copy[key].update({"Ultimately Bought": ultimately_bought_IDs})

            scraped_ids.add(key)
            last_scraped = {}
            ultimately_bought = items_copy[key]['Ultimately Bought']

            ultimately_bought = list(set(ultimately_bought))
            ebay_token_manager = TokenManager()
            for ID in ultimately_bought:
                if not ID.startswith("v1|"):
                    formatted_ID = f"v1|{ID}|0"
                else:
                    formatted_ID = ID


                if formatted_ID not in scraped_ids:
                    print("Get Data Key is: ",formatted_ID)
                    access_token = ebay_token_manager.get_token()
                    last_scraped = get_item_data(formatted_ID, access_token,'EBAY_US')
                    if last_scraped is not None:
                        items_copy[last_scraped['Item ID']] = last_scraped
                        scraped_ids.add(formatted_ID)

        print(len(items_copy))
        print(duplicates, " duplicates found!")

        all_items = list(items_copy.values())

        df = pd.DataFrame(all_items)
        return df
    else:
        print('No items found')

def ultimately_bought_network(items:dict,df:pd.DataFrame=None):
    if df is None:
        print("Trying to scrape live data...")
        df =ultimately_bought_dataframe(items)
    df["Ultimately Bought"] = df["Ultimately Bought"].fillna("[]")
    def safe_json_load(x):
        if isinstance(x, str):
            try:
                return json.loads(x)
            except json.JSONDecodeError:
                return x
        return x
    df["Ultimately Bought"] = df["Ultimately Bought"].apply(safe_json_load)

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
            "Ultimately Bought": lambda x: list(set().union(*x))
        }).reset_index()
    except Exception as e:
        print(e)
    print(len(df))

    G = nx.DiGraph()


    item_id_map = {row["Item ID"]: row["Title"] for index, row in df.iterrows()}
    numbered_items = {item_id: i+1 for i, item_id in enumerate(item_id_map.keys())}

    for item_id, title in item_id_map.items():
        G.add_node(numbered_items[item_id],title=title,font_size = 5)


    for _, row in df.iterrows():
        source_id = row["Item ID"]
        if isinstance(row["Ultimately Bought"], list):
            for bought_id in row["Ultimately Bought"]:
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

    print("\n\tRanked Nodes by Betweenness Centrality (Non-Zero Only):")
    for item_num,centrality in sorted_centrality:
        node = [x for x in numbered_items.keys() if numbered_items[x] == item_num][0]
        if centrality == 0:
            break
        print(f"{item_num}: {item_id_map.get(node, 'Unknown')} - "
            f"Normalized Betweenness Centrality: {betweenness_normalized[item_num]:.5f} - Non-Normalized : {centrality:.5f} ")
        print(f"In-Degree: {G.in_degree(item_num)} - Out-Degree: {G.out_degree(item_num)}")
        print("-" * 150)
    in_degrees = G.in_degree()
    out_degrees = G.out_degree()
    if len(G.in_degree()) <= 20:
        top_in_degrees = sorted(G.in_degree(),key=lambda x:x[1],reverse = True)
    else:
        top_in_degrees = sorted(G.in_degree(),key=lambda x:x[1],reverse = True)[:20]
    if len(G.out_degree()) <= 20:
        top_out_degrees = sorted(G.out_degree(),key=lambda x:x[1],reverse = True)
    else:
        top_out_degrees = sorted(G.out_degree(),key=lambda x:x[1],reverse = True)[:20]


    print("\n\tTop 20 Nodes By In-Degree (Customers Ultimately Bought These):")
    for node,in_degree in top_in_degrees:
        name = G.nodes[node].get("title",f"Node")
        out_degree = out_degrees[node]
        print(f"{node}: {name}\nIn-Degree: {in_degree} - Out-Degree: {out_degree}")
        print("-"*100)
    print("\n\tTop 20 Nodes By Out-Degree (Customers Ultimately Moved Away From These")
    for node,out_degree in top_out_degrees:
        name = G.nodes[node].get("title",f"Node")
        in_degree = in_degrees[node]
        print(f"{node}: {name}\nOut-Degree: {out_degree} - In-Degree: {in_degree}")
        print("-"*100)

    pagerank = nx.pagerank(G, alpha=0.85)

    if len(pagerank.items()) <= 20:
        top_pageranks = sorted(pagerank.items(),key=lambda x:x[1],reverse = True)
    else:
        top_pageranks = sorted(pagerank.items(),key=lambda x:x[1],reverse = True)[:20]
    print("\n\tTop 20 nodes with highest pagerank:")
    for node, rank in top_pageranks:
        name = G.nodes[node].get("title",node)
        print(f"{name}: {rank:.4f}")
        print("-"*100)

    pos = nx.kamada_kawai_layout(G)

    fig = plt.figure(figsize=(12, 12))
    nx.draw_networkx_nodes(G, pos, node_size=100, node_color='skyblue')
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True)
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.axis('off')
    plt.title("A Network of 'Ultimately Bought' Items")
    plt.tight_layout()

    return fig



