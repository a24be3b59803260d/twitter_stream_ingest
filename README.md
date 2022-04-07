# Installation
Start by cloning this repository to the location it will run from and updating the config.
* Create Twitter API Keys (via App creation on the developer.twitter.com site).
* Copy "collector.cfg.example" to "collector.cfg" and adjust values as needed.
* Insert Consumer API Keys and Access Tokens into the config
 * Set the tracker_string in collector.cfg to the terms/user/hashtags of interest. Full specifications for this can be found here: https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters

Setup a virtual environment for and install dependencies.
```sh
$ virtualenv -p python3 .env
$ source .env/bin/activate
(.env) $ pip install -r requirements.txt
```

# Running the collector
From the virtual environment run the app with python.
```sh
(.env) $ python collector.py
 * prefix: /tmp/maga_qanon
 * target_count: 10000
rolling new file at /tmp/maga_qanon_20190304-123240_raw_tweets.jsonl
[...]
```
Using **screen** or **nohup** will allow the collector script to run unattended.

# S3 Integration
Output may be directed to an S3 capable API instead of the local disk (enabling use of a tiny collector VM) by adding the **s3_bucketname** key to the __[io]__ section of the __collector.cfg__ file and configuring credentials that have permission to write to the specified bucket. The value of the __s3_bucketname__ key should be the bucket name without the ARN prefix.

AWS CLI configuration steps can be found here: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html

Any S3 compatible storage API can be configured by setting the **access_key**, **secret_access_key**, and **endpoint_url** keys in the __[io]__ section.

An example updated __[io]__ section appears below:
```
[io]
outfile = /tmp/twitter_archive/interesting_tweets
target_count = 1000
tracker_string = #interesting,#tweets
s3_bucketname = tweets.archive.mybucket
access_key = 0000000000000000000000000
secret_access_key = KEYAAAAAAAAAAAAAAAAAAAAAAAAAAAA
endpoint_url = https://s3.us-west-000.backblazeb2.com
```

# Errors
If the program emits a "Twitter API Access Error: 4xx" Twitter is rejecting the connection.

Code 401 means "Missing or incorrect authentication credentials. This may also [be] returned in other undefined circumstances." which probably means there is an error in the configuration keys.

All response codes should be documented here: https://developer.twitter.com/en/docs/basics/response-codes.html

