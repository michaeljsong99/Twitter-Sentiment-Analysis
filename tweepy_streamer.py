from tweepy.streaming import StreamListener # Can listen to tweets
from tweepy import OAuthHandler # Authenticating credentials
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import re # Regular Expression in Python

import twitter_credentials # Import our credentials.

# Twitter Client Class
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets): # How many tweets we want to show.
        tweets = []
        # Get the tweets off a user's timeline. If you don't specify the user, it will get your own tweets.
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_hashtag_tweets(self, hashtag, num_tweets): # Gets the most recent n tweets with a hashtag.
        tweets = []
        for tweet in Cursor(api.search, q='#' + hashtag).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline,id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets

# Twitter Authenticator class
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth

class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # Handles Twitter Authentication and connection to Twitter Streaming API.
        listener = TwitterListener(fetched_tweets_filename)

        # Create a Twitter stream.
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        stream.filter(track = hash_tag_list)

# Create a class that allows us to print the tweets.

class TwitterListener(StreamListener):
    """
    Basic Listener class that just prints recevied tweets to stdout.
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    # Takes data from tweets.
    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on data: %s" % str(e))
        return True

    # Happens if there is an error that occurs. Prints status of error to screen.
    def on_error(self, status):
        if status == 420: # This is the error code when Twitter tells you you are scraping too many.
            return False # Kill the connection to avoid getting booted on Twitter.
        print(status)


# Functionality for analyzing and categorizing content from tweets.
class TweetAnalyzer():

    def tweets_to_data_frame(self, tweets): # Converts tweets into a dataframe.
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df

    def clean_tweet(self, tweet):
        # Removing special characters and hyperlinks from the tweet.
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        return analysis.sentiment.polarity
        # > 0 if positive, 0 if neutral, < 0 if negative.



if __name__ == "__main__":

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    # To get tweets from a specific user.
    #tweets = api.user_timeline(screen_name='realDonaldTrump', count=200) # Provided from Twitter Client API.

    # To get tweets with a hashtag.
    tweets = twitter_client.get_hashtag_tweets(hashtag='coronavirus', num_tweets=500)

    #print(dir(tweets[0])) # Shows what information you can get from a tweet
    #print(tweets[0].retweet_count) # Shows how many times something was retweeted.

    df = tweet_analyzer.tweets_to_data_frame(tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])

    print(df.head(40))

    # Metrics
    # Get average length of all tweets
    #print(np.mean(df['len']))
    # Get the number of likes for the most liked tweet.
    #print(np.max(df['likes']))
    # Get the number of retweets for the most retweeted tweet.
    #print(np.max(df['retweets']))

    # Time Series
    #time_likes = pd.Series(data=df['likes'].values, index=[df['date']])
    #time_likes.plot(figsize=(16, 4), label='likes', legend=True)
    #time_retweets = pd.Series(data=df['retweets'].values, index=[df['date']])
    #time_retweets.plot(figsize=(16, 4), label='retweets', legend=True)
    #plt.show()





