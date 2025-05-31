import pandas as pd
import plotly.express as px

def price_range_pie_chart(items:dict):

    products = list(items.values())
    df = pd.DataFrame(products)
    print(df.head())
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df.dropna(subset=['Price'], inplace=True)
    max_price = df['Price'].max()
    bins = list(range(0, int(max_price) + 200, 200))
    labels = [f"{bins[i]}-{bins[i + 1]}" for i in range(len(bins) - 1)]
    df['Price Range'] = pd.cut(df['Price'], bins=bins, labels=labels, include_lowest=True, right=False)
    range_counts = df['Price Range'].value_counts().sort_index()
    range_counts_df = range_counts.reset_index()
    range_counts_df.columns = ['Price Range', 'Count']
    print("\nPrice Distribution:")
    print(range_counts_df)
    range_counts_df = range_counts_df[range_counts_df['Count'] > 0]
    fig = px.pie(
        range_counts_df,
        names='Price Range',
        values='Count',
        title="Product Price Distribution with $200 Interval"
    )
    fig.update_traces(
        textinfo='percent',
        textposition='outside',
        textfont_size=14,
        textfont_color='black'
    )
    fig.update_layout(
        showlegend=True,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    return fig



def feedback_percentage_pie_chart(items:dict):

    products = list(items.values())
    df = pd.DataFrame(products)
    df['Feedback Percentage'] = pd.to_numeric(df['Feedback Percentage'], errors='coerce')
    df.dropna(subset=['Feedback Percentage'], inplace=True)
    bins = list(range(0, 101 + 1, 1))
    labels = [f"{bins[i]}-{bins[i + 1]}%" for i in range(len(bins) - 1)]
    df['Feedback Range'] = pd.cut(df['Feedback Percentage'], bins=bins, labels=labels, include_lowest=True, right=False)
    range_counts = df['Feedback Range'].value_counts().sort_index()
    range_counts_df = range_counts.reset_index()
    range_counts_df.columns = ['Feedback Range', 'Count']
    print("\nFeedback Percentage Distribution:")
    print(range_counts_df.to_string(index=False))
    range_counts_df = range_counts_df[range_counts_df['Count'] > 0]
    fig = px.pie(
        range_counts_df,
        names='Feedback Range',
        values='Count',
        title="Seller Feedback Percentage Distribution (1% Intervals)"
    )
    fig.update_traces(
        textinfo='percent',
        textposition='outside',
        textfont_size=14,
        textfont_color='black'
    )
    fig.update_layout(
        showlegend=True,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    return fig



def price_range_chart(items:dict):

    products = list(items.values())
    df = pd.DataFrame(products)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df = df.dropna(subset=['Price'])
    max_price = df['Price'].max()
    bins = list(range(0, int(max_price) + 200, 200))
    labels = [f"{bins[i]}-{bins[i + 1]}" for i in range(len(bins) - 1)]
    df['Price Range'] = pd.cut(df['Price'], bins=bins, labels=labels, include_lowest=True, right=False)
    range_counts = df['Price Range'].value_counts().sort_index()
    print(range_counts)
    range_counts_df = range_counts.reset_index()
    range_counts_df.columns = ['Price Range', 'Count']
    fig = px.bar(range_counts_df, x='Price Range', y='Count',
                 title="Price Distribution with $200 Interval",
                 labels={'Price Range': 'Price Range($)', 'Count': 'Products Count'},
                 text='Count')
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    return fig
#
# if __name__ == "__main__":
#     choice = input('Would you like to view a pie/bar chart by price or feedback percentage? (P/FP)')
#     if choice.upper() == "P":
#         choice = input('Would you like to view a bar chart or a pie chart? (B/P)')
#         if choice.upper() == "B":
#             price_range_chart()
#         elif choice.upper() == "P":
#             price_range_pie_chart()
#     elif choice.upper() == "FP":
#         feedback_percentage_pie_chart()
#     else:
#         print('Not a valid choice!')

