# Quick Start

1. Download YOLOv3 or tiny_yolov3 weights from [here](https://drive.google.com/file/d/1uvXFacPnrSMw6ldWTyLLjGLETlEsUvcE/view?usp=sharing) (yolo.h5 model file with tf-1.4.0) , put it into model_data folder.

2. Run YOLO_DEEP_SORT with cmd :
   ```
   python3 demo.py / minimalist.py
   ```
# Output
There are 2 outputs, original video with bounding boxes and labels, and minimalist video with just the labels. <br>
![original](output-yolov3.gif) <br>
![minimalist](simplified.gif)




# Dependencies

  The code is compatible with Python 2.7 and 3. The following dependencies are needed to run the tracker:

    NumPy
    sklean
    OpenCV
    Pillow

  Additionally, feature generation requires TensorFlow-1.4.0.

# Acknowledgements
  Most of the code were pulled from QiDian's respository found [here](https://github.com/Qidian213/deep_sort_yolov3) <br>
  I only implemented the respository's code for the school setting and studied its effectiveness. <br>
  Some of the script was also edited such that it can be run on Google Colabotory. <br>


