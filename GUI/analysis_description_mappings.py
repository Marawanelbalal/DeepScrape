
description_map = {
"Seller Influence Analysis":
            "Description:\n\n\n"
            "Using the Networkx library, each item in the dataset is laid out "
            "and labeled by the name of its seller. Insights are extracted using "
            "the degree of any given seller node and the degree centrality. ",

"Product Network Graph":
            "Description:\n\n\n"
            "This analysis option uses selenium to find frequently "
            "bought together items for each item in the dataset and "
            "adds them to the dataset. For each item usually 5-15 items "
            "are found, so a 50 item dataset might increase to 200 items. "
            "An algorithm is used to link all the related items together, "
            "taking into consideration whether the scraped items exist "
            "in the dataset or not, or if they are connected to any other items. "
            "A Networkx graph is used to show the frequently bought together "
            "items, then insights are extracted using the betweenness centrality "
            "of each item. The higher the betweenness centrality, the higher the "
            "likelihood that this item is bought together with others. ",

"Review Sentiment Analysis":
            "Description:\n\n\n"
            "Using the beautifulsoup library, the top reviews are scraped "
            "for each item in the dataset (3-12). Then, the sentiment score "
            "of the item is found by getting the mean of sentiment scores of "
            "all its reviews. The sentiment score of each review is found using "
            "the rule-based VADER lexicon of the NLTK library. 5 other factors "
            "are scraped with each item:\n"
            "- Feedback Percentage\n"
            "- Accurate Description Score\n"
            "- Shipping Speed Score\n"
            "- Reasonable Shipping Cost Score\n"
            "- Communication Score\n\n"
            "All 6 of these factors are normalized on a scale of 0-5. The item "
            "is given a score from 0-5 using a formula that utilizes these 6 "
            "factors. Finally, a matplotlib bar chart is used to visualize the items "
            "and their ranks. ",

"Heatmap Analysis": {
            "Heatmap Showing Price Differences":
                "Description:\n\n\n"
                "(Opens browser): A figure made using the plotly library that shows the "
                "variability of prices and the count of each price range across the dataset "
                "with an interactive blocky heatmap",

            "Heatmap Showing Feedback Score Differences":
                "Description:\n\n\n"
                "(Opens browser): A figure made using the plotly library that shows the "
                "variability of feedback scores and the count of each score range across "
                "the dataset with an interactive blocky heatmap ",

            "Multi regional Heatmap Showing Price Differences":
                "Description:\n\n\n"
                "The number of items is split across 4 regions, United States, France, Germany, and "
                "Great Britain and a request is made to each region (e.g. 200 max items returns 50 from each region). "
                "Then, the average of the prices of each region is taken and used to represent it on a Yellow-Orange-Red "
                "heatmap of the world. The unused regions are crossed out."
            },

"Chart Analysis": {
            "Pie Chart Showing Price Differences":
                "Description:\n\n\n"
                "(Opens browser): A figure made using the plotly library that shows the "
                "variability of prices and the count of each price range "
                "across the dataset with an interactive pie chart",

            "Pie Chart Showing Feedback Score Differences":
                "Description:\n\n\n"
                "(Opens browser): A figure made using the plotly library that shows the "
                "variability of feedback scores and the count of each score range "
                "across the dataset with an interactive pie chart",

            "Bar Chart Showing Price Differences":
                "Description:\n\n\n"
                "(Opens browser): A figure made using the plotly library that shows the "
                "variability of prices and the count of each price range "
                "across the dataset with an interactive bar chart"
            },

"3D Graph Analysis":
            "Description:\n\n\n"
            "An interactive 3D scatterplot built with Matplotlib that visualizes each item based on its price, feedback percentage, and feedback score. "
            "The graph uses K-Nearest Neighbors (KNN) clustering to group the items into four distinct clusters, helping users identify patterns in product characteristics at a glance.",

"Chart Showing Communities (Related Categories)":
            "Description:\n\n\n"
            "To extract related categories, an algorithm is used to find which categories are repeated "
            "together the most. Related categories are put in one set called a community, and each community "
            "has a counter to track how many times it repeated, the higher the counter the higher the relation between "
            "the categories inside the community. The user has the option to specify a jaccard similarity threshold "
            ", all communities that are similar enough according to the threshold will be merged. Finally, a matplotlib "
            "bar chart is used to visualize communities and their count."
}

warning_map = {
    "Product Network Graph":"⚠️ <b>Warning:</b> Unlike other options, this option scrapes data with <code>selenium</code>, "
    "which is slow compared to other types of analysis, analysis on 50 product listings could take about 10 minutes..<br><br>"
    "You may choose to use a preloaded CSV with the <b>'Load CSV'</b> button, or press the "
    "<b>'Enable Scraping'</b> button and scrape live data<br><br>"
    "<br><br><br><br>Data about the preloaded CSV:"
    "<br><br>Query: Gaming Laptop<br><br>Max Number of Items: 100<br><br> Outputted items: 300",

    "Review Sentiment Analysis":"⚠️ <b>Warning:</b> Unlike other options, this option scrapes data with <code>selenium</code>, "
    "which is slow compared to other types of analysis, analysis on 50 product listings could take about 10 minutes..<br><br>"
    "You may choose to use a preloaded CSV with the <b>'Load CSV'</b> button, or press the "
    "<b>'Enable Scraping'</b> button and scrape live data<br><br>"
    "Data about the preloaded CSV:<br><br>Query: Gaming Laptop<br><br>Max Number of Items: 50<br><br>Outputted Ranked items: 45"

}
def get_description(text:str,inner_text="")->str:
    if inner_text:
        description = description_map.get(text).get(inner_text)
    else:
        description = description_map.get(text)
    description = description if isinstance(description,str) else "Choose an analysis type!"
    return description

def get_warning(text:str)->str: return warning_map[text]