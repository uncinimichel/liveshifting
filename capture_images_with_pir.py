import io
import socket
import struct
import time

import picamera
from gpiozero import MotionSensor

recording_mode = {'recording': 1, 'pause_recording': 2, 'exit_recording': 0}


class SplitFrames(object):

    def __init__(self, connection):
        self.connection = connection
        self.stream = io.BytesIO()
        self.frame_num = 0

    def write(self, buf):
        self.connection.write(struct.pack('<b', recording_mode["recording"]))
        self.connection.flush()

        if buf.startswith(b'\xff\xd8'):
            # Start of new frame; send the old one's length
            # then the data
            size = self.stream.tell()
            if size > 0:
                self.connection.write(struct.pack('<L', size))
                # Send the size of the new image
                self.connection.flush()
                self.stream.seek(0)
                self.connection.write(self.stream.read(size))
                self.frame_num += 1
                self.stream.seek(0)
                self.stream.truncate()

        self.stream.write(buf)

    def flush(self):
        self.connection.write(struct.pack('<b', recording_mode["pause_recording"]))
        self.connection.flush()


def main():
    # Set pir
    pir = MotionSensor(4)

    client_socket = socket.socket()
    client_socket.connect(('0.0.0.0', 8000))

    # Make a file-like object out of the connection
    connection = client_socket.makefile('wb')
    output = SplitFrames(connection)
    try:
        while True:
            is_motion = pir.motion_detected
            # Tell someone that I detected motion
            if is_motion:
                start = time.time()
                with picamera.PiCamera(resolution='VGA', framerate=30) as camera:
                    camera.rotation = 180
                    time.sleep(2)
                    camera.start_recording(output, format='mjpeg')
                    # Keep recording if motion is detected
                    while True:
                        camera.wait_recording(1)
                        is_still_in_motion = pir.motion_detected
                        if not is_still_in_motion:
                            break
                        else:
                            continue
                    camera.stop_recording()
                    finish = time.time()
                    print('Captured %d frames at %.2ffps for %d milliseconds' % (
                        output.frame_num,
                        output.frame_num / (finish - start),
                        (finish - start)))
            else:
                time.sleep(2)
                # Tell someone that there is no motion

    finally:
        # Write the terminating exit_recording
        connection.write(struct.pack('<b', recording_mode['exit_recording']))
        connection.close()
        client_socket.close()


if __name__ == "__main__":
    main()
