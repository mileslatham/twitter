'''
FUNCTIONS TO PULL FOLLOWER DATA FROM TWITTER. EASY TO EDIT TO FIT CERTAIN USE CASES.
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
                 keyword,
                 geocode
                 #date
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
    date = '2020-04-20'
    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True,
                     compression=True)

    # Open/Create a file to append data
    csvFile = open('twitter_network2.csv', 'a')

    # Use csv Writer to extract tweets based on hashtag use, and append to edgeList
    csvWriter = csv.writer(csvFile)
    edgeList = []
    results = []
    for tweet in tweepy.Cursor(api.search,
                               q=keyword,
                               geocode=geocode,
                               count=1000,
                               lang="en",
                               since=date).items():
        if hasattr(tweet, 'retweeted_status'):
            edgeList.append((tweet.user.screen_name,
                             tweet.retweeted_status.user.screen_name))
            results.append(tweet)
            print('results_appended.')
    G = nx.Graph()
    G.add_edges_from(edgeList)
    nx.write_edgelist(G, 'twitter_network.csv')
    print(nx.info(G))
    for item in results:
        # write out the user, the tweet and their follower count into a file
        # the unicode bits are required to write non ASCII language bits into the file
        csvWriter.writerow([item.user.screen_name,
                            item.user.name,
                            item.user.default_profile,
                            item.user.id_str,
                            item.user.following,
                            item.user.description.encode("utf-8"),
                            item.user.utc_offset,
                            item.user.statuses_count,
                            item.user.verified,
                            item.user.geo_enabled,
                            item.user.followers_count,
                            item.user.created_at,
                            item.user.friends_count,
                            item.user.location,
                            item.user.time_zone,
                            item.text.encode("utf-8"),
                            item.entities])
    return results


# function to get followers from a user in the network
# NOTE: this can be prohibitively slow with twitter's rate limiting; difficult to use for more than a few users at
# a time. Getting a network of 2nd/3rd order followers is possible with this script, but takes prohibitively long
# with our current access to twitter's api.

def get_followers(ckey,
                  csecret,
                  atoken,
                  asecret,
                  username):

    csvFile = open('follower_edge_list.csv', 'a')

    csvWriter = csv.dictWriter(csvFile)

    # setting up tweepy authorization with the above keys
    auth = tweepy.OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)

    api = tweepy.API(auth, wait_on_rate_limit=True,
                           wait_on_rate_limit_notify=True,
                           compression=True)

    # finding the followers of the master node
    masterlist = []
    followers = api.followers_ids(id=username, count=5000)

    # this wrapper sub function is used to adhere to the rate limit/avoid errors from missing data or timeouts
    def wrapper():

        while len(masterlist) < 20000:
            try:
                for follower in followers:
                    masterlist.append((username, follower))
                    followers_2 = api.followers_ids(id=follower, count=5000)
                    for follower_2 in followers_2:
                        masterlist.append((follower, follower_2))
            except tweepy.TweepError:
                print("Failed to run the command on that user, Skipping...")

            for edge in masterlist:
                csvWriter.writerow(edge)

    wrapper()
    return followers



# function to build ontology from the output of load_network
#TODO add input format flexibility (csv/*dict*)
def tweetOntology(tweets):
    df_1 = pd.read_excel(tweets, converters={'Code': str,
                                                   'Pos': str,
                                                   'PosSign': str,
                                                   'Neg': str,
                                                   'NegSign': str})

    tweetData = df_1.to_dict(orient='index')
    #print(tweetData)
    ontList = []
    sent = sia()

    for tweet in tweetData:
        pol_score = sent.polarity_scores(text=tweetData[tweet]['tweet'])
        tweetOnt = {}
        bioList = str.split(tweetData[tweet]['bio'])
        tweetList = str.split(tweetData[tweet]['tweet'])
        hashtag_dict = literal_eval(tweetData[tweet]['hashtags'])
        tweetOnt.update({'ID': tweetData[tweet]['user_name']})
        tweetOnt.update({'Name': tweetData[tweet]['screen_name']})
        tweetOnt.update({'Location': tweetData[tweet]['location']})
        #tweetOnt.update({'Position': tweetData[tweet]['bio']}) TODO: clean

        for n in range(0, len(bioList)):
            try:
                if bioList[n][0] == '#':
                    tweetOnt.update({'Org': bioList[n]})
            except IndexError:
                pass
        for n in range(0, len(tweetList)):
            try:
                if tweetList[n][0] == '@':
                    tweetOnt.update({'Agent': tweetList[n]})
            except IndexError:
                pass

        for n in hashtag_dict['hashtags']:
            try:
                tweetOnt.update({'Symbol': n['text']})
            except KeyError:
                pass

        tweetOnt.update({'W': pol_score['compound']})

        ontList.append(tweetOnt)

    with open('tweet_ontology.csv', 'w') as csvfile:
        fieldnames = ontList[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ontList)

    return ontList


h = load_network(keyword='COVID19',
                 geocode='33.658259,-117.903473,20mi')

