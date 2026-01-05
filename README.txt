# DeepScrape

DeepScrape is a data acquisition and analysis tool for scraping eBay product listings based on
user-defined queries. Built with PyQt6, the application provides a graphical interface for both
scraping and analyzing large volumes of eBay data.

---

## Features

### Customizable Search
Users can input a product query, set the number of items per request, and specify the total number
of items to retrieve.  
For example, setting 50 items per request and 200 total items will perform 4 sequential requests.
---

### `.env` Configuration
The user must supply their own API keys:

- eBay API keys (required for the application to function)
- ExchangeRate API key (optional, used for multi-regional currency unification)

The ExchangeRate API key will only enable the multiregional heatmap option and
is not necessary for other analysis features.

---

### Data Export
After scraping, results can be exported as a CSV file containing structured data such as:
- Item titles
- Seller names and ratings
- Prices and shipping costs
- Categories and additional metadata

---

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DeepScrape.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your API keys to a `.env` file (see below)
4. Run the application:
   ```bash
   python main.py
   ```

---

## How to Get the Required API Keys

### eBay API
Sign up for the eBay Developer Program:  
https://developer.ebay.com/signin?tab=register

After signing in, navigate to **Application Keysets** and use the production keys for real market data.
The App ID corresponds to the Client ID, and the Cert ID corresponds to the Client Secret.

Add them to the `.env` file as follows:
```env
EBAY_CLIENT_ID=your_client_id
EBAY_CLIENT_SECRET=your_client_secret
```

---

### ExchangeRate API (Optional)
Sign up at:  
https://app.exchangerate-api.com/sign-up

After verifying your account, add the key to the `.env` file:
```env
EXCHANGE_API_KEY=your_exchange_api_key
```

---

## Some of the analysis options

### Seller Network Graph
Each item is associated with its seller, and items belonging to the same seller are connected.
Sellers are ranked using degree-based centrality measures to show seller frequency and influence.

---

### Price Range and Feedback Distributions
Heatmaps and bar charts displaying price ranges and feedback score distributions,
implemented using pandas and matplotlib. Useful for market analysis.

---

### 3D Clustering
Each item is represented in a three-dimensional feature space consisting of:
- Price
- Seller feedback score
- Feedback percentage

All features are normalized and clustered using KNN.
This visualization is primarily exploratory and intended to highlight rough groupings.

---

### Product Network Graphs

**Frequently Bought Together**  
An undirected graph connecting items that are frequently purchased together.

**Customers Ultimately Bought**  
A directed graph modeling customer transitions from viewed items to purchased items.

Centrality measures such as betweenness, in-degree, out-degree, PageRank, and degree centrality
are used to extract insights from these networks.

---

### Multiregional Heatmap
A currency normalized heatmap showing average item prices across different eBay regions.
This feature requires both an ExchangeRate API key and geopandas for a clean looking world map with a heatmap overlay.

---

### Review Sentiment Analysis (Optional)
Uses Selenium to navigate product pages, collect reviews, and compute sentiment scores using VADER.
Scores are aggregated and normalized to produce a final item score.

This option has a longer runtime due to browser automation, and is not guaranteed to work all the time.

---

### Community Analysis
Analyzes how often product categories appear together across listings.
Frequently co-occurring categories are treated as communities.

Users can apply a Jaccard similarity threshold to merge similar communities.

---

## Notes

- Scraping or analysis may occasionally fail; retrying usually resolves the issue.
- Ensure Chrome and ChromeDriver versions match.
- Selenium-based analysis options have longer runtimes and are not guaranteed to work.
- Standard output and errors are displayed in the built-in terminal inside the application. There is no need to switch to the IDE.
- More detailed explanations of each analysis option are provided within the app.

---

## Tech Stack

- Frontend / UI: PyQt6
- Data Processing: pandas
- Visualization: matplotlib, geopandas
- Machine Learning: scikit-learn
- Graph Analysis: NetworkX
- Scraping: Selenium
- License: MIT
- Dependencies: listed in `requirements.txt`
