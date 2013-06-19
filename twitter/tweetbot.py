import tweepy
import humanize
import math
import re, sys, yaml
from datetime import datetime
from json import load
from urllib import urlopen
from urllib import urlencode
from pandas import DataFrame
from optparse import OptionParser

# Load options
QUERIES = {
    'debt_ceiling': 'select date, close_today from t3c where item like \'%subject to limit%\' order by date desc limit 2'
}

def load_options():
    parser = OptionParser()
    parser.add_option("-t", "--tweet-type", dest="tweet_type", default="debt_ceiling",
                  help="write report to FILE", metavar="FILE")

    (options, args) = parser.parse_args()
    return options

def connect_to_twitter(config="api.yml"):
    conf = yaml.safe_load(open(config))
    auth = tweepy.OAuthHandler(conf['consumer_key'], conf['consumer_secret'])
    auth.set_access_token(conf['access_token'], conf['access_token_secret'])
    api = tweepy.API(auth)
    return api

def query_treasury(sql):
    url = 'https://box.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/'
    query_string = urlencode({'q':sql})
    handle = urlopen(url + '?' + query_string)
    if handle.code == 200:
        d = load(handle)
        return DataFrame(d)
    else:
        raise ValueError(handle.read())

def human_number(num):
    return humanize.intword(int(math.ceil(num))).lower()

def human_date(date):
    return humanize.naturalday(date).title()

def construct_tweet(options):
    t = options.tweet_type
    if t == 'debt_ceiling':
        q = QUERIES[t]
        df = query_treasury(q)
        num = human_number(df['close_today'][0]*1e6)
        date = human_date(datetime.strptime(df['date'][0], "%Y-%m-%d"))
        tweet = "As of %s, the US Government is $%s in debt. Learn more at http://treasury.io" % (date, num)
    return tweet

if __name__ == '__main__':
    options = load_options()
    api = connect_to_twitter()
    tweet = construct_tweet(options)
    print "TWEET:", tweet
    api.update_status(tweet)
