import cv2
import requests
import os
import time
import webbrowser


cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

def scan_qr():
    _, img = cap.read()
    data, bbox, _ = detector.detectAndDecode(img)
    #check if there is a QRCode in the image
    if data:
        id=data
        b=webbrowser.open(str(id))
        cap.release()
        print(data)
        return id

       
    if cv2.waitKey(1) == ord("q"):
        cv2.destroyAllWindows()
        return 0



def reward(id):
	id = str(id)
	requests.get(f"https://cookiespeanutbutter.herokuapp.com/add/{id}/5")
	return id
	
while True:
    id = scan_qr()
    reward(id)
    time.sleep(2)