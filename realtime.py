import cv2
from darkflow.net.build import TFNet
import numpy as np
import time
import os

os.environ['KMP_DUPLICATE_LIB_OK']='True'
option = {
    'model': 'cfg/yolo.cfg',
    'load': 'bin/yolov2.weights',
    'threshold': 0.1,
    'gpu': 1.0
}

tfnet = TFNet(option)
colors = [tuple(255 * np.random.rand(3)) for i in range(30)]

capture = cv2.VideoCapture(0)
#capture = cv2.VideoCapture('videotitle.mp4') <-- insert video file and
#comment out VideoCapture(0) to switch to detection on existing video 

capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
#Traffic_conf and car_conf count how many frames the car/traffic light have been
#detected. This is to gurantee that the network is detecting one of these items
#without activating on seeing a signle, possibly faulty, frame of detection
traffic_conf = 0
car_conf = 0
frames = 0
seconds = 0
cseconds = 0
#This gets the location of the object on screen
def getLoc(centx, centy, leftb, rightb, topb, bottb, obj):
    loc =obj
    print(centx)
    print(rightb)
    if(centx >=rightb):
        loc += " right"
    if((centx >leftb) & (centx<rightb)):
        loc += " front"
    if(centx<=leftb):
        loc += " left"
    if(centy <bottb) & (centy>topb):
        loc += " distant"
    if(centy >=bottb):
        loc += " near"
    if(centy <=topb):
        loc += "near"
    print(loc)
    return loc



while capture.isOpened():
    stime = time.time();
    ret, frame = capture.read()
    results = tfnet.return_predict(frame)
    #The program ran at 15 frames per second on my computer. This is a terrible
    #solution for counting time, but I couldn't figure out another way to do this
    frames +=1
    if frames>15:
        frames = 0
        seconds +=1
        cseconds +=1
        print(seconds)
        print(cseconds)
    
    if ret:
        tempconf = 0
        carconf = 0
        centerx = 0
        centery = 0

        #The following lines segment the image into a matrix to be used for
        #describing the object location
        leftboundline =int(frame.shape[1]/3)
        rightboundline = int(2*frame.shape[1]/3)
        height = int(frame.shape[0])

        cv2.line(frame, (leftboundline,0),(leftboundline,height), (255,0,0), 5)
        cv2.line(frame, (rightboundline,0),(rightboundline,height), (255,0,0), 5)

        bottomline = int(frame.shape[0]/2)
        topline = int(frame.shape[0]/4)
        width = int(frame.shape[1])
        carline = 2*int(frame.shape[0]/3)

        cv2.line(frame, (0,bottomline),(width,bottomline), (0,0,255), 5)
        cv2.line(frame, (0,topline),(width,topline), (0,0,255), 5)

        cv2.line(frame, (0,carline),(width,carline), (0,255,0), 5)


        for color, result in zip(colors, results):
            
            tl = (result['topleft']['x'], result['topleft']['y'])

            br = (result['bottomright']['x'], result['bottomright']['y'])
            label = result['label']
            if (label == 'traffic light') | (label == 'stop sign') | (label == 'car'):
                if label != 'car':
                    tempconf=1
                
                centerx = int((result['topleft']['x']+result['bottomright']['x'])/2)
                centery = int((result['topleft']['y']+result['bottomright']['y'])/2)

                cv2.circle(frame, (centerx, centery), 10, (0,255,0), -1)
             
                confidence = result['confidence']
                if (label == 'car') & (confidence >= 0.3):
                    carconf = 1
                text = '{}: {:.0f}%'.format(label, confidence * 100)
                frame = cv2.rectangle(frame, tl, br, color, 7)
                frame = cv2.putText(frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
        cv2.imshow('frame', frame)
        print('FPS {:.1f}'.format(1/(time.time() - stime)))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #Update the confidence variables to see how many frames the object was present for
        if tempconf >=1:
            traffic_conf+=1
        if carconf >=1:
            car_conf+=1
             
        if traffic_conf >=40:
            print("crosswalk detected")
            phrase =  getLoc(centerx, centery, leftboundline, rightboundline, topline, bottomline, "crosswalk")
            if seconds > 10:
                #This uses the system's built in "voice program". It kind of works, but
                #has the unintented effect of pausing the video while speaking.
                #Also, I think that this prevents it from running on systems other than Windows
                os.system("mshta vbscript:Execute(\"CreateObject(\"\"SAPI.SpVoice\"\").Speak(\"\""+phrase +"\"\")(window.close)\")")
                seconds = 0
            traffic_conf=0
        
        if car_conf >=10:
            print("car detected")
            phrase =  getLoc(centerx, centery, leftboundline, rightboundline, 0, carline, "car")
            if phrase.find("near") > -1:
                if cseconds >= 3:
                    os.system("mshta vbscript:Execute(\"CreateObject(\"\"SAPI.SpVoice\"\").Speak(\"\""+phrase +"\"\")(window.close)\")")
                    cseconds = 0
            car_conf=0
    else:
        capture.release()
        cv2.destroyAllWindows()
        break
