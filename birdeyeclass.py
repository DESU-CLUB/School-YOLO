import cv2
import matplotlib.pyplot as plt
import numpy as np
import time
class BirdEye:
    def __init__(self,w,h,frame,flag): #All of these parameters will be automatically inputted by the main program
        '''
        w: Width of image
        h: Height of image
        frame: First frame of the video
        flag: Calibration flag as defined in COMBINED_GUI.py
        '''
        self.w = w #Get width of frame
        self.h = h #Get height of frame
        self.rec_src =  np.float32([[0, self.h], [1810/1920*self.w, self.h], [0, 0],[self.w, 0]]) #This is the recommended target area to warp
        self.src =  np.float32([[0, self.h], [1810/1920*self.w, self.h], [0, 0],[self.w, 0]]) #This is the target area to warp
        self.rec_disp_src = np.float32([[0, 0],[0, self.h] ,[1810/1920*self.w, self.h],[self.w, 0]]) #Recommended coordinates to display
        self.disp_src = np.float32([[0, 0],[0, self.h] ,[1810/1920*self.w, self.h],[self.w, 0]]) #This is src shown in another format to facilitate displaying of warped points
        self.dst =  np.float32([[484/1920*self.w, self.h], [775/1920*self.w, self.h], [0, 0], [self.w, 0]])  #This is the destination points
        self.rec_dst =  np.float32([[484/1920*self.w, self.h], [775/1920*self.w, self.h], [0, 0], [self.w, 0]])  #This is the  recommended destination points to warp to for BEV (Bird's Eye View)--> Recommended, but you can tinker with it outside of this code
        #Please dont change any of the constants in here, it is meant to scale with different input dimensions
        self.flag = flag #Calibration flag from COMBINED_GUI.py
        self.frame = frame #The first frame of the video 
        if self.flag: #If user wants to calibrate, run function
            self.calibrate()
            self.flag = False
        
        
    def calibrate(self):
        print('Welcome to calibration system\n\n')
        while True: #Instructions will be given during usage
            self.src = np.copy(self.rec_src)#Prevents previous input from changing the recommended inputs and outputs
            self.dst = np.copy(self.rec_dst)
            self.disp_src = np.copy(self.rec_disp_src)
            print('Step 1: Choose four points from the original image\n')
            print('• Each coordinate of a point should be bracketed and seperated by commas')
            print('• Each point should be seperated by spaces')
            print('• Format eg. (0,1080) (1810,1080) (0,0) (1920,0)\n\n') 
            #Should give in this order (Top Left) (Top Right) (Bottom Left) (Bottom Right)
            print('Recommended points are {}'.format([[0, self.h], [1810/1920*self.w, self.h], [0, 0], [self.w, 0]]))
            copy = input('Do you wish to use recommended points?(Y/N)').upper()
            while copy not in ['Y','N']: #Only allows for Y,y,n,N as input
                print('Please use either Y or N.')
                copy = input('Do you wish to use recommended points?(Y/N)').upper()
            if copy == 'Y':
                pass
            else:
                error = 1
                while True:
                    try:
                        src = input('Enter input points: ') #Processes the user input to be used by function
                        coordarray =  src.split(' ') #Split the tuples into each pt
                        array = []
                        for elem in coordarray:
                            vals = elem.split(',') #Get the x and y coord in each tuple, append to array
                            val_x = int(vals[0][1::])
                            val_y = int(vals[1][0:-1])
                            array.append([val_x,val_y])
                        if len(array) != 4:
                            raise ValueError #Raises error if assertion check fails
                        pts = np.array(array, dtype = 'float32')
                        error = 0
                    except:
                        print('Input Error: Please retry again') 
                        error = 1
                   
                    if not(error):
                        break # Get out of loop is user input is sanitised
                self.src = pts #Assign new target region for BEV (Bird's Eye View)
                self.disp_src = np.int32([pts[2],pts[0],pts[1],pts[3]]) #This displays the BEV selected region
            
            print('Step 2: Generate coordinates of destination points to warp to\n') #Destination points to warp to
            print('• Each coordinate of a point should be bracketed and seperated by commas')
            print('• Each point should be seperated by spaces')
            print('• Format eg. (0,1080) (1810,1080) (0,0) (1920,0)\n\n')
            print('Recommended points are {}'.format([[484/1920*self.w, self.h], [775/1920*self.w, self.h], [0, 0], [self.w, 0]]))
            copy = input('Do you wish to use recommended points?(Y/N)').upper()
            while copy not in ['Y','N']:
                print('Please use either Y or N.')
                copy = input('Do you wish to use recommended points?(Y/N)').upper()
            if copy == 'Y':
                pass
            else:
                error = 1
                while True:
                    try:
                        dst = input('Enter destination points: ') #Same as Step 1, it sanitises the input
                        coordarray =  dst.split(' ')
                        array = []
                        for elem in coordarray:
                            vals = elem.split(',')
                            val_x = int(vals[0][1::])
                            val_y = int(vals[1][0:-1])
                            array.append([val_x,val_y])
                        if len(array) != 4:
                            raise ValueError #Raises error if assertion check fails
                        pts = np.array(array, dtype = 'float32')
                        error = 0
                    except:
                        print('Input Error:')
                        error = 1
                    
                    if not(error):
                        break
                self.dst = pts
                
            print('Step 3: Validate results') #Shows results
            img = self.bird_eye_warp(self.frame)
            imgrgb = cv2.resize(cv2.cvtColor(img,cv2.COLOR_BGR2RGB),(1000,1000)) 
            cv2.polylines(self.frame,np.int32([self.disp_src]),False,(255,0,0),2)
            framergb = cv2.resize(cv2.cvtColor(self.frame ,cv2.COLOR_BGR2RGB),(1000,1000))
            fig, ax = plt.subplots(1,2)
            ax[0].imshow(imgrgb) #Shows targrted region and shows BEV output
            ax[1].imshow(framergb)
            plt.show()
            end = input('Is input to your liking?(Y/N): ').upper()
            while end not in ['Y','N']:
                print('Please use either Y or N.')
                end = input('Is input to your liking?(Y/N): ').upper()
            if end == 'Y':
                plt.close('all')
                break

    def lazy_eval(self):
        #For fast recalibration (Debugging purposes)
        while True:
            a = int(input('Input point number 2 x coord: '))
            b = int(input('Input point number 3 x coord'))
            
            img = self.bird_eye_warp(self.frame)
            self.src =  np.float32([[0, self.h], [1810/1920*self.w, self.h],[0, 0], [self.w, 0]])
            self.dst =  np.float32([[a, self.h], [b, self.h], [0, 0], [self.w, 0]]) #Best:
            print(self.disp_src)
            imgrgb = cv2.resize(cv2.cvtColor(img,cv2.COLOR_BGR2RGB),(1000,1000))
            cv2.polylines(self.frame,np.int32([self.disp_src]),False,(255,0,0),4)
            framergb = cv2.resize(cv2.cvtColor(self.frame ,cv2.COLOR_BGR2RGB),(1000,1000))
            fig, ax = plt.subplots(1,2)
            ax[0].imshow(imgrgb)
            ax[1].imshow(framergb)
            plt.show()
            end = input('Is input to your liking?(Y/N): ').upper()
            while end not in ['Y','N']:
                print('Please use either Y or N.')
                end = input('Is input to your liking?(Y/N): ').upper()
            if end == 'Y':
                plt.close('all')
                break

    def bird_eye_warp(self,frame): #Helper function for warping matrices
        IMAGE_W = self.w
        IMAGE_H = self.h
        src = self.src
        dst = self.dst
        self.M = cv2.getPerspectiveTransform(src, dst) # The transformation matrix
        Minv = cv2.getPerspectiveTransform(dst, src) # Inverse transformation

        img = frame
        warped_img = cv2.warpPerspective(img, self.M, (IMAGE_W, IMAGE_H)) # Image warping
        return warped_img
    
    def warp_points(self,points):
        self.M = cv2.getPerspectiveTransform(self.src, self.dst) # The transformation matrix
        return cv2.perspectiveTransform(np.array([points],dtype = 'float32'), self.M)

    
    def request_matrix(self): #For debugging purposes, if you want to output a matrix
        return self.M



        



        