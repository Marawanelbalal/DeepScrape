import networkx as nx
import matplotlib.pyplot as plt
from .fbt_analysis import frequently_bought_together
from .scraping_functions import ebay_api


def bought_together_analysis(items:dict,access_token:str):
    df = frequently_bought_together(items,access_token)

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
                formatted_bought_id = f"v1|{bought_id}|0"
                if formatted_bought_id in item_id_map:
                    if not G.has_edge(numbered_items[source_id], numbered_items[formatted_bought_id]):
                        G.add_edge(numbered_items[source_id], numbered_items[formatted_bought_id])


    betweenness = nx.betweenness_centrality(G)

    sorted_centrality = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)


    print("Top 10 Nodes by Betweenness Centrality:")
    for item_num, centrality in sorted_centrality:
        node = [x for x in numbered_items.keys() if numbered_items[x] == item_num][0]
        print(f"{item_num}: {item_id_map.get(node, 'Unknown')} - Centrality: {centrality:.5f}")
        print("-" * 150)



    pos = nx.kamada_kawai_layout(G)

    fig = plt.figure()

    nx.draw(G,pos,with_labels = True)
    print(type(fig))
    return fig



