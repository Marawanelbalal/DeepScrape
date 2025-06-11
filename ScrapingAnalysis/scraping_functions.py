from . import base64,time

from common_imports import re
from . import json,requests,BeautifulSoup
from common_imports import os,load_dotenv

from . import By,Options,uc #Selenium imports


def get_item_data(item_id,access_token,region):


  url = f"https://api.ebay.com/buy/browse/v1/item/{item_id}"
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
  load_dotenv()
  try:
    Client_ID = os.getenv("EBAY_CLIENT_ID")
    Client_Secret = os.getenv("EBAY_CLIENT_SECRET")
  except Exception as e:
    print("Invalid Client ID or Client Secret Keys\n",e)
    return

  #encode the credentials as "Client_ID:Client_Secret" in Base64
  #this is the proper format for converting both those credentials into Base64
  if Client_ID is None or Client_Secret is None:
    print("Invalid Client ID or Client Secret")
    return {},""

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

    print("Access Token created\nScraping items...")

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
          print("No items were found using this query!")
      offset += res_num
      print(offset)
    print(f"{len(items)} obtained!")
    return items,access_token
  else:
    print("Error scraping items:", response.status_code, response.text)  #anticipating any errors

def initialize_chromedriver():
  options = Options()
  options.add_argument("--headless")  # run in headless mode (no browser will open)
  options.add_argument("--disable-gpu")
  options.add_argument("--disable-extensions")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--blink-settings=imagesEnabled=false")
  options.add_argument("--disable-features=SharedStorageWorklet")
  # some of the extra arguments are not always helpful, but including them doesn't hurt.

  web = uc.Chrome(options=options)
  web.set_window_size(1366, 768)

  return web
