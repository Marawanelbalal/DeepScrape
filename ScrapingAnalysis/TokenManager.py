#This token manager was made to make sure there is always a valid token while using get_item_data() from scraping_functions
#This means we don't have to reuse a token that might be expired, or make too many tokens.
from . import time,requests,base64
from common_imports import os,load_dotenv


class TokenManager:
    def __init__(self):
        load_dotenv()
        self.CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")
        self.token = None
        self.token_time = 0
        self.expiration = 7200  # eBay tokens usually last for 7200 seconds (2 hours)

    def get_token(self):
        if self.token is None or (time.time() - self.token_time) >= self.expiration:
            self.token = self.generate_token()
            self.token_time = time.time()
        return self.token

    def generate_token(self):
        if not self.CLIENT_ID or not self.CLIENT_SECRET:
            print("Missing eBay CLIENT_ID or CLIENT_SECRET.")
            return None

        credentials = f"{self.CLIENT_ID}:{self.CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        url = "https://api.ebay.com/identity/v1/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}"
        }
        body = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"
        }

        response = requests.post(url, headers=headers, data=body)

        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Token generation failed: {response.status_code} - {response.text}")
            return None