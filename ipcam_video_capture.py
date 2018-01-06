# -*- coding: utf-8 -*-
""" IP Camera Video Capture """

import os
import sys
import time
import uuid
import base64
import pickle
import urllib.request
from multiprocessing import Pool

import boto3

# AWS Environment variables
AWS_KEY = os.getenv('AWS_KEY', 'default')
AWS_SECRET = os.getenv('AWS_SECRET', 'default')
AWS_REGION = os.getenv('AWS_REGION', 'eu-west-1')
KINESIS_STREAM_NAME = os.getenv('KINESIS_STREAM_NAME', 'default')

print(AWS_REGION)

#Frame capture parameters
DEFAULT_CAPTURE_RATE = 30

kinesis_client = boto3.client(
    'kinesis',
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
    region_name=AWS_REGION,
)

def send_jpg(frame_jpg, frame_count):
    """ Send frame to Kinesis stream """
    try:

        img_bytes = frame_jpg
        ticks = time.time()

        frame_package = {
            'CaptureTime': ticks,
            'FrameCount': frame_count,
            'ImageBytes': img_bytes
        }

        # Put encoded image in kinesis stream
        print("Sending image to Kinesis...")
        response = kinesis_client.put_record(
            StreamName=KINESIS_STREAM_NAME,
            Data=pickle.dumps(frame_package),
            PartitionKey=str(uuid.uuid4())
        )
        print(response)
    except Exception as e:
        print(e)


def main():
    """ main() """

    ip_cam_url = ''
    capture_rate = DEFAULT_CAPTURE_RATE
    argv_len = len(sys.argv)

    if argv_len > 1:
        ip_cam_url = sys.argv[1]
        if argv_len > 2 and sys.argv[2].isdigit():
            capture_rate = int(sys.argv[2])
    else:
        print("usage: ipcam_video_capture.py <ip-cam-url> [capture-rate]")
        return

    print("Capturing from '{}' at a rate of 1 every {} frames...".format(ip_cam_url, capture_rate))
    stream = urllib.request.urlopen(ip_cam_url)
    
    stream_bytes = bytes([])
    pool = Pool(processes=3)

    frame_count = 0
    while True:
        stream_bytes += stream.read(16384*2)
        end_marker = stream_bytes.rfind(b'\xff\xd9')
        start_marker = stream_bytes.rfind(b'\xff\xd8', 0, end_marker-1)

        if start_marker != -1 and end_marker != -1:
            print('Found JPEG markers. Start {}, End {}'.format(start_marker, end_marker))
            frame_jpg_bytes = stream_bytes[start_marker:end_marker+2]
            stream_bytes = stream_bytes[end_marker+2:]

            if frame_count % capture_rate == 0:
                #Send to Kinesis
                result = pool.apply_async(send_jpg, (bytearray(frame_jpg_bytes), frame_count,))
                print(result)

            frame_count += 1

if __name__ == '__main__':
    main()
