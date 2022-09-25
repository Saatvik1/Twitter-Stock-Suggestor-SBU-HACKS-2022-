# -*- coding: utf-8 -*-
from io import StringIO
import tweepy
from datetime import date
import yfinance as yf
import demoji
from threading import *

# auth = tweepy.OAuth1UserHandler(
#   consumer_key = 'UsdF3pJdZirVrDAFyq8UhCI24', consumer_secret = 'Iqi0oiDEqeZF3ro3LBdFMrBD75DKDajCmmtYEsb9RxH4zQOg7M'#, access_token, access_token_secret
# )
auth = tweepy.OAuth2BearerHandler(
    "AAAAAAAAAAAAAAAAAAAAAKSvhQEAAAAAZvFe76BXfNl3Ln4sbLJMavC5Mcw%3DQEKUSqvrrKsK8QMjS5BXjyteBv03Y7qyeQf2Ri4YvDagihfhuW"
)

api = tweepy.API(auth)

# print(api.available_trends())
# api = tweepy.API(auth)
client = tweepy.Client(
    consumer_key="3PLSvoemDuzyF6WYgXt0ZH0Mm",
    consumer_secret="eY6439bv30Qce9GG9kg3FUinIIXD9BMdClZTe4nH8BHeyqZ4mv",
    access_token="1573499265543979019-GQGPsr8uIDvIPvVG0sPxuPR5JVL03X",
    access_token_secret="6FfmKf76t2F5epc2aSRDM1JFUSIUjgSKLYJXEnXuRx3E0",
    bearer_token="AAAAAAAAAAAAAAAAAAAAAKSvhQEAAAAAZvFe76BXfNl3Ln4sbLJMavC5Mcw%3DQEKUSqvrrKsK8QMjS5BXjyteBv03Y7qyeQf2Ri4YvDagihfhuW",
)

response_template = {"tweets": [], "ticker": "", "date_updated": ""}
tweet_template = {"text": "", "id": ""}

# Maybe also consider the companies and also account for it in the calculation.


def isEnglish(s):
    try:
        s.encode(encoding="utf-8").decode("ascii")
    except UnicodeDecodeError:
        return False
    else:
        return True


def removeStringDiscrepancies(sentence):
    if "-" in sentence:
        sentence = sentence.replace("-", " down ")
    if "+" in sentence:
        sentence = sentence.replace("+", " up ")
    if '"' in sentence:
        sentence = sentence.replace('"', "")
    if "'" in sentence:
        sentence = sentence.replace("'", "")
    return sentence


tweet_jsons = []


class tweet_jsons_tracker:
    def __init__(self):
        self.tweet_jsons = []


class getTweets(Thread):
    def __init__(self, ticker, tweet_count, tweet_jsons):
        super(getTweets, self).__init__()
        self.ticker = ticker
        self.tweet_count = tweet_count
        self.tweet_jsons = tweet_jsons

    def getTweetTexts(self):
        ticker = self.ticker
        tweet_count = self.tweet_count
        tweet_jsons = self.tweet_jsons
        yf_ticker = yf.Ticker(ticker)
        company_name = yf_ticker.info["longName"]

        print(ticker)

        # Last 7 days of tweets
        tweets = api.search_tweets(
            q="$" + ticker,
            result_type="mixed",
            count=tweet_count,
            tweet_mode="extended",
        )

        # Add both restults and use a set to remove intersectional tweets.

        response = response_template.copy()

        response["date_updated"] = str(date.today())
        response["ticker"] = ticker
        response["company"] = company_name

        if len(tweets) > 0:
            for tweet in tweets:
                # string = StringIO(tweet.full_text)
                tweet_body = tweet_template.copy()

                lines = tweet.full_text.split("\n")
                new_text = ""
                for line in lines:
                    for sentence in line.split(". "):

                        # replace emojis with text to allow machine learning model to work properly
                        emojis_found = demoji.findall(sentence)
                        for emoji in emojis_found:
                            sentence = sentence.replace(emoji, emojis_found[emoji])

                        # Check if its english, if not, skip
                        if not isEnglish(sentence):
                            continue

                        # Try to isolate the text about the ticker and avoid text about other tickers.
                        # Also avoids links
                        if (
                            ("$" + ticker).lower() in sentence.lower()
                        ) or True:  # Removed this, so just set to true. leaaving just in case
                            # ("$" in sentence) and ("https://" not in sentence)

                            # Make it so that the model can handle + and - values.
                            # Clean up string

                            sentence = removeStringDiscrepancies(sentence)

                            new_text += sentence
                            new_text += " "
                ###

                tweet_body["text"] = new_text
                # tweet_body["text"] = tweet.full_text
                tweet_body["id"] = tweet.id
                response["tweets"].append(tweet_body)
                # print(response)
        else:
            response["tweets"] = "N/A"
        tweet_jsons.tweet_jsons.append(response)

    def run(self):
        self.getTweetTexts()


# test = set(joe + bruh)
# print(test)
# print(StringIO(getTweetTexts("$GME")["tweets"][4]["text"]).getvalue())


# msft = yf.Ticker("MSFT")

# company_name = msft.info["longName"]

# print(msft.earnings_history)
# print(api.search_all_tweets(query="$AMZN", max_results=10))
# print(client.available_trends())
# public_tweets = api.home_timeline()
# for tweet in public_tweets:
#    print(tweet.text)

#  api key UsdF3pJdZirVrDAFyq8UhCI24
# api key secret Iqi0oiDEqeZF3ro3LBdFMrBD75DKDajCmmtYEsb9RxH4zQOg7M
#  bearer token AAAAAAAAAAAAAAAAAAAAAP6uhQEAAAAAkWqHdS0J06oyq0NaM0WKuBu5BRI%3DvtYCxIW1dSDQ7jTMCsomKIoChMHzxQGAn00GsnpWW3ccX1fmCL
