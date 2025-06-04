from . import px,pd
#Plotly and Pandas


def price_heatmap(items:dict):

    products = list(items.values())
    df = pd.DataFrame(products)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df = df.dropna(subset=['Price'])
    max_price = df['Price'].max()
    bins = list(range(0, int(max_price) + 200, 200))
    print("Bins:", bins)
    df['PriceBin'] = pd.cut(df['Price'], bins=bins)
    freq = df['PriceBin'].value_counts().sort_index()
    print("\nPrice Distribution")
    print(freq)
    heatmap_data = pd.DataFrame([freq.values], columns=[str(interval) for interval in freq.index])
    custom_scale = [(0, "white"), (0.5, "red"), (1, "darkred")]
    fig = px.imshow(heatmap_data,
                    color_continuous_scale=custom_scale,
                    labels={'x': "Price Range", 'color': "Count"},
                    x=heatmap_data.columns,
                    y=[""])
    fig.update_layout(title="Heatmap of Price Distribution (Each $200 range)",
                      yaxis={"visible": False})
    return fig




def feedback_percentage_heatmap(items:dict):

    products = list(items.values())
    df = pd.DataFrame(products)
    df['Feedback Percentage'] = pd.to_numeric(df['Feedback Percentage'], errors='coerce')
    df.dropna(subset=['Feedback Percentage'], inplace=True)

    bins = list(range(0, 101, 1))
    labels = [f"{bins[i]}-{bins[i + 1]}%" for i in range(len(bins) - 1)]
    df['Feedback Range'] = pd.cut(df['Feedback Percentage'], bins=bins, labels=labels, include_lowest=True, right=False)
    range_counts = df['Feedback Range'].value_counts().sort_index()
    range_counts_df = range_counts.reset_index()
    range_counts_df.columns = ['Feedback Range', 'Count']
    range_counts_df = range_counts_df[range_counts_df['Count'] > 0]
    heatmap_data = pd.DataFrame([range_counts_df['Count'].values], columns=range_counts_df['Feedback Range'])
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Feedback % Range", color="Seller Count"),
        x=heatmap_data.columns,
        y=[""],
        color_continuous_scale="YlOrRd"
    )

    fig.update_layout(
        title="Heatmap of Seller Feedback Percentage Distribution",
        yaxis_visible=False,
        yaxis_showticklabels=False
    )

    return fig


