import io
import socket
import struct
import time

import picamera
from gpiozero import MotionSensor


def main():
    # Set pir
    pir = MotionSensor(4)

    client_socket = socket.socket()
    client_socket.connect(('0.0.0.0', 8000))

    # Make a file-like object out of the connection
    connection = client_socket.makefile('wb')
    try:
        while True:
            is_motion = pir.motion_detected

            if is_motion:
                with picamera.PiCamera() as camera:
                    camera.resolution = (640, 480)
                    # Start a preview and let the camera warm up for 2 seconds
                    camera.start_preview()
                    time.sleep(2)
                    stream = io.BytesIO()
                    for _ in camera.capture_continuous(stream, 'jpeg'):
                        # Write the length of the capture to the stream and flush to
                        # ensure it actually gets sent
                        connection.write(struct.pack('<L', stream.tell()))
                        connection.flush()
                        # Rewind the stream and send the image data over the wire
                        stream.seek(0)
                        connection.write(stream.read())
                        is_still_in_motion = pir.motion_detected
                        if not is_still_in_motion:
                            break
                        # Reset the stream for the next capture
                        stream.seek(0)
                        stream.truncate()
            else:
                time.sleep(2)

    finally:
        # Write a length of zero to the stream to signal we're done
        connection.write(struct.pack('<L', 0))
        connection.close()
        client_socket.close()


if __name__ == "__main__":
    main()
