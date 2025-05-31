from concurrent.futures import ThreadPoolExecutor
from .scraping_functions import reviews_worker, get_review_score, marwan_score
import pandas as pd
import json


def review_analysis(items:dict,csv_path = None):


    all_reviews = {}
    title_seller_map = {}
    title_score_map = {}
    final_score_map = {}
    title_rank_map = {}

    results = []
    if csv_path is not None:
        df = pd.read_csv(csv_path)

        # Decode JSON strings
        df["item_name"] = df["item_name"].apply(json.loads)
        df["review_list"] = df["review_list"].apply(json.loads)
        df["score_tuple"] = df["score_tuple"].apply(lambda x: tuple(json.loads(x)))

        # Reconstruct the original list of tuples
        results = list(zip(df["item_name"], df["review_list"], df["score_tuple"]))
        print("Loaded CSV!")
        print(results)
        try:
            print("Top level type: ",type(results))
            print("1st element: ",type(results[0]))
            print("1st inner 1st element: ", type(results[0][0]))
            print("2nd inner 1st element: ", type(results[0][1]))
            print("3rd inner 1st element: ", type(results[0][2]))
        except Exception as e:
            print("Couldn't print: ",e)
    else:
        for item in items.values():
            results.append(reviews_worker(item))
        try:
            print("Top level type: ",type(results))
            print("1st element: ",type(results[0]))
            print("1st inner 1st element: ", type(results[0][0]))
            print("2nd inner 1st element: ", type(results[0][1]))
            print("3rd inner 1st element: ", type(results[0][2]))
        except Exception as e:
            print("Couldn't print: ",e)
        # Convert complex types to JSON strings
        try:
            df = pd.DataFrame([
                {
                    "item_name": json.dumps(row[0]),  # str (safe but optional for strings)
                    "review_list": json.dumps(row[1]),
                    "score_tuple": json.dumps(row[2])
                }
                for row in results
            ])

            df.to_csv(r"C:\Users\maraw\Documents\name_list_tuple_map.csv", index=False)
            print("Saved to csv!")
        except Exception as e:
            print("Couldn't save to csv",e)

    for title,reviews,seller_data in results:
        all_reviews[title] = reviews
        title_seller_map[title] = seller_data

    for title, reviews in all_reviews.items():

        print(title, ":\n")

        for review in reviews:
            print(review)
            cut_off = review.find('Reply from: ')
            if cut_off != -1:
                review = review[:cut_off]
            print('-' * 50)
        print('-' * 100)

    for title, reviews in all_reviews.items():
        scores = [get_review_score(review) for review in reviews]
        if scores:
            score_sum = sum([score['compound'] for score in scores])
            final_score = score_sum / len(scores)
            title_score_map[title] = scores
            final_score_map[title] = final_score
        else:
            title_score_map[title] = None
            final_score_map[title] = None

    for title, scores in title_score_map.items():

        print(title, ":\n")

        if scores is not None:

            final_score = final_score_map[title]
            print(f'The final score is: {final_score}')
            print(f'Additional seller data:')

            ratings = title_seller_map[title]
            if ratings[0] is not None:
                FP = float([item['Feedback Percentage'] for item in items.values() if item['Title'] == title][0])
                FP *= 0.01
                AD = ratings[0]
                AD *= 0.2
                RSC = ratings[1]
                RSC *= 0.2
                SS = ratings[2]
                SS *= 0.2
                COMM = ratings[3]
                COMM *= 0.2
                rank = marwan_score(final_score, FP, AD, RSC, SS, COMM)

                print(f'Accurate Description: {AD}\nReasonable shipping cost: {RSC}')
                print(f'Shipping speed: {SS}\nCommunication: {COMM}')
                print(f'Feedback Percentage: {FP}')
                print(f'Final score: {marwan_score(final_score, FP, AD, RSC, SS, COMM)}')

                title_rank_map[title] = rank

            else:
                print('No ratings data available: Using scaled up sentiment...')
                title_rank_map[title] = final_score * 5
        else:
            print('No score data available.')
            title_rank_map[title] = 0.0

        print('-' * 100)

    sorted_ranks = sorted(title_rank_map.items(), key=lambda x: x[1], reverse=True)
    print('Items sorted by rank:\n\n')
    for item in sorted_ranks:
        print(f'For item: {item[0]}\nFinal rank: {item[1]}\n')

    return title_rank_map

def review_bar(items:dict):
    title_rank_map = review_analysis(items)
    #r"C:\Users\maraw\Documents\name_list_tuple_map.csv"
    import matplotlib.pyplot as plt

    titles = list(title_rank_map.keys())
    ranks = list(title_rank_map.values())

    fig = plt.figure(figsize=(10,6))
    plt.barh(titles,ranks,color ='lightgreen')
    plt.xlabel('Final Rank')
    plt.ylabel('Item Name')
    plt.title('Bar chart for items and their ranks.')
    plt.tight_layout()
    return fig

