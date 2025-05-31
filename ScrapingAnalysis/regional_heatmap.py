import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
#-------------------------------------------------------------------------------------------------
def ebay_api_multi_region(query,total_items):
    import requests
    import base64

    CLIENT_ID = "MarawanE-DeepScra-PRD-e8c4184bf-8925ec1a"
    CLIENT_SECRET = "PRD-8c4184bf3a60-67a9-457c-9b81-caf6"
    EXCHANGE_API_KEY = "7b58c7c5f80600ead0081243"

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    token_url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    body = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    response = requests.post(token_url, headers=headers, data=body)
    if response.status_code != 200:
        print("Error getting token:", response.text)
        return {}

    access_token = response.json().get("access_token")
    regions = ["EBAY_US", "EBAY_GB", "EBAY_DE", "EBAY_FR"]

    per_region = total_items // len(regions)

    all_prices = {}
    currencies_needed = set()

    for region in regions:
        print(f"\n Getting from region: {region}")
        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-EBAY-C-MARKETPLACE-ID": region
        }

        offset = 0
        region_count = 0

        while region_count < per_region:
            params = {
                "q": query,
                "limit": min(50, per_region - region_count),
                "offset": offset
            }

            res = requests.get(url, headers=headers, params=params)
            if res.status_code != 200:
                print(f"Error fetching from {region}: {res.status_code}")
                break

            results = res.json().get('itemSummaries', [])
            if not results:
                break

            for result in results:
                item_id = result.get('itemId', 'N/A')
                price_info = result.get('price', {})

                if price_info.get('value') is not None and price_info.get('currency') is not None:
                    original_currency = price_info['currency']
                    original_price = price_info['value']

                    all_prices[item_id] = {
                        'Original_Price': original_price,
                        'Original_Currency': original_currency,
                        'Region': region
                    }
                    currencies_needed.add(original_currency)
                    region_count += 1

                if region_count >= per_region:
                    break

            offset += len(results)


    print("\nConverting currencies to USD...")
    exchange_rates = {}

    for currency in currencies_needed:
        if currency == "USD":
            exchange_rates[currency] = 1.0
        else:
            url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{currency}/USD"
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                rate = data.get("conversion_rate", 1.0)
                exchange_rates[currency] = rate
            else:
                print(f"Failed to get exchange rate for {currency}, defaulting to 1.0")
                exchange_rates[currency] = 1.0

    for item_id, data in all_prices.items():
        currency = data['Original_Currency']
        value = data['Original_Price']
        usd_value = round(float(value) * exchange_rates.get(currency, 1.0), 2)

        all_prices[item_id]['USD_Price'] = usd_value
    return all_prices


def calculate_average_prices(all_prices_data):
    region_prices = {}

    for item_id, info in all_prices_data.items():
        region = info.get("Region", None)
        if region is None:
            continue

        usd_price = info.get("USD_Price", 0)

        if region not in region_prices:
            region_prices[region] = []

        region_prices[region].append(usd_price)
    averages = {}
    for region, prices in region_prices.items():
        if prices:
            avg = round(sum(prices) / len(prices), 2)
            averages[region] = avg
        else:
            averages[region] = 0.0
    return averages


def regional_price_heatmap(query,total_items):
    all_data = ebay_api_multi_region(query,total_items)
    print(f"All data: {all_data}")
    average_prices_by_region = calculate_average_prices(all_data)
    world = gpd.read_file(
        "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
    )
    world["NAME"] = world["NAME"].str.strip()

    region_country_map = {
        "EBAY_US": "United States of America",
        "EBAY_GB": "United Kingdom",
        "EBAY_DE": "Germany",
        "EBAY_FR": "France"
    }

    data = []
    for region_code, avg_price in average_prices_by_region.items():
        country_name = region_country_map.get(region_code)
        if country_name:
            data.append({"country": country_name, "avg_price": avg_price})

    avg_df = pd.DataFrame(data)
    merged = world.merge(avg_df, how="left", left_on="NAME", right_on="country")

    print("Countries with matched average prices:")
    print(merged[~merged["avg_price"].isna()][["NAME", "avg_price"]].reset_index(drop=True))

    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')

    merged.plot(
        column='avg_price',
        cmap='YlOrRd',
        linewidth=0.8,
        ax=ax,
        edgecolor='0.8',
        missing_kwds={
            "color": "black",
            "edgecolor": "white",
            "hatch": "///x",
            "label": "No Data"
        }
    )


    ax.set_title(
        " Average Product Prices in USD by Country (eBay Markets)",
        fontdict={"fontsize": 18, "fontweight": "bold"},
        pad=20
    )

    cmap = plt.cm.YlOrRd
    norm = mpl.colors.Normalize(vmin=merged['avg_price'].min(), vmax=merged['avg_price'].max())
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label('Average Price', color='white')
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
    ax.set_axis_off()

    plt.tight_layout()
    return fig
