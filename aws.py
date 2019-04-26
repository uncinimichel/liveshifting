from datetime import datetime

import boto3
import pandas as pd

AWS_REGION = "eu-west-1"
session = boto3.Session(profile_name='piuser')
s3 = session.resource('s3')
ses = session.client('ses', region_name=AWS_REGION)
recording_bucket = 'com.liveshifting.recordings'


def get_today():
    return datetime.now().strftime('%Y-%m-%d')


def list_object():
    results = s3.Bucket(recording_bucket)

    raw_data = {"s3_keys": [],
                "date": [],
                "timestamp": [],
                "image_format": [],
                "human_date": [],
                "simple_keys": []}
    for result in results.objects.all():
        date, timestamp_image_format = result.key.split("/")
        timestamp, image_format = timestamp_image_format.split(".")
        human_date = datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        raw_data["s3_keys"].append(result.key)
        raw_data["date"].append(date)
        raw_data["timestamp"].append(timestamp)
        raw_data["image_format"].append(image_format)
        raw_data["human_date"].append(human_date)
        raw_data["simple_keys"].append(timestamp_image_format)

    df = pd.DataFrame(data=raw_data,
                      columns=['s3_keys', 'date', 'timestamp', 'image_format', 'human_date', 'simple_keys'])
    df.to_csv('./download/example.csv')

    # time_now = int(str(time()).split('.')[0])
    # processed.sort(key=lambda p: int(p[2]))
    for index, row in df.sort_values(by=["timestamp"], ascending=False).head(50).iterrows():
        download_key(key=row["s3_keys"], to_name=row["simple_keys"])


def download_key(key, to_name):
    s3.meta.client.download_file(recording_bucket, key, "./download/" + to_name)


def update_image(image_file, name):
    # Create a folder for today
    today = get_today()
    file_name = "%s/%s" % (today, name)
    s3.Object(recording_bucket, file_name).put(Body=image_file)
    print("Upload of %s in %s" % (file_name, recording_bucket))


def download_today_folder():
    today = get_today()
    file_name = "%s/%s" % (today, "1554360505.jpeg")
    s3.meta.client.download_file(recording_bucket, file_name, "./download/ciao.jpeg")


def main():
    # download_today_folder()
    list_object()
    pass


if __name__ == "__main__":
    main()


def notify_via_ses():
    BODY_HTML = """<html>
<head></head>
<body>
  <h1>Amazon SES Test (SDK for Python)</h1>
  <p>This email was sent with
    <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
    <a href='https://aws.amazon.com/sdk-for-python/'>
      AWS SDK for Python (Boto)</a>.</p>
</body>
</html> 
            """

    # The subject line for the email.
    subject = "Amazon SES Test (SDK for Python)"

    # The email body for recipients with non-HTML email clients.
    body_text = ("Amazon SES Test (Python)\r\n"
                 "This email was sent with Amazon SES using the "
                 "AWS SDK for Python (Boto)."
                 )
    CHARSET = "UTF-8"
    SENDER = "Sender Name <uncini.michel@gmail.com>"

    # try:

    ses.send_email(
        Source=SENDER,
        Destination={
            'ToAddresses': [
                'uncini.michel@gmail.com',
            ]
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': BODY_HTML,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': body_text,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': subject,
            },
        }
    )
    # Display an error if something goes wrong.
    # except:
    #     print("err")
    # else:
    #     print("Email sent! Message ID:"),
    #     print(response['MessageId'])
