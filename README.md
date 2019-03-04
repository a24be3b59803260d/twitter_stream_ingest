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

# Errors
If the program emits a "Twitter API Access Error: 4xx" Twitter is rejecting the connection.

Code 401 means "Missing or incorrect authentication credentials. This may also [be] returned in other undefined circumstances." which probably means there is an error in the configuration keys.

All response codes should be documented here: https://developer.twitter.com/en/docs/basics/response-codes.html


# Future Work

Future updates will include an option to automatically push output directly to S3 buckets reducing storage needs for the collector instance to less than 100MB (well within a t2.nano instance).

