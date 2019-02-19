import argparse
import urllib
import json
import datetime
import random
import os
import pickle
from datetime import timedelta
import scipy
import oauth2
from dateutil import parser
import get_twitter_data
import get_yahoo_data
import re
#import scipy
import tweepy
import csv
import sys
from io import StringIO
from zipfile import ZipFile
from urllib.request import urlopen
import urllib.parse
import numpy as np
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
# import Multiclass_SVM
from sklearn.naive_bayes import BernoulliNB
import NaiveBayes
from sklearn.metrics import confusion_matrix
import datetime
# from textblob import TextBlob


class TwitterData:
    #start __init__
    def __init__(self,givenDate):
        self.currDate = datetime.datetime.strptime(givenDate,'%Y-%m-%d')
        #self.currDate = datetime.datetime.now()
        #print type(self.currDate)
        #print self.currDate
        #print "123"
        # print type(y)
        # print y
        self.weekDates = []
        self.weekDates.append(self.currDate.strftime("%Y-%m-%d"))
        for i in range(1,20):
            dateDiff = timedelta(days=-i)
            newDate = self.currDate + dateDiff
            self.weekDates.append(newDate.strftime("%Y-%m-%d"))
        # end loop
        # print ("New Week Dates =",self.weekDates)
    # end

    # start getWeeksData
    def getTwitterData(self, keyword, time):
        self.weekTweets = {}
        if(time == 'lastweek'):
            for i in range(0,9):
                params = {'since': self.weekDates[i+1], 'until': self.weekDates[i]}
                self.weekTweets[i] = self.getData(keyword, params)
            # end loop

            # Write data to a pickle file
            filename = 'Data/weekTweets_'+urllib.parse.unquote(keyword.replace("+", " "))+'_'+str(int(random.random()*10000))+'.txt'
            outfile = open(filename, 'wb')
            pickle.dump(self.weekTweets, outfile)
            outfile.close()
        elif(time == 'today'):
            for i in range(0,1):
                params = {'since': self.weekDates[i+1], 'until': self.weekDates[i]}
                # params = {'since': self.weekDates[i]}
                self.weekTweets[i] = self.getData(keyword, params)
            # end loop
        else:
            for i in range(15, 0, -1):
                print('i',i,'since', self.weekDates[i], 'until: ', self.weekDates[i-1])
                params = {'since': self.weekDates[i], 'until': self.weekDates[i-1]}
                self.weekTweets[i] = self.getData(keyword, params)
            filename = 'Data/weekTweets_'+urllib.parse.unquote(keyword.replace("+", " "))+'_'+str(int(random.random()*10000))+'.txt'
            outfile = open(filename, 'wb')
            pickle.dump(self.weekTweets, outfile)
            outfile.close()
        return self.weekTweets
    '''
        inpfile = open('data/weekTweets/weekTweets_obama_7303.txt')
        self.weekTweets = pickle.load(inpfile)
        inpfile.close()
        return self.weekTweets
    '''
    # end

    def parse_config(self):
      config = {}
      # from file args
      if os.path.exists('config.json'):
          with open('config.json') as f:
              config.update(json.load(f))
      else:
          # may be from command line
          parser = argparse.ArgumentParser()

          parser.add_argument('-ck', '--consumer_key', default=None, help='Your developper `Consumer Key`')
          parser.add_argument('-cs', '--consumer_secret', default=None, help='Your developper `Consumer Secret`')
          parser.add_argument('-at', '--access_token', default=None, help='A client `Access Token`')
          parser.add_argument('-ats', '--access_token_secret', default=None, help='A client `Access Token Secret`')

          args_ = parser.parse_args()
          def val(key):
            return config.get(key)\
                   or getattr(args_, key)\
                   or input('Your developper `%s`: ' % key)
          config.update({
            'consumer_key': val('consumer_key'),
            'consumer_secret': val('consumer_secret'),
            'access_token': val('access_token'),
            'access_token_secret': val('access_token_secret'),
          })
      # should have something now
      return config

    def oauth_req(self, url, http_method="GET", post_body=None,
                  http_headers=None):
      config = self.parse_config()
      consumer = oauth2.Consumer(key=config.get('consumer_key'), secret=config.get('consumer_secret'))
      token = oauth2.Token(key=config.get('access_token'), secret=config.get('access_token_secret'))
      client = oauth2.Client(consumer, token)

      resp, content = client.request(
          url,
          method=http_method
      )
      return content

    # start getTwitterData

    def getData(self, keyword, params = {}):
        maxTweets = 200
        url = 'https://api.twitter.com/1.1/search/tweets.json?'
        data = {'q': keyword, 'lang': 'en', 'result_type': 'mixed','count': maxTweets, 'include_entities': 0} #, 'since_id': 2016
        # print("Keyword is this: ", keyword)
        # Add if additional params are passed
        if params:
            for key, value in params.items():
                data[key] = value
        # print("This is data: ", data)
        url += urllib.parse.urlencode(data)
        # print("this is the URl: ", url)

        response = self.oauth_req(url) 
        jsonData = json.loads(response)
        # print(jsonData['statuses'].encode('utf-8'))
        tweets = []
        if 'errors' in jsonData:
            print ("API Error")
            print (jsonData['errors'])
        else:
            for item in jsonData['statuses']:
                # print item['created_at']
                #d=datetime.DateTime.strp
                d = datetime.datetime.strptime(item['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                #print d
                #print 456
                #d=datetime.datetime.now
                str = d.strftime('%Y-%m-%d')+" | "+item['text'].replace('\n', ' ')
                print(item['created_at'])
                # dt = parser.parse(item['created_at'])
                # tweets.append(item['text'])
                # print (str)
                tweets.append(str)
        return tweets
        print("Finished retrieving tweets")
    # end

# end class