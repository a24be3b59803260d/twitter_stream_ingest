#!/usr/bin/env python3
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream

import json
import configparser
from datetime import datetime


class TwitterListener(StreamListener):

    def next_filename(self):
        return self.prefix + datetime.now().strftime(
            '_%Y%m%d-%H%M%S_{fname}').format(
            fname='raw_tweets.jsonl')

    def __init__(self, prefix, target_count=10):
        super().__init__(self)
        self.prefix = prefix
        self.target_count = target_count
        print("Starting with following params:")
        print(" * prefix: %s" % prefix)
        print(" * target_count: %d" % target_count)
        self.outfile = open(self.next_filename(), 'w')
        self.tweet_count = 0

    def on_data(self, data):
        self.outfile.write(data)
        self.tweet_count += 1

        if self.tweet_count >= self.target_count:
            self.outfile.close()
            nf = self.next_filename()
            print("rolling new file at %s" % nf)
            self.outfile = open(nf, 'w')
            self.tweet_count = 0

        return True

    def on_error(self, status):
        print("Twitter API Access Error: %s" % status)
        exit(status)

if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('collector.cfg')

    tl = TwitterListener(
        config['io'].get('outfile'),
        config['io'].getint('target_count'))

    tracker_string = config['io'].get('tracker_string')

    auth = OAuthHandler(
               config['twitter'].get('consumer_key'),
               config['twitter'].get('consumer_secret'))
    auth.set_access_token(
               config['twitter'].get('access_token'),
               config['twitter'].get('access_token_secret'))

    stream = Stream(auth, tl)

    stream.filter(track=tracker_string)
