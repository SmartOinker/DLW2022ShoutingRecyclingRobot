# DLW2022ShoutingRecyclingRobot
Here is Trashify, the smart recycling bin that will help Singapore turn into a real Smart Nation. Trashify does this by modifying the current recycling bins in Singapore, such that materials which are non-recyclable won't contaminate the recyclables.
The machine learning model used is YOLOv5x, and it was trained on a [public dataset](https://universe.roboflow.com/squid/packaging/dataset/3). This was complemented with a lid that will cover the recycling bin unless a recyclable was shown to the camera. 
Furthermore, a point system was built, where users who recycled could scan their QR code for points. This system made use of Google Authentication to verify users and a Flask+SQL backend to tabulate the points.
