# Quick Start

1. Download YOLOv3 or tiny_yolov3 weights from [here](https://drive.google.com/file/d/1uvXFacPnrSMw6ldWTyLLjGLETlEsUvcE/view?usp=sharing) (yolo.h5 model file with tf-1.4.0) , put it into model_data folder.

2. Run School-YOLO with cmd :
   ```
   python3 demo.py
   python3 minimalist.py
   ```
# Output
There are 2 outputs, original video with bounding boxes and labels, and minimalist video with just the labels. <br>
![original](output-yolov3.gif)
![minimalist](simplified.gif)


3. Run School-YOLO on [Google Colab](https://colab.research.google.com/drive/1239pS4IhzAmHlQz2gW7yc7DgB3cTUeNB?authuser=2#scrollTo=6wk1pUSMluFc) <br>
```
!git clone https://github.com/DESU-CLUB/School-YOLO/tree/deepsort-tracker
%cd <path to video> #replace sample_input.mp4
%tensorflow_version 1.x

!python3 demo.py
!python3 minimalist.py
```



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
  
# License
## MIT LICENSE
Copyright 2020 HCIRS ML Division

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.




