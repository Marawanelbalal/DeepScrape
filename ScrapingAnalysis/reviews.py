from . import pd #pandas
from . import json,requests,time,random,BeautifulSoup
from . import plt #pyplot
from . import By
import resources_rc
from common_imports import read_csv_from_qrc
from .scraping_functions import initialize_chromedriver


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
  #Rotate user agents and make a session to avoid rate limits
  headers = {
    "User-Agent":  random.choice(USER_AGENTS),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.ebay.com/",
  }

  session.headers.update(headers)


  try:
    soup = session.get(URL, timeout=10)
  except requests.exceptions.RequestException as e:
    print("Request failed: ", e)
    return [], None

  #In case of eBay blockage, sleep for a long time.
  if "Pardon Our Interruption" in soup.text or "automated access" in soup.text:
    print("Blocked by eBay. Received interruption page.\nSleeping for 10 minutes")
    time.sleep(600)
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
  #To stay in the safe zone, add random time limits between requests.
  delay = random.uniform(60, 120)
  print(f"Sleeping for: {delay} seconds")
  time.sleep(delay)
  return unique_reviews,(AD,RSC,SS,COMM)

def get_reviews_sel(URL: str)->list and tuple:
    web = initialize_chromedriver()

    try:
        web.get(URL)
        time.sleep(3)
    except Exception as e:
        print("Request failed: ", e)
        web.quit()
        return [], None

    if "Pardon Our Interruption" in web.page_source or "automated access" in web.page_source:
        print("Blocked by eBay. Received interruption page.\nSleeping for 10 minutes")
        web.quit()
        return [], None
    else:
        print("Successful scraping for item: ", URL)

    # Extract reviews
    reviews_elements = web.find_elements(By.XPATH, '//div[contains(@class, "fdbk-container__details__comment")]')
    reviews = [element.text for element in reviews_elements]

    seen = set()
    unique_reviews = []
    for rev in reviews:
        if rev not in seen:
            seen.add(rev)
            unique_reviews.append(rev)

    # Extract seller ratings
    AD, RSC, SS, COMM = None, None, None, None
    try:
        rating_elements = web.find_elements(By.XPATH, '//span[contains(@class, "fdbk-detail-seller-rating__value")]')
        if len(rating_elements) >= 4:
            AD = float(rating_elements[0].text)
            RSC = float(rating_elements[1].text)
            SS = float(rating_elements[2].text)
            COMM = float(rating_elements[3].text)
    except ValueError as e:
        print('Something went wrong collecting seller data:\n', e)

    # To stay in the safe zone, add random time limits between requests.
    web.quit()
    delay = random.uniform(1, 3)
    print(f"Sleeping for: {delay} seconds")
    time.sleep(delay)

    return unique_reviews,(AD,RSC,SS,COMM)


def reviews_worker(item):
  reviews = get_reviews_sel(item['Link'])
  item_name = item['Title']
  review_list = reviews[0]

  if reviews[1] is None:
    scores_tuple = (None, None, None, None, float(item['Feedback Percentage']))
  else:
    scores_tuple = reviews[1] + (float(item["Feedback Percentage"]),)
  return item_name,review_list,scores_tuple

def get_review_score(review):
  import nltk
  from nltk.sentiment.vader import SentimentIntensityAnalyzer
  review_analyzer = SentimentIntensityAnalyzer()
  #update the lexicon with some common phrases found
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
def calculate_item_score(S,FP,AD,SC,SS,C):
  return round( ( (3 * S) + (0.5 * FP) + (0.7 * AD) + (0.15 * SC) + (0.5 * SS) + (0.15 * C) ), 2)

def review_analysis(items:dict,csv_path = None):
    #If a CSV path is given, use it, otherwise try to scrape data live

    all_reviews = {}
    title_seller_map = {}
    title_score_map = {}
    final_score_map = {}
    title_rank_map = {}

    results = []
    if csv_path is not None:
        df = read_csv_from_qrc(csv_path)

        #Decode JSON strings back to their original forms
        df["review_list"] = df["review_list"].apply(json.loads)
        df["score_tuple"] = df["score_tuple"].apply(lambda x: tuple(json.loads(x)))

        #Reconstruct the original list of tuples
        results = list(zip(df["item_name"], df["review_list"], df["score_tuple"]))
        print("Loaded CSV!")
        print(results)

    else:
        for item in items.values():
            results.append(reviews_worker(item))
        #Convert complex data structures to JSON strings
        try:
            df = pd.DataFrame([
                {
                    "item_name": json.dumps(row[0]),  # str (safe but optional for strings)
                    "review_list": json.dumps(row[1]),
                    "score_tuple": json.dumps(row[2])
                }
                for row in results
            ])

            df.to_csv(r"C:\Users\Marawan\Documents\name_list_tuple_map.csv", index=False)
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

                AD = ratings[0]
                AD *= 0.2
                RSC = ratings[1]
                RSC *= 0.2
                SS = ratings[2]
                SS *= 0.2
                COMM = ratings[3]
                COMM *= 0.2
                FP = float(ratings[4])
                FP *= 0.01
                rank = calculate_item_score(final_score, FP, AD, RSC, SS, COMM)

                print(f'Accurate Description: {AD}\nReasonable shipping cost: {RSC}')
                print(f'Shipping speed: {SS}\nCommunication: {COMM}')
                print(f'Feedback Percentage: {FP}')
                print(f'Final score: {calculate_item_score(final_score, FP, AD, RSC, SS, COMM)}')

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

    return review_bar(title_rank_map)

def review_bar(title_rank_map:dict):

    titles = list(title_rank_map.keys())
    ranks = list(title_rank_map.values())

    fig = plt.figure(figsize=(10,6))
    plt.barh(titles,ranks,color ='lightgreen')
    plt.xlabel('Final Rank')
    plt.ylabel('Item Name')
    plt.title('Bar chart for items and their ranks.')
    plt.tight_layout()
    return fig

