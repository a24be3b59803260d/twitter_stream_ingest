import boto3
import threading
import os
import configparser


class BucketUploader(threading.Thread):
    def __init__(
            self,
            filename,
            feature_extractor=None):
        threading.Thread.__init__(self)

        self.FEATURE_EXTENSION = ".features.csv"

        self.filename = filename
        self.features_extractor = feature_extractor

        config = configparser.ConfigParser()
        config.read('collector.cfg')

        self.bucket_name = config['io'].get('s3_bucketname')
        self.delete_after_upload = config['io'].get('delete_after_upload').lower() == 'true'
        self.access_key = config['io'].get('access_key')
        self.secret_access_key = config['io'].get('secret_access_key')
        self.endpoint_url= config['io'].get('endpoint_url')

    def run(self):
        blob_id = self.filename.split('/')[-1]
        if self.features_extractor:
            print(f"Running feature extraction on {blob_id}")
            feature_filename = f"{self.filename}{self.FEATURE_EXTENSION}"
            self.features_extractor(self.filename, feature_filename)
            print(f"Finished extracting featuers to {feature_filename}")
            self.upload_blob(
                f"{self.filename}{self.FEATURE_EXTENSION}",
                f"{blob_id}{self.FEATURE_EXTENSION}")
        self.upload_blob(
            f"{self.filename}",
            f"{blob_id}")

    def upload_blob(self, filename, blob_id):
        print("Uploading blob '%s' to S3 bucket '%s'." % (
            blob_id,
            self.bucket_name))
        try:
            s3 = boto3.resource(
                's3',
                endpoint_url = self.endpoint_url,
                aws_access_key_id = self.access_key,
                aws_secret_access_key = self.secret_access_key)

            s3.Object(self.bucket_name, blob_id).put(
                Body=open(filename, 'rb'))

            if self.delete_after_upload:
                os.remove(filename)
                print("Upload successful; removed file: %s" % filename)
            else:
                print("Upload successful; preserving file: %s" % filename)

        except BaseException as err:
            print(f"Unexpected {err}, {type(err)}")
            print("An error occurred, leaving file '%s' on disk" % self.filename)
            raise

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print("No input file specified.")
        exit(-1)

    input_file = sys.argv[1]

    uploader_thread = BucketUploader(input_file)
    uploader_thread.start()
    uploader_thread.join()
