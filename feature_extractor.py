import json
import csv
import tldextract

def extract_to_file(tweetsfilename, featuresfilename):
    fieldnames = [
        'id', # Tweet ID
        'timestamp_ms', # Timestamp in ms, GMT
        'user_id', # Twitter User ID
        'action', # mention, tweet, retweet
        'entity_type', # user_id, hashtag, url, tld, symbol
        'entity' # object associated with action
    ]

    with open(featuresfilename, 'w') as featurefile:
        writer = csv.DictWriter(
            featurefile,
            fieldnames=fieldnames
        )
        writer.writeheader()

        with open(tweetsfilename, 'r') as tweets:
            for rawtweet in tweets:
                try:
                    tweet = json.loads(rawtweet)

                    # extract common features
                    common_features = dict()
                    common_features['id'] = tweet['id']
                    common_features['timestamp_ms'] = tweet['timestamp_ms']
                    common_features['user_id'] = tweet['user']['id']

                    # extract user relationships
                    for user in tweet['entities']['user_mentions']:
                        write_feature_row(writer, common_features, 'mention', user['id'], 'user_id')

                    # if not retweet extract user content
                    if "retweeted_status" not in tweet:
                        for hashtag in tweet['entities']['hashtags']:
                            write_feature_row(writer, common_features, 'tweet', hashtag['text'], 'hashtag')
                        for url in tweet['entities']['urls']:
                            write_feature_row(writer, common_features, 'tweet', url['expanded_url'], 'url')
                        for url in tweet['entities']['urls']:
                            tld = tldextract.extract(url['expanded_url'])
                            write_feature_row(writer, common_features, 'tweet', tld.fqdn, 'tld')
                        for s in tweet['entities']['symbols']:
                            write_feature_row(writer, common_features, 'tweet', s, 'symbol')

                    else: # extract retweet relationships
                        u = str(tweet['retweeted_status']['user']['id'])
                        write_feature_row(writer, common_features, 'retweet', u, 'user_id')

                        # extract echoed content
                        for hashtag in tweet['retweeted_status']['entities']['hashtags']:
                            write_feature_row(writer, common_features, 'retweet', hashtag['text'], 'hashtag')
                        for url in tweet['retweeted_status']['entities']['urls']:
                            write_feature_row(writer, common_features, 'retweet', url['expanded_url'], 'url')
                        for url in tweet['retweeted_status']['entities']['urls']:
                            tld = tldextract.extract(url['expanded_url'])
                            write_feature_row(writer, common_features, 'retweet', tld.fqdn, 'tld')
                        for s in tweet['retweeted_status']['entities']['symbols']:
                            write_feature_row(writer, common_features, 'retweet', s['text'], 'symbol')

                except:
                    print(f"Error extracting from the following tweet:")
                    print(rawtweet)

def write_feature_row(w, common, action, entity, entity_type):
    tmp_dict = dict()
    for k in common:
        tmp_dict[k] = common[k]
    tmp_dict['action'] = action
    tmp_dict['entity'] = entity
    tmp_dict['entity_type'] = entity_type
    w.writerow(tmp_dict)


if __name__ == "__main__":
    import sys

    extract_to_file(sys.argv[1], sys.argv[2])