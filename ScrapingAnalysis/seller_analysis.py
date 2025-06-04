from . import plt,nx

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

  degree_centrality = nx.degree_centrality(G)

  print("Degree Centrality:")
  for item,centrality in degree_centrality.items():
    print(f"{item}: {centrality}")
  components = list(nx.connected_components(G))
  print("Number of Connected Components:", len(components))

  for idx, component in enumerate(components,start=1):
    print(f"Component {idx}: {len(component)} products")
    print("-"*50)


  seller_product_counts = {seller: len(products) for seller, products in seller_products.items()}


  print("number of products for every seller:")
  for seller, count in seller_product_counts.items():
    print(f"{seller}: {count} products")
    print("-" * 50)

  plt.title("Relationships Between Products Sold by the Same Seller")
  return fig