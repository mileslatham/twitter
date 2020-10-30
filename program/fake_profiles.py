'''
WORK IN PROGRESS
Miles Latham (2020)
latham.miles@gmail.com
'''

import tweepy
import csv
import networkx as nx
import pandas as pd
from ast import literal_eval
from nltk.sentiment.vader import SentimentIntensityAnalyzer as sia
import nltk
nltk.download('vader_lexicon')
import xlwt
import xlrd
# date in YYYY-MM-DD format
import os
import glob
import openpyxl

# baseline function to load a network centered around retweets. ie tweets that use a selected
# hashtag are identified, and then loaded into an edgelist using interactions between users (retweets, favorites,
# as the edges
def load_network(#ckey,
                 #csecret,
                 #atoken,
                 #asecret,
                 ID,
                 username
                 ):
    ckey = ''
    csecret = ''

    # The access tokens can be found on your applications's Details
    # page located at https://dev.twitter.com/apps (located
    # under "Your access token")
    atoken = ''
    asecret = ''
    # setting up tweepy authorization with the above keys
    auth = tweepy.OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)

    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True,
                     compression=True)

    # Open/Create a file to append data
    csvFile = open('twitter_network2.csv', 'a')

    # Use csv Writer to extract tweets based on hashtag use, and append to edgeList
    csvWriter = csv.writer(csvFile)
    edgeList = []

    # getting the retweeters
    retweets_list = api.retweets(ID)
    for retweet in retweets_list:
        username = retweet.user.screen_name
        edgeList.append('RealDonaldTrump')
        edgeList.append(username)

    G = nx.Graph()
    G.add_edges_from(edgeList)
    nx.write_edgelist(G, 'twitter_network.csv')
    print(nx.info(G))
    for item in retweets_list:
        # write out the user, the tweet and their follower count into a file
        # the unicode bits are required to write non ASCII language bits into the file
        csvWriter.writerow([item.user.profile_image_url_https,
                            item.user.screen_name,
                            item.user.name,
                            item.user.default_profile,
                            item.user.id_str,
                            item.user.following,
                            item.user.description.encode("utf-8"),
                            item.user.utc_offset,
                            item.user.statuses_count,
                            item.user.verified,
                            item.user.followers_count,
                            item.user.created_at,
                            item.user.friends_count,
                            item.user.location,
                            item.user.time_zone,
                            item.text.encode("utf-8"),
                            item.entities])


    return retweets_list

load_network(ID=1316031426618327040,
             username='RealDonaldTrump')