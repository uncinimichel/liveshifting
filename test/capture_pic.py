import io
import socket
import struct
import time

import picamera


def main():
    client_socket = socket.socket()
    client_socket.connect(('0.0.0.0', 8000))

    # Make a file-like object out of the connection
    connection = client_socket.makefile('wb')
    # Create an in-memory stream
    stream = io.BytesIO()
    try:
        with picamera.PiCamera() as camera:

            camera.resolution = (640, 480)
            camera.framerate = 30
            time.sleep(2)
            start = time.time()
            count = 0
            stream = io.BytesIO()
            # Use the video-port for captures...
            for _ in camera.capture_continuous(stream, 'jpeg',
                                               use_video_port=True):

                connection.write(struct.pack('<L', stream.tell()))
                connection.flush()
                stream.seek(0)
                connection.write(stream.read())
                count += 1
                if time.time() - start > 30:
                    break
                stream.seek(0)
                stream.truncate()

    finally:
        # Write the terminating 0-length to the connection to let the
        # server know we're done
        connection.write(struct.pack('<L', 0))
        connection.close()
        client_socket.close()
        finish = time.time()
    print('Sent %d images in %d seconds at %.2ffps' % (
        count, finish - start, count / (finish - start)))


if __name__ == "__main__":
    main()
