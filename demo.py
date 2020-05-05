#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from timeit import time
import warnings
import sys
from google.colab.patches import cv2_imshow
import cv2
import numpy as np
from PIL import Image
from yolo import YOLO
from deep_sort.detection import Detection
from deep_sort import preprocessing
warnings.filterwarnings('ignore')

def main(yolo): #Main function

   # Definition of the parameters
    nms_max_overlap = 0.95

    writeVideo_flag = True
    
    video_capture = cv2.VideoCapture('4.4.MOV') #Changed to caps

    if writeVideo_flag:
    # Define the codec and create VideoWriter object
        w = int(video_capture.get(3))
        h = int(video_capture.get(4))
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter('output.mov', fourcc, 20, (w, h))
        list_file = open('detection.txt', 'w')
        frame_index = -1 
        
    fps = 0.0
    count = 0
    refresh_num = 0
    while True:
        count +=1
        ret, frame = video_capture.read()  #ret is to check if video exists
        if ret != True:
            break
        t1 = time.time()
        
        image = Image.fromarray(frame[...,::-1]) #bgr to rgb
        boxs, scores = yolo.detect_image(image)
        
        
        detections = [Detection(bbox,score) for bbox,score in zip(boxs,scores)] #stores this in list, Detection is an object
        # print(detections[0][0])
        
        # Run non-maxima suppression. -->Read up on this
        boxes = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        indices = preprocessing.non_max_suppression(boxes, nms_max_overlap, scores)
        detections = [detections[i] for i in indices]
        
        for det in detections:
            bbox = det.to_tlbr()     #top left bottom right format

            cv2.rectangle(frame,(int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])),(0,255,0), 2)
            # cv2.putText(frame, str(round(det.confidence,2)), (int(bbox[0]), int(bbox[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,255,0), 2)

        cv2.putText(frame, "number of people: " + str(refresh_num), (1050,100),0, 5e-3 * 200, (0,255,0),2)
        
        if count %30 ==0:
            refresh_num = len(detections)
        else:
            refresh_num = refresh_num
        #cv2_imshow(frame) Removed slow frame showing
        
        if writeVideo_flag:
            # save a frame
            out.write(frame)
            frame_index = frame_index + 1
            #This code here is for writing coords to txt file
            list_file.write(str(frame_index)+' ')
            if len(boxs) != 0:
                for i in range(0,len(boxs)):
                    list_file.write(str(boxs[i][0]) + ' '+str(boxs[i][1]) + ' '+str(boxs[i][2]) + ' '+str(boxs[i][3]) + ' ')
            list_file.write('\n')
            
        fps  = ( fps + (1./(time.time()-t1)) ) / 2
        print("fps= %f"%(fps))
        
        # Press Q to stop!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    if writeVideo_flag:
        out.release()
        list_file.close() #File for txt
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(YOLO())
