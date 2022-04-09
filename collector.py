#!/usr/bin/env python3
# from tweepy.streaming import StreamingClient
from tweepy import Stream
from tweepy import OAuthHandler, API

import json
import time
import configparser
from datetime import datetime
from urllib3.exceptions import ProtocolError as UrlLibProtocolError
from requests.exceptions import ConnectionError as RequestsConnectionError
from os.path import exists

from s3_uploader import BucketUploader
from feature_extractor import extract_to_file


class TwitterListener(Stream):

    def __next_filename(self):
        return self.prefix + datetime.now().strftime(
            '_%Y%m%d-%H%M%S_{fname}').format(
            fname='raw_tweets.jsonl')

    def __init__(
            self,
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret,
            prefix,
            target_count,
            bucket_name=None):
        super().__init__(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret)
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
        self.backoff_in_seconds = 1

    def close_file(self):
        self.outfile.close()

        # check to to see if we are uploading to s3
        if self.s3:
            # create uploader thread
            uploader_thread = BucketUploader(
                self.outfilename,
                extract_to_file) # Optional feature extraction function
            uploader_thread.start()

    def on_data(self, data):
        self.backoff_in_seconds = 1
        jd = json.loads(data)
        self.outfile.write(json.dumps(jd) + "\n")
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
    follow_file = config['io'].get('follow_file')

    twitter_listener = None

    # check for S3 configuration, enable if present
    s3_bucketname = config['io'].get('s3_bucketname', None)

    consumer_key = config['twitter'].get('consumer_key')
    consumer_secret = config['twitter'].get('consumer_secret')
    access_token = config['twitter'].get('access_token')
    access_token_secret = config['twitter'].get('access_token_secret')

    userids_list = list()
    if exists(follow_file):
        with open(follow_file, 'r') as f:
            userids = list()
            userstrings = f.read().split("\n")

            auth = OAuthHandler(
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=access_token,
                access_token_secret=access_token_secret)

            api = API(auth)

            for user in userstrings:
                userids.append(
                    str(api.get_user(screen_name=user).id)
                )

            if userids:
                userids_list = ",".join(userids)

    twitter_listener = TwitterListener(
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret,
        outfile,
        target_count,
        s3_bucketname)
    
    if not s3_bucketname:
        print("[!] No S3 bucket name found, running in local archive mode.")

    print(" * Tracker String: %s" % tracker_string)

    backoff_in_seconds = 1
    while backoff_in_seconds < 65:
        try:
            print("Starting listener...")
            if tracker_string or userids_list:
                twitter_listener.filter(track=[tracker_string], follow=[userids_list])
            else:
                print("Missing or invalid track or follow params.")
                exit(0)

        except KeyboardInterrupt:
            print("Shutting down listener...")
            twitter_listener.close_file()
            print("Clean shutdown successful!")
            exit(0)
        except (UrlLibProtocolError, RequestsConnectionError):
            print(
                "Connection reset by host, retrying in %d seconds." %
                twitter_listener.backoff_in_seconds)
            time.sleep(twitter_listener.backoff_in_seconds)
            twitter_listener.backoff_in_seconds *= 2
        except:
            raise
