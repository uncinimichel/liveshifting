import io
import os
import socket
import struct
from datetime import datetime
from time import time

import cv2
import numpy as np

from detect_person import is_detection


class SocketListeningImages:

    def __init__(self, mode="folder"):
        print(mode)
        if mode == "folder ":
            self.save = self.save_image_in_folder
        else:
            self.save = self.save_image_to_aws

    images_path = './images'

    def setup(self):
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', 8000))
        server_socket.listen(0)

        print("socket listening for connections on 0.0.0.0:8000")
        connection = server_socket.accept()[0].makefile('rb')
        return connection, server_socket

    def save_image_in_folder(self, cv2_image, folder=images_path):
        if not os.path.isdir(folder):
            os.makedirs(folder)
        today = datetime.now().strftime('%Y-%m-%d')
        today_images = os.path.join(folder, today)
        if not os.path.isdir(today_images):
            os.makedirs(today_images)
        image_name = str(time()).split('.')[0] + '.jpeg'
        image_path = os.path.join(today_images, image_name)
        print(image_path)
        cv2.imwrite(image_path, cv2_image)
        print('Image is saved')

    def save_image_to_aws(self, fn_upload, cv2_image):
        image_name = str(time()).split('.')[0] + '.jpeg'
        _, buf = cv2.imencode('jpeg', cv2_image)

        fn_upload(buf.getvalue(), image_name)

    def verify_and_get_image(self, image_bytes):
        image_stream = io.BytesIO()
        image_stream.write(image_bytes)
        # Rewind the stream, open it as an image with PIL and do some processing on it, like save it
        image_stream.seek(0)
        data = np.fromstring(image_stream.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, 1)

        # print('Image is %dx%d' % image.size)
        # image.verify()
        # print('Image is verified')
        # If you need to load the image after using this method, you must reopen the image file.
        return image

    def start(self):
        connection, server_socket = self.setup()
        base_image = None

        try:
            while True:
                # Read the recording type:
                recording_mode_binary = connection.read(struct.calcsize('<b'))
                recording = struct.unpack('<b', recording_mode_binary)[0]
                if recording == 2:
                    print("Recording is Paused")
                    base_image = None
                    continue
                elif recording == 1:
                    print("Recording is still going ")
                elif recording == 0:
                    print("Recording is ending and I need to exit")
                    break

                # Read the length of the image as a 32-bit unsigned int.
                image_len_binary = connection.read(struct.calcsize('<L'))
                image_len = struct.unpack('<L', image_len_binary)[0]

                image_binary = connection.read(image_len)
                image = self.verify_and_get_image(image_binary)

                if base_image is None:
                    base_image = image

                is_detection_detected, image_with_detection = is_detection(base_image, image)

                if is_detection_detected:
                    print("Yes detection")
                    self.save(image, self.images_path)
                else:
                    print("No detection")

        finally:
            print("socket stop listening for connections")
            connection.close()
            server_socket.close()


if __name__ == "__main__":
    SocketListeningImages(mode="aws").start()
