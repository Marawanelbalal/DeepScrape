from . import nx #Networkx
from . import webdriver,By,Options,stealth #Selenium imports
from . import plt #Pyplot
from . import pd #Pandas
from . import time,random,copy
from .scraping_functions import get_item_data,extract_item_id


def customers_also_bought(URL,XPATH):
    options = Options()
    options.add_argument("--headless")  #run in headless mode (no browser will open)
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--disable-features=SharedStorageWorklet")
    #some of the extra arguments are not always helpful, but including them doesn't hurt.

    prefs = {
      "profile.default_content_setting_values": {
        "images": 2,
        "notifications": 2,
        "geolocation": 2,
        "javascript": 1,
      }
    }
    options.add_experimental_option("prefs", prefs)
    web = webdriver.Chrome(options = options)
    stealth(web,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    web.get(URL)
    content = web.page_source[:1000]
    if "Pardon Our Interruption" in content or "automated access" in content:
      print("Blocked by eBay. Received interruption page.")
      return []
    # wait = WebDriverWait(web, 15)
    # also_bought = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'GvB_')]")))
    time.sleep(random.uniform(2, 5))
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

def frequently_bought_together(items:dict,access_token)->pd.DataFrame:

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



