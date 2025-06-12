from . import plt,nx
from .scraping_functions import show_graph_summary


def seller_network(items):

  G = nx.Graph()

  seller_products = {}
  #Create a node for each item based on their seller
  for item in items.values():
    seller = item["Seller"]
    item_title = item["Title"]

    if seller not in seller_products:
      seller_products[seller] = []

    seller_products[seller].append(item_title)

  for seller, products in seller_products.items():
    #Connect nodes (items) if they have the same seller
    for i in range(len(products)):
      G.add_node(products[i], label=f"({seller})")
      for j in range(i + 1, len(products)):
        G.add_edge(products[i], products[j], relation="Same Seller")

  fig = plt.figure(figsize=(16, 12))
  pos = nx.kamada_kawai_layout(G)

  nx.draw(G, pos, with_labels=False, node_color="lightblue", edge_color="gray", node_size=150)

  labels = {node: G.nodes[node]['label'] for node in G.nodes}
  nx.draw_networkx_labels(G, pos, labels, font_size=6, font_color='black',
                          bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

  show_graph_summary(G)

  degree_centrality = nx.degree_centrality(G)
  sorted_centrality = dict(sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True))

  # Reverse map from product title to seller
  product_to_seller = {
    product: seller
    for seller, products in seller_products.items()
    for product in products
  }

  print("\tDegree Centrality:")
  for item,centrality in sorted_centrality.items():
    if centrality != 0:
      print("-" * 50)
      print(f"{item}: {centrality}, Seller: {product_to_seller[item]}")
  print("-" * 50)

  seller_product_counts = {seller: len(products) for seller, products in seller_products.items()}
  seller_product_counts = dict(sorted(seller_product_counts.items(), key=lambda x: x[1], reverse=True))

  print("Sorted number of products for every seller:")
  for seller, count in seller_product_counts.items():
    print(f"{seller}: {count} products")
    print("-" * 50)

  plt.title("Relationships Between Products Sold by the Same Seller")
  return fig