import cv2
camera_port = 0
ramp_frames = 30
import time
import serial
import requests

bin_id = 1

import fastbook
fastbook.setup_book()
from fastbook import *
from fastai.vision.widgets import *
learn_inf = load_learner("/Users/yuyouyou/Downloads/export.pkl")

def opendusbin():
    arduino.write(b'A')

print("set up done")


while True:
    print("starting")
    camera = cv2.VideoCapture(camera_port)
    # camera = cv2.VideoCapture(camera_port, cv2.CAP_DSHOW)
    def get_image():
        retval, im = camera.read()
        return im


    print("starting capture...")
    for i in range(3, 0, -1):
        print(i)
        time.sleep(1)

    for i in range(ramp_frames):
        temp = get_image()
    print("capturing image...")

    camera_capture = get_image()
    file = "testing.png"
    cv2.imwrite(file, camera_capture)

    del camera
    print("picture taken. ")



    dest = "/Users/yuyouyou/Desktop/testing.png"
    ims = Image.open(dest)
    # print(ims.to_thumb(128, 128))
    prediction= learn_inf.predict(dest)
    print(prediction)
    if prediction[0] in ["brown-glass", "cardboard", "green-glass", "metal", "paper", "plastic", "white-glass"]:
        try:
            arduino = serial.Serial(port='/dev/tty.usbserial-1410', baudrate=9600, timeout=.1)
            opendusbin()
            requests.get(f"https://cookiespeanutbutter.herokuapp.com/bin/{bin_id}")
        except:
            print("no arduino connected")

    else:
        print("THIS IS NOT RECYCABLE")


    time.sleep(2)
