import io
import os
import socket
import struct
from datetime import datetime
from time import time

from PIL import Image

from aws import update_image

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means all interfaces)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')

images_path = './images'


def save_image_in_folder(pil_image, folder=images_path):
    if not os.path.isdir(folder):
        os.makedirs(folder)
    today = datetime.now().strftime('%Y-%m-%d')
    today_images = os.path.join(folder, today)
    if not os.path.isdir(today_images):
        os.makedirs(today_images)
    image_name = str(time()).split('.')[0] + '.jpeg'
    image_path = os.path.join(today_images, image_name)
    print(image_path)
    pil_image.save(image_path)
    print('Image is saved')


def save_image_to_aws(fn_upload, pil_image):
    image_name = str(time()).split('.')[0] + '.jpeg'
    in_mem_file = io.BytesIO()
    pil_image.save(in_mem_file, format=pil_image.format)
    fn_upload(in_mem_file.getvalue(), image_name)


def main():
    try:
        while True:
            # Read the length of the image as a 32-bit unsigned int. If the
            # length is zero, quit the loop end exit
            image_len_binary = connection.read(struct.calcsize('<L'))
            image_len = struct.unpack('<L', image_len_binary)[0]
            if not image_len:
                break
            # Construct a stream to hold the image data and read the image
            # data from the connection
            image_stream = io.BytesIO()
            image_stream.write(connection.read(image_len))
            print('Image image_len %s' % image_len)
            # Rewind the stream, open it as an image with PIL and do some processing on it, like save it
            image_stream.seek(0)
            image = Image.open(image_stream)
            print('Image is %dx%d' % image.size)
            image.verify()
            print('Image is verified')
            # If you need to load the image after using this method, you must reopen the image file.
            image = Image.open(image_stream)
            # save_image_in_folder(image, images_path)
            save_image_to_aws(update_image, image)

    finally:
        connection.close()
        server_socket.close()


if __name__ == "__main__":
    main()
