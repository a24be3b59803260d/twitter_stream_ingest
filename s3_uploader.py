import boto3
import threading
import os


class BucketUploader(threading.Thread):
    def __init__(self, bucket_name, filename):
        threading.Thread.__init__(self)
        self.bucket_name = bucket_name
        self.filename = filename

    def run(self):
        blob_id = self.filename.split('/')[-1]
        print("Uploading blob '%s' to S3 bucket '%s'." % (
            blob_id,
            self.bucket_name))
        try:
            s3 = boto3.resource('s3')
            s3.Object(self.bucket_name, blob_id).put(
                Body=open(self.filename, 'rb'))

            os.remove(self.filename)
            print("Upload successful; removed file: %s" % self.filename)
        except:
            print("An error occurred, leaving file '%s' on disk" % self.filename)


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 3:
        print("No input file specified.")
        exit(-1)

    output_bucket = sys.argv[1]
    input_file = sys.argv[2]

    uploader_thread = BucketUploader(output_bucket, input_file)
    uploader_thread.start()


