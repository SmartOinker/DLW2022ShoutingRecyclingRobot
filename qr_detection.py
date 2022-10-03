import cv2
import requests
import os
import time
import webbrowser


cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()
bin_id = 1
def scan_qr():
    _, img = cap.read()
    try:
        data, bbox, _ = detector.detectAndDecode(img)
    except:
        print("no qr. continue")
        return 0
    #check if there is a QRCode in the image
    if data:
        print("scanned.")
        id=data
        cap.release()
        print(data)
        return data

       
    if cv2.waitKey(1) == ord("q"):
        cv2.destroyAllWindows()
        return 0



def reward(id):
    id = str(id)
    print(f"id: {id}")
    req = requests.get(f"https://cookiespeanutbutter.herokuapp.com/add/{id}/{bin_id}")
    print(req.text)
    return id
	
while True:
    id = scan_qr()
    reward(id)