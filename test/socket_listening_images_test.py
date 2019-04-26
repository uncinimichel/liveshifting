import io
import socket
import struct
import threading
import time
import unittest
from unittest.mock import MagicMock

from PIL import Image

from socket_listening_images import SocketListeningImages


class TestSocketListeningMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.socket_server = SocketListeningImages()
        x = threading.Thread(target=cls.socket_server.start)
        x.start()
        # Give time to the server to start
        time.sleep(2)
        cls.client_socket = socket.socket()
        cls.client_socket.connect(('0.0.0.0', 8000))
        cls.connection = cls.client_socket.makefile('wb')

    @classmethod
    def tearDownClass(cls):
        recording_mode = 0
        cls.connection.write(struct.pack('<b', recording_mode))
        cls.connection.flush()
        cls.connection.close()
        cls.client_socket.close()

    def setUp(self):
        self.socket_server.save = MagicMock(return_value=None)

    def send_is_recording_with_stream(self, stream):
        # Write the length of the capture to the stream and flush to
        # ensure it actually gets sent
        self.connection.write(struct.pack('<b', 1))
        self.connection.flush()

        self.connection.write(struct.pack('<L', stream.tell()))
        self.connection.flush()
        # Rewind the stream and send the image data over the wire
        stream.seek(0)
        self.connection.write(stream.read())
        # self.connection.flush()
        # Reset the stream for the next capture
        stream.seek(0)
        stream.truncate()

    def test_equal_images_are_not_stored(self):
        i = 0
        while i < 10:
            i = i + 1
            stream = io.BytesIO()
            img = Image.open('./test_images/with_person.jpeg', mode='r')
            img.save(stream, format='PNG')
            self.send_is_recording_with_stream(stream)

        assert not self.socket_server.save.called

    def test_equal_images_are_not_stored_but_last_one(self):
        i = 0
        while i < 10:
            i = i + 1
            stream = io.BytesIO()
            img = Image.open('./test_images/with_person.jpeg', mode='r')
            img.save(stream, format='PNG')
            self.send_is_recording_with_stream(stream)

        assert not self.socket_server.save.called

        stream = io.BytesIO()
        img = Image.open('./test_images/no_person.jpeg', mode='r')
        img.save(stream, format='PNG')
        self.send_is_recording_with_stream(stream)

        time.sleep(1)
        assert self.socket_server.save.called

    def test_two_different_images_are_stored(self):
        images = ['./test_images/with_person.jpeg', './test_images/no_person.jpeg']
        for img in images:
            stream = io.BytesIO()
            img = Image.open(img, mode='r')
            img.save(stream, format='PNG')
            self.send_is_recording_with_stream(stream)

        # Give some time for the socket to get that
        time.sleep(1)
        assert self.socket_server.save.called

    def test_images_are_not_equal_steam_paused_then_images_are_equal(self):
        images = ['./test_images/with_person.jpeg', './test_images/with_person.jpeg']
        for img in images:
            stream = io.BytesIO()
            img = Image.open(img, mode='r')
            img.save(stream, format='PNG')
            self.send_is_recording_with_stream(stream)

        assert not self.socket_server.save.called
        self.connection.write(struct.pack('<b', 2))
        self.connection.flush()

        images = ['./test_images/with_person.jpeg', './test_images/no_person.jpeg']
        for img in images:
            stream = io.BytesIO()
            img = Image.open(img, mode='r')
            img.save(stream, format='PNG')
            self.send_is_recording_with_stream(stream)
        # Give some time for the socket to get that
        time.sleep(1)
        assert self.socket_server.save.called


if __name__ == '__main__':
    unittest.main()
