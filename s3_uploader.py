import boto3
import threading
import os
import configparser


class BucketUploader(threading.Thread):
    def __init__(
            self,
            filename):
        threading.Thread.__init__(self)

        self.filename = filename

        config = configparser.ConfigParser()
        config.read('collector.cfg')

        self.bucket_name = config['io'].get('s3_bucketname')
        self.access_key = config['io'].get('access_key')
        self.secret_access_key = config['io'].get('secret_access_key')
        self.endpoint_url= config['io'].get('endpoint_url')

    def run(self):
        blob_id = self.filename.split('/')[-1]
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
                Body=open(self.filename, 'rb'))

            os.remove(self.filename)
            print("Upload successful; removed file: %s" % self.filename)
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
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
