#!/usr/bin/env python3
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream

import json
import configparser
from datetime import datetime

from s3_uploader import BucketUploader


class TwitterListener(StreamListener):

    def __next_filename(self):
        return self.prefix + datetime.now().strftime(
            '_%Y%m%d-%H%M%S_{fname}').format(
            fname='raw_tweets.jsonl')

    def __init__(self, prefix, target_count, bucket_name=None):
        super().__init__(self)
        self.prefix = prefix
        self.target_count = target_count
        print("Starting with following params:")
        print(" * prefix: %s" % prefix)
        print(" * target_count: %d" % target_count)
        self.outfilename = self.__next_filename()
        self.outfile = open(self.outfilename, 'w')
        self.tweet_count = 0
        self.s3 = False
        if bucket_name is not None:
            print(" * s3_bucketname: %s" % bucket_name)
            self.s3 = True
            self.bucket = bucket_name

    def close_file(self):
        self.outfile.close()

        # check to to see if we are uploading to s3
        if self.s3:
            # create uploader thread
            uploader_thread = BucketUploader(
                self.bucket,
                self.outfilename)
            uploader_thread.start()

    def on_data(self, data):
        self.outfile.write(data)
        self.tweet_count += 1

        if self.tweet_count >= self.target_count:
            self.close_file()

            self.outfilename = self.__next_filename()
            print("rolling new file at %s" % self.outfilename)
            self.outfile = open(self.outfilename, 'w')
            self.tweet_count = 0

        return True

    def on_error(self, status):
        print("Twitter API Access Error: %s" % status)
        exit(status)


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('collector.cfg')

    outfile = config['io'].get('outfile')
    target_count = config['io'].getint('target_count')
    tracker_string = config['io'].get('tracker_string')

    twitter_listener = None

    # check for S3 configuration, enable if present
    try:
        twitter_listener = TwitterListener(
            outfile,
            target_count,
            config['io'].get('s3_bucketname'))
    except:
        print("[!] No S3 bucket name found, running in local archive mode.")
        twitter_listener = TwitterListener(
            outfile,
            target_count)

    auth = OAuthHandler(
               config['twitter'].get('consumer_key'),
               config['twitter'].get('consumer_secret'))
    auth.set_access_token(
               config['twitter'].get('access_token'),
               config['twitter'].get('access_token_secret'))

    stream = Stream(auth, twitter_listener)

    try:
        stream.filter(track=tracker_string)
    except KeyboardInterrupt:
        print(twitter_listener.__dict__.keys())
        twitter_listener.close_file()
        print("Clean shutdown successful!")
    except:
        raise

