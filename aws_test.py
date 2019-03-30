import io

from PIL import Image

from aws import update_image


def main():
    stream = io.BytesIO()
    img = Image.open('./pasqua1.jpeg', mode='r')
    img.save(stream, format='PNG')
    update_image(img, "name.png")


# def upload_steam(location, stream)


if __name__ == "__main__":
    main()

# Print out bucket names
# for bucket in s3.buckets.all():
#     print(bucket)
