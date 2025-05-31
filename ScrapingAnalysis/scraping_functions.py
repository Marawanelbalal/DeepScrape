import base64

import pandas
import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium_stealth import stealth
from selenium.webdriver.support import expected_conditions as EC


import time
import re
import random
import networkx as nx
import matplotlib.pyplot as plt
import json



def get_item_data(item_id, access_token,region):
  #The browse api allows us to get item data using only the ID
  url = f"https://api.ebay.com/buy/browse/v1/item/v1|{item_id}|0"
  headers = {
    "Authorization": f"Bearer {access_token}",
    "X-EBAY-C-MARKETPLACE-ID": f"EBAY_{region}"
  }

  response = requests.get(url, headers=headers)

  if response.status_code == 200:
    result = response.json()
    shipping_options = result.get('shippingOptions', [])
    if shipping_options:
      shipping_cost = shipping_options[0].get('shippingCost', {}).get('value', 'N/A')
    else:
      shipping_cost = 'N/A'
    if shipping_options:
      shipping_cost = shipping_options[0].get('shippingCost', {}).get('value', 'N/A')

    price_value = result.get('price', {}).get('value', 'N/A')
    price_currency = result.get('price', {}).get('currency', 'N/A')
    condition = result.get('condition', 'N/A')

    item_data = {
      "Title": result.get("title", 'N/A'),
      "Item ID": result.get("itemId", 'N/A'),
      "Price": f"{price_value} {price_currency}",
      "Condition": condition,
      "Seller": result.get("seller", {}).get("username", 'N/A'),
      "Feedback Score": result.get("seller", {}).get("feedbackScore", 'N/A'),
      "Shipping Cost": shipping_cost,
      "Link": result.get("itemWebUrl", 'N/A'),
      "Buying Options": result.get("buyingOptions", []),
      "Also Bought": []
    }

    return item_data
  else:
    print(f"Error fetching item {item_id}: {response.status_code}")
    return None


def scrape_data(item_data,URL):
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.ebay.com/"
  }
  request = requests.get(URL,headers)
  if request.status_code == 200:
    soup = BeautifulSoup(request.content,'html5lib')
    price_primary = soup.find('div',class_="x-price-primary")
    price = price_primary.find('span',class_="ux-textspans")
    availability = soup.find('div',class_="x-quantity__availability",id = "qtyAvailability")
    availability_data = availability.find_all('span',class_="ux-textspans")
    discount = soup.find('span',class_="ux-textspans ux-textspans--EMPHASIS")
    if price:
      price = float(price.text.replace('/ea','').replace('US $', '').replace(' USD', '').strip())
    item_data['Price'] = price
    item_data['availability_data'] = [x.text for x in availability_data]
    if discount is not None:
      item_data['Discount'] = int(discount.text.replace('% off)', '').strip('()').strip())
    else:
      item_data['Discount'] = None

def extract_item_id(item_url):
  #use simple regular expression to get the item id from the url
  #because ebay follows a specified format for item id in url
  match = re.search(r"/itm/(\d+)", item_url)
  return match.group(1) if match else None


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




def seller_network(items):
  G = nx.Graph()

  seller_products = {}
  for item in items.values():
    seller = item["Seller"]
    item_title = item["Title"]

    if seller not in seller_products:
      seller_products[seller] = []

    seller_products[seller].append(item_title)

  for seller, products in seller_products.items():
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
  print("Degree Centrality:", degree_centrality)
  components = list(nx.connected_components(G) )
  print("Number of Connected Components:", len(components))

  for idx, component in enumerate(components):
    print(f"Component {idx + 1}: {len(component)} products")
    print("-"*50)


  seller_product_counts = {seller: len(products) for seller, products in seller_products.items()}


  print("number of products for every seller:")
  for seller, count in seller_product_counts.items():
    print(f"{seller}: {count} products")
    print("-" * 50)

  plt.title("Relationships Between Products Sold by the Same Seller")
  return fig

def safe_load(val):
  # function to avoid an error when loading json strings
  if isinstance(val, str) and val.strip():
    try:
      return json.loads(val)  # Reconvert JSON string into (list,tuple or dict)
    except json.JSONDecodeError:
      return []
  return []


def ebay_api(query: str,res_num: int,maximum: int,progress_callback=None)->dict and str:
  # Put the client ID and client secret as variables
  Client_ID = "MarawanE-DeepScra-PRD-e8c4184bf-8925ec1a"
  Client_Secret = "PRD-8c4184bf3a60-67a9-457c-9b81-caf6"

  #encode the credentials as "Client_ID:Client_Secret" in Base64
  #this is the proper format for converting both those credentials into Base64
  credentials = f"{Client_ID}:{Client_Secret}"
  encoded_credentials = base64.b64encode(credentials.encode()).decode()
  #credentials are encoded in Base64 to be sent with the request

  URL = "https://api.ebay.com/identity/v1/oauth2/token" #production endpoint

  headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {encoded_credentials}"
  }
  body = {
    "grant_type": "client_credentials",
    "scope": "https://api.ebay.com/oauth/api_scope"
  }

  response = requests.post(URL, headers=headers, data=body)

  access_granted = False
  if response.status_code == 200:  # 200 means accepted.
    access_token = response.json().get("access_token")
    # .json() turns the returned json format data into a python dictionary
    # now we get the access token using .json().get

    print("Access Token:", access_token)

    search = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    items = {}



    #attach headers to the request that include the access_token
    headers = {
      "Authorization": f"Bearer {access_token}",  #pass our token here
      "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"  #apply the default as united states
    }

    offset = 0
    while len(items) < maximum:
      if offset >= maximum:
        break
      params = {
        "q": query,
        "limit": res_num,
        "offset": offset
        #the offset is the number of the item from which the API starts to get its items
        #the offset parameter is used for pagination, allowing the user to scrape thousands of items
      }
      response = requests.get(search, params=params, headers=headers)
      if response.status_code == 200:
        results = response.json().get('itemSummaries',{})
        # itemSummaries is the key which contains the values needed for the project

        if results:

          for result in results:

            if len(items) >= maximum or offset >= maximum:
              break
            image = result.get('im')
            shipping_options = result.get('shippingOptions',
                                          [])  # Return an empty list if shippingOptions not found, instead of key error.
            if shipping_options:  # This is because sometimes items don't have shipping options
              # and cause an error that stops the program

              shipping_cost = shipping_options[0].get('shippingCost', {}).get('value', 'N/A')
            else:
              shipping_cost = 'N/A'

            #take only the specific data we need from itemSummaries and append it into our own dictionary
            #scraping real world data can get messy so this is why it is necessary to add heavy error detection
            #using the get function
            if result['itemId'] not in items:
              item_data = {
                'Title': result.get('title', ""),
                'Item ID': result.get('itemId', ""),
                'Price': result.get('price', {}).get('value', ''),
                'Link': result.get('itemWebUrl', ''),
                'Buying Options': result.get('buyingOptions', ''),
                'Shipping Cost': shipping_cost,
                'Also Bought' : []
              }
              image_data = result.get('image',{})
              img_URL = image_data.get('imageUrl',"")
              item_data.update({"Image":img_URL})

              seller = result.get('seller', {})
              item_data.update({
                'Seller': seller.get('username', ''),
                'Feedback Score': seller.get('feedbackScore', ''),
                'Feedback Percentage': seller.get('feedbackPercentage', ''),
              })

              categories = result.get('categories', [])
              item_data['Category'] = [(category.get('categoryName', ''), category.get('categoryId', '')) for category in
                                       categories]

              items[result['itemId']] = item_data
              if progress_callback:
                progress_callback(len(items))
        else:
          print("No items found using this query!")
      offset += res_num
      print(offset)
    return items,access_token
  else:
    print("Error obtaining token:", response.status_code, response.text)  #anticipating any errors
def get_reviews(URL:str)->list and tuple:
  USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/116.0",
  ]
  session = requests.Session()
  headers = {
    "User-Agent":  random.choice(USER_AGENTS),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.ebay.com/",
  }

  session.headers.update(headers)
  time.sleep(random.uniform(12, 17))

  try:
    soup = session.get(URL, timeout=10)
  except requests.exceptions.RequestException as e:
    print("Request failed: ", e)
    return [], None

  if "Pardon Our Interruption" in soup.text or "automated access" in soup.text:
    print("Blocked by eBay. Received interruption page.")
    return [], None
  else:
    print("Successful scraping for item: ",URL)

  site = BeautifulSoup(soup.content, 'html5lib')

  R = site.find_all('div', class_="fdbk-container__details__comment")
  seller_rating_values = site.find_all('span',class_ = 'fdbk-detail-seller-rating__value')

  AD,RSC,SS,COMM = None,None,None,None

  if seller_rating_values:

    try:

      AD = float(seller_rating_values[0].text)
      RSC = float(seller_rating_values[1].text)
      SS = float(seller_rating_values[2].text)
      COMM = float(seller_rating_values[3].text)

    except ValueError as e:

      print('Something went wrong collecting seller data:\n',e)

  reviews = [review.text for review in R]

  seen = set()
  unique_reviews = []
  for rev in reviews:
    if rev not in seen:
      seen.add(rev)
      unique_reviews.append(rev)
  return unique_reviews,(AD,RSC,SS,COMM)



def reviews_worker(item):
  reviews = get_reviews(item['Link'])
  item_name = item['Title']
  review_list = reviews[0]
  print(type(reviews[0]))
  print(type(reviews[1]))
  print(type(reviews))
  if reviews[1] is None:
    scores_tuple = (None, None, None, None, float(item['Feedback Percentage']))
  else:
    scores_tuple = reviews[1] + (float(item['Feedback Percentage']),)
  return item_name,review_list,scores_tuple

def get_review_score(review):
  import nltk
  from nltk.sentiment.vader import SentimentIntensityAnalyzer
  review_analyzer = SentimentIntensityAnalyzer()
  #update the lexicon with some phrases found
  review_analyzer.lexicon.update({
    "smaller than I expected": -1.5,
    "so far so good": 1.5,
    "no problems": 1.0,
    "Exactly as advertised": 1.0,
    "Fast shipping": 1.0,
    "Would do business again": 1.0
  })
  vader_score = review_analyzer.polarity_scores(review)
  return vader_score


#this function is used in item rank in reviews.py
def marwan_score(S,FP,AD,SC,SS,C):
  return round( ( (3 * S) + (0.5 * FP) + (0.7 * AD) + (0.15 * SC) + (0.5 * SS) + (0.15 * C) ), 2)