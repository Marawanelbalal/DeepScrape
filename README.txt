DeepScrape
==========

DeepScrape is a comprehensive data acquisition and analysis tool for scraping eBay product listings based on user-defined queries.
Built with PyQt6, the application provides a graphical interface for both scraping and analyzing large volumes of eBay data.

🔧 Features
------------

- **Customizable Search**  
  Users can input a product query, set the number of items per request, and specify the total number of items to retrieve. For example, setting 50 items/request and 200 total will perform 4 sequential requests.
  The maximum recommended number of items per request is 200. 

- **.env Configuration**  
  The user must supply their own:
  - eBay API keys, essential for the application to work.
  - Optional: ExchangeRate API key (for multi-regional currency unification), Failure to provide this key will only lock out the multiregional heatmap option and will not impact other options.

- **Data Export**  
  After scraping, results can be exported as a CSV file.


🚀 Getting Started
1. Clone the repo: `git clone https://github.com/yourusername/DeepScrape.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Add your keys to a `.env` file (see instructions below)
4. Run the app: `python main.py`


How to get the required keys?
-----------------------------
For the eBay keys, sign up for the eBay developer's program: https://developer.ebay.com/signin?tab=register
After signing in, go to Application Keysets, on the right there are the required production keys.
The App ID is the Client ID, and Cert ID is the Client Secret, now place them in the .env file like this:
> EBAY_CLIENT_ID = your_client_ID
> EBAY_CLIENT_SECRET = your_client_secret

For the ExchangeRate API, sign up here: https://app.exchangerate-api.com/sign-up
Afterwards, an email will be sent to verify the account. Finally, the user will have access to the key.
Place it in the .env file like this:
> EXCHANGE_API_KEY = your_exchange_api_key

📊 Analysis Options
--------------------

- **Seller Influence Graph**  
  Built using NetworkX, this graph shows how sellers are connected to popular products.

- **Price Range & Feedback Distribution**  
  Visualized with heatmaps and bar charts using matplotlib and pandas.

- **KNN Clustering**  
  Clusters similar products and visualizes them on a 3D graph using scikit-learn.

- **Community Analysis**  
  Identifies and counts related product categories, visualized in chart form.

- **Product Network Graph**  
  Frequently bought together: Creates a network of items connected to their "Bought Together" items via an undirected graph.
  Customers Ultimately Bought: Creates a network of items connected to the items the customers ended up buying via a directed   graph.

- **Multiregional Heatmap**  
  Currency-normalized map across different regions (requires a Forex API key and geopandas).

- **Review Sentiment Analysis** *(optional)*  
  Uses Selenium to fetch and analyze review sentiments (longer runtime).

Notes
------

- Scraping or Analysis can occasionally fail; simply retry.
- Ensure ChromeDriver and Chrome versions match.
- Some analysis types (Review Sentiment and Product Network Graphs) take longer due to Selenium dependencies.
- No API rate limits or regional restrictions assumed.
- Most output is shown in the built-in terminal within the app — not in the IDE terminal.
- More details about each analysis type is provided inside the application.

Tech Stack
-----------

- **Frontend/UI**: PyQt6  
- **Data Handling**: pandas, matplotlib, scikit-learn, geopandas, NetworkX  
- **Scraping**: Selenium  
- **License**: MIT  
- **Dependencies**: Listed in requirements.txt
