from datetime import datetime

import boto3

session = boto3.Session(profile_name='piuser')
s3 = session.resource('s3')
recording_bucket = 'com.liveshifting.recordings'


def update_image(image_file, name):
    # Create a folder for today
    today = datetime.now().strftime('%Y-%m-%d')
    file_name = "%s/%s" % (today, name)
    s3.Object(recording_bucket, file_name).put(Body=image_file)
    print("Upload of %s in %s" % (file_name, recording_bucket))


def main():
    pass


if __name__ == "__main__":
    main()
