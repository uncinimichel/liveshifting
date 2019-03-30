import io
import socket
import struct
import time

from PIL import Image


def main():
    # Connect a client socket to my_server:8000 (change my_server to the
    # hostname of your server)
    client_socket = socket.socket()
    client_socket.connect(('0.0.0.0', 8000))

    # Make a file-like object out of the connection
    connection = client_socket.makefile('wb')
    try:
        i = 0
        while True:
            i = i + 1
            stream = io.BytesIO()
            img = Image.open('./pasqua1.jpeg', mode='r')
            img.save(stream, format='PNG')

            # Write the length of the capture to the stream and flush to
            # ensure it actually gets sent
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            # Rewind the stream and send the image data over the wire
            stream.seek(0)
            connection.write(stream.read())
            # connection.flush()
            # Reset the stream for the next capture
            stream.seek(0)
            stream.truncate()
            time.sleep(1)
            if i == 5:
                break

    finally:
        # Write a length of zero to the stream to signal we're done
        connection.write(struct.pack('<L', 0))
        connection.close()
        client_socket.close()


if __name__ == "__main__":
    main()
