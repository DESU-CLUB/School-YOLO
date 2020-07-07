#! /usr/bin/env python
# -*- coding: utf-8 -*-

#Import dependencies
import os 
from timeit import time #To time how long it takes to process stuff
import warnings #To ignore benign warnings that are not fatal errors
import sys 
import cv2 #Image processing module
import numpy as np # Matrix processing module
from PIL import Image #Image processing module
from yolo import YOLO # Deep learning code with pretrained object detector
from deep_sort.detection import Detection # Dependencies for object detector to run
from deep_sort import preprocessing #Dependencies for object detector to run
from birdeyeclass import BirdEye #Bird's Eye View Processing Tools
from scipy.spatial.distance import pdist, squareform #To calculate distance
import matplotlib.pyplot as plt #Graphing tools
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas #To save images as minimap

warnings.filterwarnings('ignore') #Ignores warnings


def main(yolo): #Main function
    
   # Definition of the parameters
    nms_max_overlap = 0.95 #How much bounding boxes shld overlap before it is supressed

    writeVideo_flag = True
    
    #video_capture = cv2.VideoCapture('4.4.MOV') #Changed to caps --> Decomment this in production
    
    vid_path = input('Input video path here: ') #Video path
   
    video_capture = cv2.VideoCapture(vid_path)#Give the path to ur input video here
    ###End of testing code    

    calibrate = input('Do you wish to calibrate the input?(Y/N): ').upper() #This will ask the user if they want to calibrate the parameters for the BEV (Bird's Eye View) Transformation
    while calibrate not in ['Y','N']:
        print('Choose Y or N') #Catching errant user input
        calibrate = input('Do you wish to calibrate the input?(Y/N): ').upper() #Re-ask for input
    if calibrate == 'Y':
        CALIBRATE_FLAG = True #This means you will undergo calibration of the BEV, but there will be steps provided
    else:
        CALIBRATE_FLAG = False #No calibration performed

    DISTANCE_FLAG = False #Whether you want a minimap showing the locations and to show which students are flouting social distancing measures
    #Code is same as calibration, except this time its for checking whether user wants the additional output
    distance = input('Do you want to check the social distance (Y/N): ').upper()
    while distance not in ['Y','N']:
        print('Choose Y or N')
        distance = input('Do you want to check the social distance (Y/N):  ').upper()
    if distance == 'Y':
        DISTANCE_FLAG = True
    else:
        DISTANCE_FLAG = False
    
    
    
    if writeVideo_flag:
    # Define the codec and create VideoWriter object
        w = int(video_capture.get(3))
        h = int(video_capture.get(4))
        fourcc = cv2.VideoWriter_fourcc(*'MJPG') #Initialising the video writing tools
        if DISTANCE_FLAG:
            out = cv2.VideoWriter('output_videos/minimap.mov', fourcc, 20, (w*2, h))  #Initialises the video writing object, and sends the output to the path (This is the minimap writer)
            #debug_out =cv2.VideoWriter('output_videos/debug.mov', fourcc, 20, (w*2, h))
        re_out =  cv2.VideoWriter('output_videos/detections.mov', fourcc, 20, (w, h))#Initialises the video writing object, and sends the output to the path (This is the detections writer)
        
        frame_index = -1
    
    
    fps = 0.0 #fps counter
    count = 0
    refresh_num = 0
    while True:
        count +=1
        ret, frame = video_capture.read()  #ret is to check if video exists
        if ret != True:
            break
        oframe = np.copy(frame) #copies the frame of the video to a variable-> Why?: To use it later if social distancing is used
        t1 = time.time() #Checks current time
        if frame_index==-1:
            bird = BirdEye(w,h,frame,CALIBRATE_FLAG) #Allow for calibration if it is the first frame
        image = Image.fromarray(frame[...,::-1]) #bgr to rgb
        boxs, scores = yolo.detect_image(image) #Detect humans in the image
        
        
        detections = [Detection(bbox,score) for bbox,score in zip(boxs,scores)] #stores this in list, Detection is an object
        # print(detections[0][0])
        
        # Run non-maxima suppression. -->Read up on this
        boxes = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        indices = preprocessing.non_max_suppression(boxes, nms_max_overlap, scores)
        detections = [detections[i] for i in indices]
        
        bbox_lst = []#List to store social distanced students
        w_bbox_lst = []#List to store coordinates of very close students
        if DISTANCE_FLAG: #Only run this if you want to see who is socially distanced
            for det in detections:
                bbox =det.to_tlbr()   #top left bottom right format\
                #Calculate center coordinates
                x_c = (int(bbox[0])+int(bbox[2]))//2
                y_c = (int(bbox[1])+int(bbox[3]))//2 
                bbox =  np.append(bbox,x_c)
                bbox = np.append(bbox,y_c) #Appends them to coordinates detected
                bbox_lst.append(bbox) #Appends detected human coordinates to a list storing all detections
                warped_bbox =  bird.warp_points([[x_c,y_c]]) #Transforms everything into a semi-bird eye view to get a more accurate metric of distance
                w_bbox_lst.append(warped_bbox[0][0]) #Append these warped human centre coordinates to list
            if  len(w_bbox_lst)>0: #If there are ppl detected
                close_idxs = []
                ac_coords =  []
                dist = np.array(w_bbox_lst)
                pairdist=  squareform(pdist(dist,'euclidean')) #Find the distance between everyone detected
                #Eg, if I have person A, B C, the code will find distance of A from A, A from B, A from C, and find distance of B from A, B from B....... until distance of C from C
                
                for i in range(len(w_bbox_lst)): #So i run it through the list of warped coordinates
                    close_coords = []#List to store ppl too close to each other
                    for k in range(len(pairdist[i])): #I check distance between everyone from the ith person
                        if pairdist[i][k] < 30.5 and k not in close_idxs and pairdist[i][k] != 0:
                            #IF their distance is less than  30.5 (this is changeable to ur preference!) and the current kth person is still socially distanced with others, and the current person Im checking is not the ith person, then run the code
                            '''
                            #Why: 1) 30.5 is just an estimate of 1m, I use it to check if theyre socially     distanced
                                  2) Im comparing everyones' distances to the ith person. If they are already flouting the rules, there is no need to check if they are close to the current person,as they will be highlighted anyways #TODO: Validate this theory, and see if there is a need to change it
                                  3) I check if everyone is less than a certain value. But if I dont add this parameter, what happens is that even if the person is socially distanced, he will still be highlighted as this distance between him and himself is 0 (Furthermore, there is no way two people can have the same coordinates, so this can be used)
                            '''
                            close_coords.append(bbox_lst[k]) #If hes not socially distanced, add him/her to the naughty list!
                            close_idxs.append(k) #Append this to close_idxs, which is the indexes of the ppl too close to each other
                        if len(close_coords) != 0: #If there are ppl too close to the ith guy
                            close_coords.append(bbox_lst[i]) #He is then appended to the naughty list
                            close_idxs.append(i) #append him to close indexes
                            ac_coords.append(np.array(close_coords)) #Add the ith person and his fellow accomplices to a list storing all the people they are close with
                bbox_lst = np.array(bbox_lst) #Now turn it into a matrix!
                bbox_lst = np.delete(bbox_lst,close_idxs,axis = 0) #Delete the ppl too close to each other from Santa's good list
            if bbox_lst == []:#If good list is empty, to prevent naming errors or numpy slicing errors
                fig=  plt.figure()
                plt.tight_layout() #Presentation helper function
                plt.xlim(-80, 1950) #Sets limits for x and y-axis, preventing unstable output
                plt.ylim(-80, 1160)
            else:
                fig=  plt.figure()# Makes a plot
                plt.tight_layout()
                plt.xlim(-80, 1950) #Sets limits for x and y-axis, preventing unstable output
                plt.ylim(-80, 1160)
                plt.scatter(bbox_lst[:,0],bbox_lst[:,1])
                plt.axis('off')
                for q in range(len(bbox_lst)): #Draw rectangles on those not too close (coloured in green)
                    cv2.rectangle(frame,(int(bbox_lst[q][0]),int(bbox_lst[q][1])),\
                        (int(bbox_lst[q][2]),int(bbox_lst[q][3])),(0,255,0),3)
            if ac_coords != []: #If naughty list not empty
                for z in ac_coords:
                    if z.size>0:
                        plt.plot(z[:,0],z[:,1],'-o',color= 'orange') #Draw connections between which ppl are too close
                        plt.axis('off')
                    else:
                        continue
                for row in ac_coords:
                    middle_coords= []
                    for col in row:
                        cv2.rectangle(frame,(int(col[0]),int(col[1])),(int(col[2]),int(col[3])),(0,0,255),3)
                        middle_coords.append([int(col[4]),int(col[5])])
                    cv2.polylines(frame,np.int32([middle_coords]),False,(0,0,255),4)
            plt.show(block=False)
            plt.close()
            canvas = FigureCanvas(fig) #For turning minimap into np array 
            canvas.draw()
            mat=  np.array(canvas.renderer._renderer)
            mat = cv2.cvtColor(mat,cv2.COLOR_RGB2BGR)                
            mat = cv2.resize(mat, (w,h)) #Resize it to smth suitable for image
            mat = cv2.flip(mat,0)
            print(mat.shape)
            frame= cv2.resize (frame,(w,h)) #Resizes rectangle drawn video
        else:
            
            for det in detections:
                bbox = det.to_tlbr()     #top left bottom right format
                cv2.rectangle(frame,(int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])),(0,255,0), 2)
        # cv2.putText(frame, str(round(det.confidence,2)), (int(bbox[0]), int(bbox[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.75*h/1920, (0,255,0), 2)

        cv2.putText(frame, "number of people: " + str(refresh_num), (int(1350/1920*w),100),0, 5e-3 * 200, (0,255,0),2)
        #Put text showing number of ppl detected in canteen
        plt.show()
        if count %30 ==0:
            refresh_num = len(detections) #Refresh number of detections every half a second
        else:
            refresh_num = refresh_num
        #cv2_imshow(frame) Removed slow frame showing
        if DISTANCE_FLAG:
            output = np.zeros((h,  w*2, 3), dtype="uint8") #Meshes output of original frame and minimap together
            debug_output = np.zeros((h,  w*2, 3), dtype="uint8")
        if writeVideo_flag:
            
            # save a frame
            if DISTANCE_FLAG:
                output[0:h,0:w]= oframe
                output[0:h,w:w*2]= mat
                out.write(output)
                #debug_output[0:h,0:w]= frame
                #debug_output[0:h,w:w*2]= mat
                #debug_out.write(debug_output)
                
            re_out.write(frame)#Frame with detections

            frame_index = frame_index + 1
            #Doc string is for writing coords to txt file
        fps  = ( fps + (1./(time.time()-t1)) ) / 2 #Shows how slow it is,nearer to 0 means slower, 
        print("fps= %f"%(fps))
        

    video_capture.release()
    if writeVideo_flag:
        if DISTANCE_FLAG:
            out.release()#Release C++ pointers (OpenCV uses C++ inherently)
        re_out.release()
        #debug_out.release()
    cv2.destroyAllWindows()




if __name__ == '__main__':
    main(YOLO()) #Run code
